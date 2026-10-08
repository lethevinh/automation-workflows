#!/usr/bin/env python3
"""Generate a Mermaid node graph from an n8n workflow.json and inject it into
the workflow's README between <!-- mermaid:start --> / <!-- mermaid:end -->
markers. Styled with the repo's "Paper" theme — see docs/visual-style.md.

Usage:
    python3 scripts/render-mermaid.py <workflow-dir> [<workflow-dir> ...]
"""

import json
import re
import sys
from pathlib import Path

START = "<!-- mermaid:start -->"
END = "<!-- mermaid:end -->"

THEME = (
    '%%{init: {"theme":"base","themeVariables":{'
    '"fontFamily":"ui-monospace, SFMono-Regular, Menlo, monospace",'
    '"fontSize":"13px","background":"#FFFFFF","primaryColor":"#FFFFFF",'
    '"primaryBorderColor":"#CBD5E1","primaryTextColor":"#0F172A",'
    '"lineColor":"#94A3B8","tertiaryColor":"#FFFFFF"}}}%%'
)

CLASSES = {
    "trigger": "fill:#EFF6FF,stroke:#3B82F6,color:#0F172A",
    "logic": "fill:#ECFDF5,stroke:#10B981,color:#0F172A",
    "decide": "fill:#FFFBEB,stroke:#F59E0B,color:#0F172A",
    "store": "fill:#F5F3FF,stroke:#8B5CF6,color:#0F172A",
    "ai": "fill:#FDF2F8,stroke:#EC4899,color:#0F172A",
    "external": "fill:#F8FAFC,stroke:#64748B,color:#0F172A",
    "gate": "fill:#FEF2F2,stroke:#EF4444,color:#0F172A",
    "disabled": "opacity:.55,stroke-dasharray:4 3",
}

# Node shape per class — system-design vocabulary (docs/visual-style.md).
SHAPES = {
    "trigger": ('(["', '"])'),   # stadium — entry point
    "decide": ('{"', '"}'),      # rhombus — branch
    "store": ('[("', '")]'),     # cylinder — persistence
}


def classify(node_type: str, name: str = "") -> str:
    t = node_type.lower()
    if "trigger" in t or "webhook" in t or "chatform" in t:
        return "trigger"
    if t.endswith(".if") or "switch" in t:
        return "decide"
    if any(k in t for k in ("sheets", "postgres", "airtable", "notion",
                            "datastore", "mongo", "mysql", "redis")):
        return "store"
    if "approv" in name.lower():
        return "gate"
    if "openai" in t or "langchain" in t or "anthropic" in t:
        return "ai"
    if any(k in t for k in ("gmail", "telegram", "slack", "httprequest",
                            "discord", "emailsend", "twilio")):
        return "external"
    return "logic"


def node_label(name: str) -> str:
    """Make a node name safe inside a quoted Mermaid label."""
    return re.sub(r"\s+", " ", name).replace('"', "'").strip()


def branch_label(src_type: str, out_idx: int, n_slots: int) -> str | None:
    """Label an outgoing edge when the source node has multiple outputs."""
    if n_slots < 2:
        return None
    if src_type.endswith(".if"):
        return "true" if out_idx == 0 else "false"
    if "switch" in src_type.lower():
        return str(out_idx)
    return f"out {out_idx}"


def mermaid_block(workflow: dict) -> str:
    nodes = [
        n for n in workflow.get("nodes", [])
        if n.get("type") != "n8n-nodes-base.stickyNote"
    ]
    ids = {n["name"]: f"n{i}" for i, n in enumerate(nodes)}
    kinds = {n["name"]: classify(n.get("type", ""), n["name"]) for n in nodes}
    conns = workflow.get("connections", {})

    lines = [THEME, "flowchart TB"]
    for n in nodes:
        nid, kind = ids[n["name"]], kinds[n["name"]]
        label = node_label(n["name"])
        l, r = SHAPES.get(kind, ('["', '"]'))
        lines.append(f"    {nid}{l}{label}{r}")

    for src, conn in conns.items():
        if src not in ids:
            continue
        for conn_type, slots in conn.items():
            arrow = "-->" if conn_type == "main" else "-.->"
            for out_idx, targets in enumerate(slots or []):
                for t in targets or []:
                    dst = t.get("node")
                    if dst not in ids:
                        continue
                    if conn_type == "main":
                        lbl = branch_label(
                            next(n["type"] for n in nodes if n["name"] == src),
                            out_idx, len(slots))
                    else:
                        lbl = conn_type.replace("ai_", "")
                    edge = f"    {ids[src]} {arrow}"
                    if lbl:
                        edge += f'|"{lbl}"|'
                    lines.append(f"{edge} {ids[dst]}")

    for cls, style in CLASSES.items():
        lines.append(f"    classDef {cls} {style}")
    for cls in ("trigger", "logic", "decide", "store", "ai", "external",
                "gate"):
        members = [ids[n["name"]] for n in nodes
                   if kinds[n["name"]] == cls and not n.get("disabled")]
        if members:
            lines.append(f"    class {','.join(members)} {cls}")
    disabled = [ids[n["name"]] for n in nodes if n.get("disabled")]
    if disabled:
        lines.append(f"    class {','.join(disabled)} disabled")
    return "```mermaid\n" + "\n".join(lines) + "\n```"


def inject(readme: Path, block: str) -> None:
    text = readme.read_text()
    if START in text and END in text:
        pre = text[: text.index(START)]
        post = text[text.index(END) + len(END):]
        text = pre + START + "\n" + block + "\n" + END + post
    else:
        raise SystemExit(f"{readme}: missing {START} / {END} markers")
    readme.write_text(text)


def main() -> None:
    for arg in sys.argv[1:]:
        wf_dir = Path(arg)
        workflow = json.loads((wf_dir / "workflow.json").read_text())
        block = mermaid_block(workflow)
        inject(wf_dir / "README.md", block)
        print(f"{wf_dir}: injected {block.count('-->') + block.count('-.->')} edges")


if __name__ == "__main__":
    main()
