# Zapier Automations

Zapier has no clean JSON export, so each folder ships a validated blueprint
plus the credential-free way to prove its deterministic lane runs as declared:

```
<zap-slug>/
├── spec.json         # trigger, steps (each names its app + idempotency), failure branch, test cases, scoring
├── schema.json       # JSON Schema for spec.json
├── validate-spec.py  # schema guard + the every-step-names-its-app rule
├── replay.py         # offline replay of the deterministic lane, no Zapier account
├── fixtures/         # the bundled fixture the replay asserts against
├── README.md         # problem -> solution -> replay -> verification -> honest limit
└── assets/           # test-mode walkthrough; per-step screenshots are owner-supplied
```

The `spec.json` blueprint is the source of truth; `replay.py` reads the scoring
rules and bands straight out of it, so a blueprint that stops matching its
fixture breaks the check. Zapier has no credential-free one-click demo — the
offline replay is the substitute, and each README states that limit.

## Index

| Zap | Use case | Offline check | Live demo |
|---|---|---|---|
| [lead-router](lead-router/) | Score, dedupe and route form/email leads into Close | `validate-spec.py` + `replay.py` (8 leads, exactly 1 digest) | none — Zapier has no credential-free click-to-run |
