# Visual style — "Paper"

The repo's shared design language for every diagram (archify SVGs, Mermaid
node graphs, future graphics). One palette, one set of semantic colors, so
readers learn it once and read every diagram the same way.

## Palette

| Token | Value | Role |
|---|---|---|
| `bg` | `#FFFFFF` | Canvas — always light |
| `grid` | `#EEF2F7` | Background grid hairlines |
| `ink` | `#0F172A` | Primary text |
| `muted` | `#64748B` | Secondary text, edge labels |
| `edge` | `#94A3B8` | Default connectors |
| `lane-fill` | `rgba(15,23,42,.035)` | Swimlane wash |
| `lane-stroke` | `#D8E0EA` | Swimlane borders |

## Semantic colors

Node role — never decorated arbitrarily, always by function:

| Role | Fill | Stroke | Shape (Mermaid) | Meaning |
|---|---|---|---|---|
| `trigger` | `#EFF6FF` | `#3B82F6` | stadium | Entry point — cron, webhook, manual |
| `logic` | `#ECFDF5` | `#10B981` | rect | Deterministic processing / merge / code |
| `decide` | `#FFFBEB` | `#F59E0B` | rhombus | Branch — IF, Switch, route |
| `store` | `#F5F3FF` | `#8B5CF6` | cylinder | Persistence — Sheets, DB, ledger |
| `ai` | `#FDF2F8` | `#EC4899` | rect | LLM / AI node |
| `external` | `#F8FAFC` | `#64748B` | rect | Third-party service call |
| `gate` | `#FEF2F2` | `#EF4444` | — | Human approval / exception (lanes) |
| `disabled` | — | — | dashed, 55% | Demo-only / disabled node |

Emphasis edge: `#10B981`. Dashed = optional or async.

## Mapping to generators

- **archify** (`assets/diagram.svg`): `frontend→trigger blue`,
  `backend→logic green`, `database→store violet`, `cloud→amber`,
  `security→gate red`, `messagebus→pink`, `external→slate`. Applied via
  CSS-variable override injected by `scripts/extract-archify-svg.py` at
  extract time — never hand-edit the SVG.
- **Mermaid** (README node graphs): node shape + `classDef` assigned by
  `scripts/render-mermaid.py` from the n8n node type — regenerate, don't
  hand-tune. Decision nodes (IF/Switch) take the amber diamond; nodes
  named `*approv*` take the red gate class.

> Note: amber is the one token with two meanings — "branch/decision" in
> node graphs, "cloud service" inside archify diagrams. Both layers carry
> their own legend/shape vocabulary, so the shared palette stays
> unambiguous in context.

## Type & shape rules

- Monospace voice (JetBrains Mono in archify, mono stack in Mermaid) —
  technical, blueprint-adjacent.
- Light background only — no dark-mode exports into READMEs.
- Rounded corners; thin strokes (≤2px); no shadows.
