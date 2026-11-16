# state-machine and activity (UML 2.5.1)

## `state-machine`
| Field | Rule |
|---|---|
| `states[]` | `{id, label, kind, parent, entry, do, exit, tone, dim}` |
| `kind` | `state` (default, rounded box) · `initial` (filled dot) · `final` (ringed dot) · `choice` (small diamond) |
| `parent` | id of a composite state; a state with children is drawn as a frame; one level only |
| `entry` / `do` / `exit` | behaviours shown inside the state as `entry / …` |
| `transitions[]` | `{from, to, event, guard, action, style, tone, from_side, to_side}`; label = `event [guard] / action`, ≤ 36 chars; `from_side` (`left right top bottom`) moves a crossing line, e.g. a transition leaving a composite frame sideways |
| `direction` | `LR` (default), switches to `TB` when too wide |

- A transition may start or end on a composite (the frame), e.g. "cancel" out of every sub-state.
- Checks: exactly one top-level initial; at most one initial per composite; an initial has one outgoing transition and no event; a final has none; a choice has ≥ 2 outgoing transitions, each with a guard (`else` for the rest); no composite inside a composite.
- Several final states are allowed; one per end state (Delivered, Cancelled, Expired) keeps lines short instead of funnelling everything into one ringed dot.
- States are conditions ("Awaiting payment"), not actions; the work goes on transitions (`/ action`) or `entry`.
- Mermaid: `stateDiagram-v2` with `[*]`, `<<choice>>`, `state X { }`; transitions between scopes are written at top level (Mermaid cannot draw some of them inside composites; check: https://mermaid.js.org/syntax/stateDiagram.html).

```json
{"id": "door", "type": "state-machine", "title": "Door controller", "key": "Dot = initial · label = event [guard] / action",
 "notice": "A locked door ignores 'open'.",
 "states": [{"id": "i", "kind": "initial"}, {"id": "c", "label": "Closed"}, {"id": "o", "label": "Open"},
            {"id": "l", "label": "Locked"}],
 "transitions": [{"from": "i", "to": "c"}, {"from": "c", "to": "o", "event": "open"}, {"from": "o", "to": "c", "event": "close"},
                 {"from": "c", "to": "l", "event": "lock", "guard": "code ok"}, {"from": "l", "to": "c", "event": "unlock"}]}
```

## `activity`
| Field | Rule |
|---|---|
| `nodes[]` | `{id, kind, label, sub, tag, tone, partition}` |
| `kind` | `action` (default, rounded) · `initial` · `final` (activity final, ringed dot) · `flow_final` (circled X: ends one branch only) · `decision` / `merge` (small diamond) · `fork` / `join` (black bar) · `object` (box) · `accept` / `send` (box, tag "accept event" / "send signal") |
| `partitions` | optional `[{id, label}]`: drawn as bands (activity swimlanes) |
| `edges[]` | `{from, to, guard, label}`; `guard` drawn as `[guard]`, ≤ 34 chars |
| `direction` | `TB` (default) or `LR` |

- Checks: an initial (no incoming, one outgoing); fork 1 in / ≥ 2 out; join ≥ 2 in / 1 out; decision 1 in / ≥ 2 out with a guard on every exit; merge ≥ 2 in / 1 out; finals have no outgoing.
- Fork and join bars grow with their branch count; their arrows leave and arrive at separate points.
- Decision exits leave from the side corners.
- Mermaid: `flowchart` with `@{ shape: fork }`, `sm-circ`, `fr-circ`, `cross-circ` (Mermaid 11.3+; check: https://mermaid.js.org/syntax/flowchart.html). Mermaid lists `cross-circ` as "Summary"; it stands in for the flow final because it looks the same.

```json
{"id": "backup", "type": "activity", "title": "Nightly backup", "key": "Bar = fork / join",
 "notice": "Both dumps must finish before the upload.",
 "nodes": [{"id": "i", "kind": "initial"}, {"id": "f", "kind": "fork"}, {"id": "a", "label": "Dump orders db"},
           {"id": "b", "label": "Dump users db"}, {"id": "j", "kind": "join"}, {"id": "u", "label": "Upload to bucket"},
           {"id": "e", "kind": "final"}],
 "edges": [{"from": "i", "to": "f"}, {"from": "f", "to": "a"}, {"from": "f", "to": "b"}, {"from": "a", "to": "j"},
           {"from": "b", "to": "j"}, {"from": "j", "to": "u"}, {"from": "u", "to": "e"}]}
```
