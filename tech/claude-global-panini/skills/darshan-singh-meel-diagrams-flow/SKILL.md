---
name: darshan-singh-meel-diagrams-flow
description: Flow and process diagrams for the darshan-singh-meel-diagrams engine - flowchart, swimlane / cross-functional process (BPMN-lite - pools, lanes, events, tasks, exclusive/parallel/inclusive gateways, message flows), decision tree, UML state machine (event [guard] / action, initial, final, choice, composite), UML activity with fork/join, retry / error-handling flow (bounded retries, DLQ, alert, compensation) and approval workflow (roles, SLAs, approve / reject / changes / escalation). JSON spec to static SVG (light and dark) plus Mermaid, layout-checked; flowchart, retry and approval flows take the airflow style (one run with task states) or the dbt style (dependency or impact chain). Load with darshan-singh-meel-diagrams. Triggers - "flowchart", "process diagram", "swimlane", "BPMN", "decision tree", "state machine", "activity diagram", "fork join", "retry flow", "error handling flow", "dead letter", "approval workflow", "sign-off flow".
---

# Diagrams - flow family

Seven types for "what happens, in which order, by whom, and what if". Load `darshan-singh-meel-diagrams` alongside: it owns the engine, the spec basics (`id`, `type`, `title`, `key`, `notice`), embedding and the layout checker. This skill never edits the base.

## Pick the type
| Question | Type | Not when | Use instead |
|---|---|---|---|
| What are the steps and branches of one process? | `flowchart` | several roles hand work over | `swimlane` |
| Who does which step, and where does work cross teams or companies? | `swimlane` | one actor, or no hand-offs | `flowchart` |
| Which outcome follows from a few yes/no questions? | `decision-tree` | answers loop back or merge | `flowchart` |
| Which states can one thing be in, and what moves it between them? | `state-machine` | the steps are work, not conditions | `activity` / `flowchart` |
| Which work runs in parallel and where does it wait for all branches? | `activity` | no parallelism | `flowchart` |
| What happens when a call fails, how often is it retried, where do failures end? | `retry-flow` | no failure handling to show | `flowchart` |
| Who approves what, with which SLA, and what happens on reject or timeout? | `approval-workflow` | roles are the main point | `swimlane` |

- Call order between services, with timing → interaction family (`sequence`). Task dependencies of a DAG run → data family (`airflow-dag`). Agent loops → ai family.
- Two questions in one picture → two diagrams.

## High level first, then detail
- **Overview:** one `flowchart` with `groups` per stage and `view: "overview"` (one box per stage), or a `swimlane` with only the hand-off tasks. ≤ 7 ± 2 boxes.
- **Detail:** one diagram per stage or lane the reader needs; name it in the overview's Notice.
- Over ~12 boxes, over ~6 swimlane steps per row, or a "canvas would be …px wide" error → split at a hand-off, use the overview, or switch `direction`.

## Spec fields
Per type in `references/`: `flowchart.md` (flowchart, retry-flow, approval-workflow, decision-tree), `swimlane.md` (BPMN-lite), `uml.md` (state-machine, activity). Every field list there ends with a minimal JSON.

## Graph style (plain, dbt, airflow)
| Type | Styles | When |
|---|---|---|
| `flowchart`, `retry-flow`, `approval-workflow` | `plain` (default), `airflow` | `airflow` when the picture is one run: task `state` colours, `operator` as tag (what the step calls), groups as task groups, `collapse`. |
| same | `dbt` | the picture is a dependency or impact chain, not a decision flow: which step waits on which, what a failed step blocks (`dim` the unaffected steps). Pills coloured by `cat`, the author's category (check, build, deploy, service, agent ...). |
| `swimlane`, `decision-tree`, `state-machine`, `activity` | `plain` only | fixed notation (BPMN, UML); a style is a validation error. |

Examples: airflow style `references/examples/webhook-delivery.json` (one delivery run: task group, `post_partner` up_for_retry, failure path to the DLQ); dbt style `references/examples/release-impact.json` (what a failed contract test blocks). The author picks the style that fits; none is forced.

## Process
1. Pick the type from the table; read its reference file.
2. Write the spec with real step names from the code, runbook or process owner; synthetic values only.
3. Build: `python <skills>/darshan-singh-meel-diagrams/scripts/diagram.py spec.json -o x.svg --mermaid x.mmd --png x.png` (the registry finds this family by itself).
4. Fix every spec error and `LAYOUT` line; never ship with one.
5. Look at the PNG, light and `--dark`: every branch labelled, every end reachable, the Notice visible in the picture.
6. Embed as the base skill says (`references/embedding.md` there).

## Notation rules
- **Flowchart:** pill = start / end, box = step, diamond = decision (question inside, every exit labelled), slanted box = input / output, double-sided box = sub-process, cylinder = store. One start; ends have no exits.
- **BPMN-lite** (`references/swimlane.md`): start event thin circle, intermediate double circle, end thick circle; triggers drawn inside (catch unfilled, throw filled). Task = rounded box. Gateway = diamond with X (exclusive), + (parallel), O (inclusive). Sequence flow = solid arrow inside a pool; message flow = dashed, open circle at the start, open arrowhead, only between pools.
- **UML state machine:** filled dot = initial, ringed dot = final, small diamond = choice; transition label `event [guard] / action`; entry / do / exit inside the state; composite = frame with its own initial.
- **UML activity:** black bar = fork (one in, all out run) or join (waits for all in); diamond = decision (guards `[ ]`, one `[else]`) or merge; ringed dot = activity final, circled X = flow final; partitions = bands.
- **Retry:** every retry bounded (`max`), delay and backoff on the loop, every failure path ends in a DLQ, alert, compensation, fallback or end.
- **Approval:** every review / approve step has an approved exit and a rejected or changes exit, names its role; approver role differs from the submitter (four-eyes).

## Sizing limits
- Canvas ≤ 1000px; flowchart boxes wrap at 180px, swimlane tasks at 130px, labels on arrows ≤ 36 characters (guards 34).
- Swimlane: tries lanes as rows (LR) and switches to lanes as columns (TB) when too wide; ≤ 5 lanes in TB.
- State machine: one level of composite states; deeper → own diagram.

## Common mistakes
- A decision with one exit, or exits without labels → error; label every branch.
- Two `start` nodes, or a step that leads nowhere in a diagram with ends → error; one process, one start, every path to an end.
- A process with roles drawn as a flowchart with role names in the boxes → use `swimlane`.
- Sequence flows across pools, message flows inside one pool → BPMN error; the validator says which.
- States named as actions ("Send mail") → states are conditions ("Awaiting payment"); actions go on transitions or `entry`.
- Unbounded retries, or a retry flow with no failure end → validation error.
- One "rejected" end shared by many steps hides who rejected; label the exits.

## Rules
- Notation facts from `references/sources.md` (omg.org BPMN 2.0.2 and UML 2.5.1, mermaid.js.org, airflow.apache.org); unverified items say `check: <page>`.
- Outputs stay local; no real personal data in labels.
- Core changes go to the base skill's owner; this family adds local helpers only.
