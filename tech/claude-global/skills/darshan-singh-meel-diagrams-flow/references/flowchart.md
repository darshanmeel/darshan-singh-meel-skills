# flowchart, retry-flow, approval-workflow, decision-tree

Common fields (`id`, `type`, `title`, `key`, `notice`, `max_w`) are in the base skill's `references/spec.md`.

## `flowchart`
| Field | Rule |
|---|---|
| `nodes` | `[{id, label, kind, cat, sub, tag, tone, group, dim, href, tip, state, operator}]`; `label` required |
| `kind` | `start` `end` (pill) · `step` (box, default) · `decision` (diamond, ≥ 2 labelled exits) · `io` (slanted box, input / output) · `subprocess` (box with double sides, details elsewhere) · `store` (cylinder) · `document` · `note` · `wait` (hexagon) · `manual` (rounded) |
| `edges` | `[{from, to, label, style, tone, kind, head, tail, dim}]`; label ≤ 36 chars; `kind: "failure"` = red failure path with a legend line |
| `groups` | `[{id, label, tone}]`; with `view: "overview"` each group becomes one box with a count; `collapse: [ids]` collapses some |
| `direction` | `TB` (default) or `LR` |
| `style` | `plain` (default) · `airflow` (one run: `state` colours, `operator` as tag, groups as task groups) · `dbt` (dependency or impact chain: steps drawn as pills coloured by `cat`, legend from `cat`; `dim` the steps a failure does not touch) |
| `cat` | dbt style only: the author's category of a step (`check`, `build`, `deploy`, `release`, `service`, `agent` ...): colour key and legend entry. Without `cat` the flow kind is the key. Tones come from the spec's `kinds` (`{"deploy": "amber"}`), else one per new category; `tag` stays the author's |

Checks (all three types):
- one `start` (`view: "overview"` excepted); an `end` has no exits;
- every `decision` has ≥ 2 exits, each with a `label` (an `outcome` or edge `kind` counts);
- when the diagram has an `end`, every other step with arrows in has an arrow out (a `store`, `document`, `note`, `dlq`, `alert`, `compensate` or `fallback` may end a path).

```json
{"id": "pw-reset", "type": "flowchart", "title": "Password reset", "key": "Pill = start/end · diamond = decision",
 "notice": "Locked accounts never get a reset link.",
 "nodes": [{"id": "s", "label": "Reset requested", "kind": "start"}, {"id": "q", "label": "Account locked?", "kind": "decision"},
           {"id": "m", "label": "Mail reset link"}, {"id": "h", "label": "Send to helpdesk"}, {"id": "e", "label": "Done", "kind": "end"}],
 "edges": [{"from": "s", "to": "q"}, {"from": "q", "to": "m", "label": "no"}, {"from": "q", "to": "h", "label": "yes"},
           {"from": "m", "to": "e"}, {"from": "h", "to": "e"}]}
```

## `retry-flow`
Same node and edge fields as `flowchart`, with `steps` instead of `nodes`; `direction` default `LR`.

| Field | Rule |
|---|---|
| `steps[].kind` | flowchart kinds plus `dlq` (red cylinder) · `alert` (amber note) · `compensate` (amber) · `fallback` |
| `steps[].retry` | `{"max": n ≥ 1, "delay": "exp 30s"}` → dashed amber self-loop "retry ≤n · delay" above the box (right of it in `TB`) |
| `steps[].timeout` | added to the tag (to the `operator` in airflow style): "timeout 10s"; it widens the box, so drop it when LR runs out of width |
| `edges[].kind` | `failure` (red) · `compensate` (dashed amber) · `fallback` (dotted) · `retry` (a drawn retry edge, e.g. back to an earlier step) |

- Failure, compensation and fallback edges leave from the side (bottom in `LR`) on their own port, so the happy path stays a straight line and no two kinds share a line; a target straight ahead is entered from the same side.
- The retry loop takes a side no side exit uses; a drawn edge back into that step arrives on the other side.
- Checks: retry has `max`; at least one failure path; a failure path ends in a `dlq`, `alert`, `compensate`, `fallback` or `end` step; at least one retry.
- `style: "airflow"` with `state` per step shows one run (e.g. `up_for_retry`, `failed`); omit `state` on steps that have not run.

## `approval-workflow`
| Field | Rule |
|---|---|
| `steps[]` | `{id, label, kind, role, sla, sub, tone, group, state}` |
| `kind` | `start` `end` · `submit` · `review` · `approve` · `auto` (system step) · `notify` · `decision` · `timer` (hexagon) · `store` |
| `role` | shown as the tag; required on `review` and `approve` |
| `sla` | shown under the label: "SLA 3 days" |
| `edges[].outcome` | `approved` (green) · `rejected` (red) · `changes` (dashed amber, back to the submitter) · `escalate` (dashed blue, timeout); default label = outcome |

- Direction `TB` by default; rejected, changes and escalation edges leave from the side.
- Checks: every `review` / `approve` step has an `approved` exit and a `rejected` or `changes` exit and a `role`; an `approve` role differs from every `submit` role (four-eyes rule).
- `style: "airflow"` with `state: "awaiting_input"` shows where a running request waits for a person (the Airflow task state of a human-in-the-loop task, https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html).

## `decision-tree`
| Field | Rule |
|---|---|
| `nodes[]` | `{id, label, parent, answer, sub, tone}`; one root without `parent` |
| `answer` | label of the line from the parent, ≤ 36 chars, required on every non-root node |
| leaves | nodes without children = outcomes (pill, `tone` for meaning, default soft) |
| `direction` | `TB` (default) or `LR` for deep, narrow trees |

- Questions are boxes with a thick border; each needs ≥ 2 answers. The parent chain must reach the root.
- Lines are drawn org-chart style: trunk from the question, a bus halfway to the answers, a drop into each child; each answer sits on its own part of the bus.
- `style`, `view` and `collapse` do not apply (fixed notation).
- Over 1000px → `direction: "LR"` or split a subtree into its own diagram.
- Same outcome in two places is fine (two leaves with the same label and different ids).

## Mermaid
- All four write a Mermaid `flowchart`; I/O uses `@{ shape: lean-r }`, sub-process `@{ shape: subproc }` (Mermaid 11.3+ shape syntax; check: https://mermaid.js.org/syntax/flowchart.html), edge colours as `linkStyle`.
- Self-loops (retries) are written as `a -.-> a`.
- The header names the direction the SVG used (an LR flow that ran out of width is written `flowchart TB`).

## dbt style on a flowchart
A dependency or impact chain of any kind (CI stages, service calls, agent steps, job chains): `cat` per step, `dim` what a failure does not touch. Full example: `examples/release-impact.json`.

```json
{"id": "deploy-impact", "type": "flowchart", "style": "dbt", "title": "What a failed image build blocks",
 "key": "Pill colour = stage kind · faded = not affected", "notice": "Docs still publish when the image build fails.",
 "kinds": {"deploy": "amber"},
 "nodes": [{"id": "s", "label": "merge", "kind": "start"}, {"id": "img", "label": "build_image", "cat": "build", "tone": "red"},
           {"id": "docs", "label": "build_docs", "cat": "build", "dim": true},
           {"id": "dep", "label": "deploy_api", "cat": "deploy", "tag": "helm upgrade"}, {"id": "e", "label": "live", "kind": "end"}],
 "edges": [{"from": "s", "to": "img"}, {"from": "s", "to": "docs", "dim": true}, {"from": "img", "to": "dep"},
           {"from": "dep", "to": "e"}, {"from": "docs", "to": "e", "dim": true}]}
```
