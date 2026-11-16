# Experience: `journey` and `service-blueprint`

## `journey` - what a user does, thinks and feels per stage
| Field | Rule |
|---|---|
| `persona` | who walks the journey, ≤ 16 characters ("New analyst"); drawn left of the stage headers |
| `stages` | 2-6, left to right: `{id, label, sub?, actions, touchpoints?, thoughts?, score?, feeling?, pains?, opportunities?}` |
| `actions` | what the user does (required); strings |
| `touchpoints` | where it happens: screen, channel, document (teal) |
| `thoughts` | what they think, in their words (amber note) |
| `score` | 1 angry · 2 frustrated · 3 neutral · 4 pleased · 5 delighted; every stage or none. `feeling` replaces the word |
| `pains`, `opportunities` | red boxes / dashed green boxes |

- Rows appear only when a stage fills them; the emotion line joins the scores.
- Mermaid: `journey` with one section per stage and its actions scored; touchpoints, pains and opportunities are SVG only.

```json
{"id": "signup", "type": "journey", "title": "Sign-up", "key": "line = feeling, 5 best", "notice": "E-mail confirmation is the low point.",
 "persona": "Trial user",
 "stages": [{"id": "s1", "label": "Sign up", "actions": ["Enters e-mail"], "score": 4},
            {"id": "s2", "label": "Confirm", "actions": ["Waits for the e-mail"], "pains": ["Lands in spam"], "score": 2}]}
```

## `service-blueprint` - what runs behind each user step
| Field | Rule |
|---|---|
| `items` | `{id, lane, col, label, sub?, fail?, tone?, shape?}`; evidence and customer items may stand without an arrow |
| `lane` | `evidence` (what the customer sees or keeps; document shape), `customer`, `frontstage` (people and screens the customer meets), `backstage` (staff work the customer does not see), `support` (systems, other teams) |
| `col` | step number 0, 1, 2 … - one column per customer action; items of one step share its column |
| `fail` | `true` = fail point: red, thick border, tag "fail point" |
| `edges` | `{from, to, label?}`: what triggers what; base edge fields work |
| `max_w` | box width, default 170; 150 fits four steps, five steps need 120 |

- All five lanes are always drawn, with the line of interaction (customer / frontstage), line of visibility (frontstage / backstage) and line of internal interaction (backstage / support); each line's name sits in the header of the lane above it.
- Arrows between lanes leave sideways and enter from above or below, so none runs along a line.
- No Mermaid form: embed the SVG.

```json
{"id": "refund", "type": "service-blueprint", "title": "Refund", "key": "lane = layer · red = fail point",
 "notice": "Refunds wait on a manual finance step.",
 "items": [{"id": "c", "lane": "customer", "col": 0, "label": "Asks for refund"},
           {"id": "f", "lane": "frontstage", "col": 0, "label": "Agent logs case"},
           {"id": "b", "lane": "backstage", "col": 1, "label": "Finance approves", "fail": true}],
 "edges": [{"from": "c", "to": "f"}, {"from": "f", "to": "b"}]}
```
Full examples: `examples/analyst-onboarding-journey.json`, `examples/data-access-blueprint.json`.
