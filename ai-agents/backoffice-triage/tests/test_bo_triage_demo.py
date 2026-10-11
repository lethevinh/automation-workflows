"""AC (d): prompts and config are versioned, and the mock run is green in CI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PACK_DIR = Path(__file__).resolve().parents[1]


def test_prompts_and_config_are_versioned() -> None:
    # prompts carry explicit version suffixes
    prompt_files = sorted(PACK_DIR.glob("prompts/*.txt"))
    assert len(prompt_files) == 3
    for prompt in prompt_files:
        assert ".v1." in prompt.name, prompt.name

    system = (PACK_DIR / "prompts" / "triage.system.v1.txt").read_text(
        encoding="utf-8"
    )
    assert "Never send anything" in system
    classify_prompt = (PACK_DIR / "prompts" / "classify.task.v1.txt").read_text(
        encoding="utf-8"
    )
    assert '"queue"' in classify_prompt  # structured JSON contract

    # config files carry a version integer the loader refuses to drift past
    config = json.loads((PACK_DIR / "config" / "config.json").read_text(
        encoding="utf-8"
    ))
    router = json.loads((PACK_DIR / "config" / "router.json").read_text(
        encoding="utf-8"
    ))
    assert config["version"] == 1
    assert router["version"] == 1
    assert config["send_policy"]["require_approval"] is True


def _run_demo(out_dir: Path) -> subprocess.CompletedProcess[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [sys.executable, str(PACK_DIR / "bo_triage_cli.py"), "--mock-llm",
         "--out", str(out_dir)],
        cwd=out_dir,
        capture_output=True,
        text=True,
        check=False,
    )


def test_mock_run_is_green_and_self_verifying(tmp_path: Path) -> None:
    out = tmp_path / "mock-out"
    proc = _run_demo(out)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "RESULT: PASS" in proc.stdout
    for name in ("routes.csv", "audit.csv", "sent.csv", "blocked.csv"):
        assert (out / name).is_file()


def test_mock_run_is_idempotent(tmp_path: Path) -> None:
    out = tmp_path / "mock-out"
    first = _run_demo(out)
    assert first.returncode == 0
    before = {name: (out / name).read_bytes() for name in
              ("routes.csv", "audit.csv", "sent.csv", "blocked.csv")}

    second = _run_demo(out)
    assert second.returncode == 0
    after = {name: (out / name).read_bytes() for name in
             ("routes.csv", "audit.csv", "sent.csv", "blocked.csv")}
    assert after == before


def test_route_mode_runs_a_real_inbox_without_self_verify(tmp_path: Path) -> None:
    """The README documents ``bo-triage --route``; prove the command exists and
    is safe by default: with no approvals file, nothing is sent."""

    out = tmp_path / "out"
    proc = subprocess.run(
        [sys.executable, str(PACK_DIR / "bo_triage_cli.py"), "--route",
         "--inbox", str(PACK_DIR / "fixtures" / "inbox"),
         "--approvals", str(tmp_path / "no-approvals.csv"),
         "--out", str(out)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "route mode: outputs written" in proc.stdout
    assert "sent (0)" in proc.stdout
    assert (out / "sent.csv").is_file()
    assert (out / "blocked.csv").is_file()