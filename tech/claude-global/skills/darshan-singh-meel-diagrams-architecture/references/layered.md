# `layered-architecture` - layers, what may call what, where the rule breaks

Bands top-down, an optional cross-cutting column on the right, and arrows between items. Arrows that break the layer rule turn red and get a legend line.

## Spec
```json
{"id": "booking-layers", "type": "layered-architecture", "title": "…", "key": "…", "notice": "…",
 "rule": "strict",
 "layers": [{"id": "api", "label": "API", "items": [{"id": "routes", "label": "HTTP routes", "sub": "FastAPI"}]},
            {"id": "data", "label": "Data", "items": [{"id": "pg", "label": "bookings-db", "kind": "store"}]}],
 "cross_cutting": {"label": "cross-cutting", "items": [{"id": "auth", "label": "Auth", "sub": "JWT check"}]},
 "edges": [{"from": "routes", "to": "pg"}]}
```

| Field | Rule |
|---|---|
| `layers` | ≥ 2, top layer first; each `id`, `label`, `items` (nodes); ids unique and not `cross-cutting` |
| item `kind` | `component` (default, blue), `store` (cylinder, green), `cross` (lav); any base node field |
| `cross_cutting` | optional `{label, items}`: security, logging, config - used by every layer, drawn without arrows |
| `rule` | `strict` (default): a call goes to the layer directly below · `relaxed`: to any layer below |
| `edges` | base edge fields; an upward call is always red, a skipped layer is red under `strict` |
| `header_w`, `max_w` | band header width (default 130), box width limit |

- Items wrap to a second line inside a band when a layer is too wide.
- Mermaid: flowchart TB, one subgraph per layer, rule breaks coloured with `linkStyle`.
- Use it for the shape of one codebase or platform. For the platform's runtime pieces use `c4-container`; for data layers (bronze, silver, gold) the data family's medallion view.
