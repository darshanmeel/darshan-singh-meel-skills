---
name: darshan-singh-meel-diagrams-interaction
description: Interaction and time diagrams for the darshan-singh-meel-diagrams engine - UML sequence (lifelines, sync / async / reply, activation, alt / opt / loop / par / break / critical frames, notes), timeline (periods, events, eras), Gantt / roadmap / run timing (milestones, dependencies, today line), user / customer journey (actions, touchpoints, thoughts, emotion line, pains, opportunities), service blueprint (evidence, customer, frontstage, backstage, support), RACI matrix and swimlane handoff timeline (team lanes x time, waits). JSON spec to static SVG (light and dark) plus Mermaid where Mermaid has the type. Gantt takes the airflow style (one DAG run - queued and running time, states) and the dbt style (model timing by thread); handoff takes both. Load with darshan-singh-meel-diagrams. Triggers - "sequence diagram", "who calls whom", "timeline", "roadmap", "Gantt", "run timing", "where did the time go", "customer journey", "service blueprint", "RACI", "handoff", "lead time between teams".
---

# Diagrams - interaction family

Seven types for "who talks to whom, in what order, over what time". Load `darshan-singh-meel-diagrams` alongside: it owns the engine, the common fields (`id`, `type`, `title`, `key`, `notice`), embedding and the layout checker. This skill never edits the base.

## Pick the type
| Question | Type | Not when | Use instead |
|---|---|---|---|
| Which component calls which, in what order, what comes back, what if it fails? | `sequence` | no call order, only structure | architecture family (`c4-container`) |
| What happened (or will) in which period? | `timeline` | dates, durations or overlap matter | `gantt` |
| What runs when, how long, what waits on what, are we on time? | `gantt` | only the order of events | `timeline` |
| Where did a DAG run or dbt build spend its time? | `gantt` + `style` | the task dependencies are the point | data family (`airflow-dag`, `dbt-lineage`) |
| What does a user do, feel and hit at each stage? | `journey` | the systems behind it are the point | `service-blueprint` |
| Which staff actions and systems sit behind each user step, and where does it fail? | `service-blueprint` | no user-facing service | `swimlane` (flow family) |
| Who is responsible, accountable, consulted, informed per task? | `raci` | the order of work matters | `handoff` or `swimlane` |
| Where does work wait between teams, and how long? | `handoff` | one team, or no timing | `swimlane` (flow family) |

- A process with decisions per role → flow family `swimlane`. Message topics and producers without order → architecture family `event-driven`.
- Two questions in one picture → two diagrams.

## High level first, then detail
- **Sequence:** first the happy path across ≤ 5 participants (systems, not classes); then one diagram per failure path or sub-call. One diagram ≈ one use case.
- **Roadmap:** one Gantt with one bar per work package per section; detail Gantts per section only for the team running it.
- **Journey → blueprint:** the journey for the user's view; a blueprint for the one or two stages with the pains.
- **Run timing:** one bar per task of the DAG or per resource of the dbt build; a whole project → the slowest path only.

## Spec fields
Per type in `references/`: `sequence.md`, `time.md` (timeline, gantt), `experience.md` (journey, service-blueprint), `roles.md` (raci, handoff). Each ends with a minimal JSON.

## Graph style (plain, dbt, airflow)
| Type | Styles | When |
|---|---|---|
| `gantt` | `plain` (default) | roadmaps and plans: `status` done / active / planned / crit / risk |
| `gantt` | `airflow` | one DAG run: `state` per task (Airflow task-instance states), `queued` time drawn dashed before the bar, state and duration next to the bar |
| `gantt` | `dbt` | one dbt build: `kind` per resource (model, seed, snapshot, test …) as solid colour, sections = threads, duration next to the bar |
| `handoff` | `plain`, `airflow`, `dbt` | `airflow` when the steps have a run state (a release in flight), `dbt` when they have kinds; `view` / `collapse` are rejected - lanes are the grouping |
| `sequence`, `timeline`, `journey`, `service-blueprint`, `raci` | none | fixed notation; `style` is ignored |

Examples: `nightly-run-gantt` (airflow), `dbt-run-timing` (dbt), `model-release-handoff` (airflow).

## Process
1. Pick the type from the table; read its reference file.
2. Write the spec with real names from the code, logs, plan or process owner; synthetic values only.
3. Build: `python <skills>/darshan-singh-meel-diagrams/scripts/diagram.py spec.json -o x.svg --mermaid x.mmd --png x.png` (the registry finds this family by itself).
4. Fix every spec error and `LAYOUT` line; never ship with one.
5. Look at the PNG, light and `--dark`: every label readable, nothing on a line, the Notice visible in the picture.
6. Embed as the base skill says (`references/embedding.md` there). `service-blueprint` and `raci` have no Mermaid form: embed the SVG file in Markdown.

## Notation rules
- **Sequence (UML):** participant box on top with a dashed lifeline; synchronous call = solid line, filled head; asynchronous = solid line, open head; reply = dashed line, open head; white bar = active (a sync call opens it on the receiver, the reply closes it; actors never get one). Frames: operator in the tab (`alt`, `opt`, `loop`, `par`, `break`, `critical`), guard in `[ ]`, operands split by a dashed line. Notes = amber folded box. `autonumber` numbers the messages.
- **Timeline:** periods left to right in order, equal spacing (not to scale); events stacked under their period; sections = eras as bands.
- **Gantt:** time to scale; bar = work, black diamond = milestone (zero length), arrow = finish-to-start dependency entering the bar's left end, red dashed line = today, lilac dotted line = marker (freeze, SLA, review). Dates: end is inclusive; times: end is the instant it stopped.
- **Journey:** stages left to right; rows actions, touchpoints, thoughts, emotion (1 angry … 5 delighted, dot colour red / amber / green and the word), pain points (red), opportunities (dashed green).
- **Service blueprint:** five lanes, top to bottom - physical evidence, customer actions, frontstage, backstage, support processes; dashed lines of interaction, visibility and internal interaction between them; `fail: true` marks a fail point (red, thick).
- **RACI:** one A per task, at least one R; A/R allowed when the same role does and signs off; empty = not involved.
- **Handoff:** lanes = teams, columns = time slots with headings; arrows between lanes are handoffs (amber) labelled with the wait.

## Sizing limits
- Canvas ≤ 1000px. Sequence ≤ 6 participants and message labels ≤ 36 characters (longer → a note). Timeline LR up to 6-7 periods, then it turns top-down automatically; ≤ 14 periods.
- Gantt ≤ ~20 rows; label column ≤ 260px. Journey 2-6 stages. Blueprint ≤ 5 steps at `max_w` 150. RACI ≤ 8 roles. Handoff ≤ 5 time slots (4 in dbt style: pills are wider).
- The engine names the fix when something does not fit: fewer participants, shorter labels, split.

## Common mistakes
- Sequence with classes and methods instead of systems: readers want the network calls. Return arrows for async messages: there is no reply.
- Gantt bars with no owner question: the Notice should name the critical path or the slip.
- Journey with system steps: those belong in the blueprint. Emotion scores without a reason in a pain or thought.
- RACI with two A's or none, or a role column nobody fills.
- Handoff labels with the work instead of the wait: the label is the waiting time.

## Rules
- Notation facts come from `references/sources.md`; anything unverified is marked `check: <page>` there.
- Output stays local; no real personal data in labels. All examples in `references/examples/` are synthetic.
- Tests: `python tests/run.py` (builds every example, runs `check.py`, Mermaid and validation checks); `--write` refreshes the example SVGs.
