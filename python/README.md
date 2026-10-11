# Python Automation Scripts

Standalone, dependency-free Python CLIs — the pieces that sit next to a
workflow engine when a native node is not enough. Every pack ships typed,
pytest-covered, and with a credential-free demo lane:

```
<slug>/
├── README.md           # problem -> solution -> demo -> verification -> honest limit
├── pyproject.toml      # installable: pip install -e . (console script)
├── invoice_ledger_*.py # flat typed modules, stdlib only
├── fixtures/           # bundled demo fixtures + the expected output the demo asserts
├── tests/              # pytest
└── .env.example        # live-lane credential placeholders (never used by the demo)
```

The deterministic core is the artifact; live integrations (mailbox, LLM) are
documented owner-side steps that feed the same folder the demo reads.

## Index

| Script | Use case | Offline check | Live demo |
|---|---|---|---|
| [invoice-ledger](invoice-ledger/) | Parse invoices & receipts into a bookkeeping-ready ledger, idempotently | `invoice-ledger --demo` (4 posted, 2 skipped, 3 reviewed, 1 draft) · `pytest` 23 passed | watched folder; mailbox/LLM lane is owner-supplied |