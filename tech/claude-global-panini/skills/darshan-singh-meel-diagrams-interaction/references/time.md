# Time: `timeline` and `gantt`

## `timeline` - what happened in which period
| Field | Rule |
|---|---|
| `periods` | 1-14, in order: `{label, section?, events}`; `label` is free text ("2024", "Q3", "Sprint 12") |
| `events` | strings or `{label, sub?, tone?}`; `red` = incident, `green` = capability live, `amber` = risk |
| `sections` | optional eras `{id, label}`; consecutive periods with the same `section` share a band |
| `direction` | `LR` (default when every period gets ≥ 120px) or `TB` (chosen automatically for long timelines) |

- Periods are equally spaced, not to scale. Durations or overlap matter → `gantt`.
- Mermaid: `timeline`, `section …`, `period : event : event`.

```json
{"id": "releases", "type": "timeline", "title": "API versions", "key": "pill = year · box = release",
 "notice": "v1 was retired one year after v2 shipped.",
 "periods": [{"label": "2024", "events": ["v1 GA"]}, {"label": "2025", "events": ["v2 GA", {"label": "v1 retired", "tone": "red"}]}]}
```

## `gantt` - what runs when, how long, what waits on what
| Field | Rule |
|---|---|
| `start`, `end` | the window: ISO dates (`2026-01-05`) or times of day (`02:00`, `02:00:30`); every task must fit |
| `tasks` | `{id, label, section?, start? / after?, end? / days? / minutes? / milestone?}` plus `status`, `kind` or `state` by style, `queued`, `note`, `strong`; the longest label sets the label column (≤ 260px, about 34 monospace characters) |
| `sections` | optional `{id, label}`: phases (roadmap), task groups (Airflow) or threads (dbt) |
| `today` | a date or time; red dashed line labelled "today" |
| `markers` | `[{date, label}]`: lilac dotted lines (freeze, SLA, budget review) |
| `style` | `plain` (default), `airflow`, `dbt` |
| `arrows` | `false` hides dependency arrows (`after` still sets the start) |
| `legend` | `false` hides the legend |

- **Start:** `start`, or `after: [ids]` = starts when the latest of them ends (finish-to-start, drawn as an arrow into the bar's left end; into a milestone's top). With both, `start` may not be before the latest of them ends (a spec error).
- **Length:** `end` (dates: inclusive; times: the instant it stopped), `days` (dates), `minutes` (times, decimals allowed), or `milestone: true` (zero length, black diamond).
- **Look by style:**
  - `plain` - `status`: `done` green, `active` teal ("in progress"), `planned` dashed, `crit` red ("critical path"), `risk` amber. Spec `kinds` adds or overrides statuses.
  - `airflow` - `state` from the Airflow task-instance states (base `AIRFLOW_STATES`); `queued: "02:14"` draws the wait for a worker slot as a dashed grey bar before the run; the note defaults to "state · duration" (`45s`, `18m`, `1h 14m`).
  - Retries: one row per try (`payments_extract (try 1)`); earlier tries `up_for_retry`, the last try its final state.
  - `dbt` - `kind` from the base `DBT_KINDS` (model, seed, snapshot, test, …), solid bars; sections are threads; the note defaults to the duration.
- `note` = short text next to the bar; it moves to the other side or gets a background when a marker line runs under it.
- Mermaid: `gantt`, `dateFormat YYYY-MM-DD` or `HH:mm:ss`, `section`, tags `done` / `active` / `crit` / `milestone` (airflow: `success` → done, `running` → active, `failed` → crit; queued time stays SVG only), `after a b` (a later explicit start keeps the time and a `%%` comment), markers as `vert`. Mermaid draws its own today line on the viewing date.

```json
{"id": "q1-plan", "type": "gantt", "title": "Q1 plan", "key": "bar = work · diamond = milestone",
 "notice": "Testing starts only when both builds are done.", "start": "2026-01-05", "end": "2026-03-27",
 "tasks": [{"id": "a", "label": "Build API", "start": "2026-01-05", "days": 20, "status": "done"},
           {"id": "b", "label": "Build UI", "start": "2026-01-12", "days": 25, "status": "active"},
           {"id": "t", "label": "Test", "after": ["a", "b"], "days": 10},
           {"id": "go", "label": "Go-live", "after": ["t"], "milestone": true}]}
```
Full examples: `examples/lakehouse-roadmap.json` (plain), `examples/nightly-run-gantt.json` (airflow), `examples/dbt-run-timing.json` (dbt).
