# swimlane (cross-functional process, BPMN-lite)

A subset of BPMN 2.0.2 collaboration diagrams: enough for hand-offs between roles and companies, not a full BPMN modeller.

## Fields
| Field | Rule |
|---|---|
| `pools` | optional `[{id, label}]`: one per participant (company, customer, external system) |
| `lanes` | `[{id, label, pool}]` in drawing order; lanes of one pool must be consecutive |
| `nodes[]` | `{id, kind, label, lane, trigger, gateway, tag, sub, tone, col, max_w}` |
| `kind` | `task` (default, rounded) · `subprocess` (thick border, tag "sub-process ⊞") · `start` · `intermediate` · `end` · `gateway` · `data` (document) |
| `trigger` | events only: `none` (default) · `message` (envelope) · `timer` (clock, not on end) · `error` (zigzag) · `signal` (triangle) · `terminate` (end only, filled disc) |
| `gateway` | `exclusive` (X, default) · `parallel` (+) · `inclusive` (O) |
| `tag` | task type in words: "user task", "service task", "script task" |
| `col` | optional fixed step index along the flow |
| `flows[]` | `{from, to, type, label}`; `type`: `sequence` (default) · `message` · `default` (label "default") · `conditional` (mini-diamond at the start, not out of a gateway) |
| `direction` | `LR` (lanes as rows) or `TB` (lanes as columns); unset = LR, TB when LR is over 1000px |

## Notation (BPMN 2.0.2)
- Start event: circle, single thin line. Intermediate: double thin line. End: single thick line. Catching triggers unfilled, throwing (end) filled.
- Task: rounded rectangle, single thin line. Gateway: diamond; exclusive X (optional in BPMN, always drawn here), parallel +, inclusive O.
- Sequence flow: solid line, solid arrowhead, only inside one pool. Message flow: dashed line, open circle at the start, open arrowhead, only between pools.
- Event labels sit beside the circle, gateway labels beside the diamond (above in LR, left in TB); arrows keep to the other sides.

## Checks
- Message flow inside one pool, sequence flow between pools → error naming the fix.
- A message flow out of a start event (it only catches) or into an end event (it only throws) → error.
- Start event with an incoming sequence flow, end event with an outgoing one, gateway that neither splits nor merges, timer on an end event, terminate on a non-end event → error.
- At least one start and one end event.

## Layout
- Step index: a sequence flow moves one step on, a message flow keeps the step, so sender and receiver sit level and the dashed line is straight. A reply (a message whose sender was itself reached by a message) moves one step on, so the flow never reads backwards.
- A lane named like its pool (a one-lane pool such as "Vendor") shows only the pool header.
- Boxes that share a lane and step sit side by side, ordered by where their next steps are.
- LR holds ~6 steps at 1000px; longer processes switch to TB (lanes as columns, ≤ 5 lanes), or split at a hand-off.

## Mermaid
- Mermaid has no swimlanes: one `subgraph` per lane ("Pool / Lane"), events as circles, gateways as diamonds with X / + / O, message flows as `-.->`. The SVG is the reference picture.

```json
{"id": "leave", "type": "swimlane", "title": "Leave request", "key": "Circle = event · diamond = gateway",
 "notice": "HR only sees approved requests.",
 "lanes": [{"id": "emp", "label": "Employee"}, {"id": "mgr", "label": "Manager"}],
 "nodes": [{"id": "s", "kind": "start", "label": "Need leave", "lane": "emp"},
           {"id": "ask", "label": "Request leave", "lane": "emp"},
           {"id": "ok", "kind": "gateway", "label": "Approve?", "lane": "mgr"},
           {"id": "e1", "kind": "end", "label": "Booked", "lane": "mgr"},
           {"id": "e2", "kind": "end", "label": "Declined", "lane": "emp"}],
 "flows": [{"from": "s", "to": "ask"}, {"from": "ask", "to": "ok"}, {"from": "ok", "to": "e1", "label": "yes"},
           {"from": "ok", "to": "e2", "label": "no"}]}
```
