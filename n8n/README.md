# n8n Workflows

Production-ready n8n workflows. Each folder is self-contained:

```
<workflow-slug>/
├── workflow.json    # Export straight from n8n — importable as-is
├── .env.example     # Credentials/config placeholders (no secrets, ever)
├── README.md        # Problem → Diagram → Setup → Results
└── assets/          # Canvas screenshot, architecture diagram, demo gif
```

## Index

| Workflow | Use case | Status |
|---|---|---|
| _First workflows being documented._ | | |

## How to import a workflow

1. In n8n, go to **Workflows → Import from File** and pick `workflow.json`.
2. Copy `.env.example` to `.env` (or set the vars in your n8n environment)
   and fill in your credentials.
3. Open each credential node and select your saved credential.
4. Activate.

All workflows are tested on a self-hosted n8n instance (Docker) and n8n
Cloud. Node-version notes live in each workflow's README.
