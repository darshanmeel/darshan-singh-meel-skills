# Roles: `raci` and `handoff`

## `raci` - who does, signs off, is asked, is told
| Field | Rule |
|---|---|
| `roles` | column headings, ≤ 8: roles or teams, never people's names |
| `tasks` | `{label, cells}`; one cell per role: `""`, `"R"`, `"A"`, `"C"`, `"I"` or a pair such as `"A/R"` |

- Validation: exactly one A per task, at least one R, letters R A C I only.
- Cell colour: A ink (strongest), R blue, C teal, I grey; the letters say it too. Empty cells keep a thin outline.
- No Mermaid form: embed the SVG, or write the table in Markdown.

```json
{"id": "deploy-raci", "type": "raci", "title": "Production deploy", "key": "R does · A signs off · C asked · I told",
 "notice": "The service owner signs off, not the platform team.",
 "roles": ["Developer", "Service owner", "Platform"],
 "tasks": [{"label": "Merge to main", "cells": ["R", "A", ""]}, {"label": "Deploy", "cells": ["C", "A", "R"]}]}
```

## `handoff` - where work waits between teams
| Field | Rule |
|---|---|
| `lanes` | ≥ 2 `{id, label}`: teams, roles or systems, top to bottom |
| `steps` | `{id, lane, col, label, sub?, …}` plus `state` / `operator` (airflow style) or `kind` (dbt style) |
| `col` | time slot 0, 1, 2 …; two steps of one slot in different lanes stack vertically |
| `columns` | optional headings per slot ("day 1", "Mon", "sprint 3") |
| `handoffs` | `{from, to, label?}`; across lanes they become `kind: "handoff"` (amber, legend "handoff to another team"); `label` = the wait ("3 d") |
| `style` | `plain` (default), `airflow`, `dbt`; `view` and `collapse` are rejected |
| `max_w` | box width, default 130; dbt names over ~14 characters wrap at 130 - unbroken names need `max_w` 160 and ≤ 3 slots |

- Keep wait labels short (`"3 d"`, `"4 h"`): the gap between slots grows with the label.
- Put a handoff's target in a later slot. A same-slot handoff leaves the wait label only the gap between lanes; when `check.py` reports it on a lane border, move the target one slot later.
- Mermaid: flowchart with one subgraph per lane.

```json
{"id": "hire", "type": "handoff", "title": "Hiring", "key": "lane = team · label = wait", "notice": "HR waits two days for the budget.",
 "lanes": [{"id": "hm", "label": "Hiring manager"}, {"id": "hr", "label": "HR"}],
 "steps": [{"id": "req", "lane": "hm", "col": 0, "label": "Open role"}, {"id": "post", "lane": "hr", "col": 1, "label": "Post job"}],
 "handoffs": [{"from": "req", "to": "post", "label": "2 d"}]}
```
Full examples: `examples/data-incident-raci.json`, `examples/model-release-handoff.json`.
