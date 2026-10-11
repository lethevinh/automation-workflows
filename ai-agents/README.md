# AI Agents

Agent setups that plug into real business workflows — classification, drafting,
enrichment, orchestration. Every pack ships typed, pytest-covered, versioned
prompts/config, and a credential-free `--mock-llm` lane that runs offline on
bundled fixtures:

```
<agent-slug>/
├── README.md        # problem -> solution -> mock lane -> verification -> honest limit
├── pyproject.toml   # installable: pip install -e . (console script)
├── bo_triage_*.py   # flat typed modules, stdlib only
├── prompts/         # versioned system/task prompts (v1, v2, ...)
├── config/          # versioned model/tool/routing configuration
├── fixtures/        # bundled demo messages + the expected output the demo asserts
├── tests/           # pytest
└── .env.example     # live-lane credential placeholders (never used by the mock lane)
```

The agent core is deterministic; the LLM sits at the edges (low-confidence
classification, draft phrasing) and is the documented owner-side swap-in. The
mock lane proves the routing, the approval gate and the audit trail with no key
and no network.

## Index

| Agent | Use case | Offline check | Live demo |
|---|---|---|---|
| [backoffice-triage](backoffice-triage/) | Route inbound email/form/message to a queue, draft the action, gate every send behind a human approval row, audit one row per route | `bo-triage --mock-llm` (10 routed, 3 sent, 7 blocked, 10 audit rows) · `pytest` 23 passed | LLM key + inbox/ticket system, owner-supplied |
