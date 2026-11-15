# `sequence` - UML sequence diagram

Answers: who calls whom, in what order, what comes back, which branch runs when.

## Fields
| Field | Rule |
|---|---|
| `participants` | ≥ 2, left to right in call order: `{id, label, sub?, actor?, shape?}`. `actor: true` draws a stick figure (a person); `shape: "cylinder"` a store, any base shape works. `sub` = technology, one short line. |
| `steps` | in time order; each is a message, a note or a frame (below) |
| `autonumber` | `true` prefixes "1. 2. …" (Mermaid: `autonumber`) |

**Message** `{from, to, label, kind?, activate?, deactivate?, tone?}`
- `kind`: `sync` (default, solid line, filled head), `async` (solid, open head), `reply` (dashed, open head).
- `from == to` = self call, drawn as a loop to the right.
- Activation: a `sync` message opens a bar on the receiver (not on actors); a `reply` closes the sender's bar. `activate: false` / `true` and `deactivate: true` override.
- `label` ≤ 36 characters: the operation or event name (`POST /orders/{id}/pay`, `OrderPaid`). Payload detail → a note.
- `tone`: `red` for a failure path, other edge tones as in the base.

**Note** `{note, right_of | left_of | over}`; `over` takes one id or a list (spans those lifelines).

**Frame** `{frame, label, steps, else?}`
- `frame`: `alt` (choice), `opt` (optional), `loop`, `par` (parallel), `break` (stop the rest), `critical` (atomic).
- `label` = guard in square brackets: `[card declined]`, `[every 2 s, max 30 s]`.
- `else`: more operands `[{label, steps}]` for `alt` (Mermaid `else`), `par` (`and`), `critical` (`option`).
- Frames nest; keep it to two levels.

## Layout
- Lifelines are spaced so every message label fits between its two lifelines; self calls and notes widen the gap they need.
- Frames span the lifelines their messages touch, plus padding per nesting level; the tab and guards cover the lifelines under them.
- Over 1000px → `layout:` error with the fix (fewer participants, shorter labels, split).

## Mermaid
`sequenceDiagram` with `participant id as Label` / `actor`, `->>` sync, `-)` async, `-->>` reply, `+` / `-` activation, `Note …`, frames with `end`. `#`, `;` and `:` in labels are written as `#35;`, `#59;` and a ratio sign.

## Minimal
```json
{"id": "login", "type": "sequence", "title": "Login with SSO", "key": "solid = call · dashed = reply",
 "notice": "The session is created only after the token is verified.",
 "participants": [{"id": "u", "label": "User", "actor": true}, {"id": "app", "label": "web-app"}, {"id": "idp", "label": "Identity provider"}],
 "steps": [{"from": "u", "to": "app", "label": "open /dashboard"},
           {"from": "app", "to": "idp", "label": "redirect /authorize"},
           {"from": "idp", "to": "app", "label": "code", "kind": "reply"},
           {"from": "app", "to": "u", "label": "set session cookie", "kind": "reply"}]}
```
Full example: `examples/checkout-payment.json`.
