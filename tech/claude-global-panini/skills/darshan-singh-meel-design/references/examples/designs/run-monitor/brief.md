# Brief: run-monitor
Mode: redesign · Route: local canvas · Stack: plain HTML (React build later)
Status: final

## Job
- Product: run monitor for a data platform team: every scheduled pipeline (dbt jobs, ingestion syncs, exports) and its last runs.
- User: on-call data engineer, several times a day, laptop at 1280 and phone at 390 when paged.
- Main job of the screens: see what failed in the last 24 hours and get it running again.
- Top 3 questions or actions: 1. What failed and why? 2. Retry it. 3. Is anything late or still running that should have finished?

## Screens
| Screen | Job | Entry from | Leads to | Shared parts |
|---|---|---|---|---|
| Runs | triage the last 24 h | bookmark, pager link | Run | header, nav, status mark, run row, buttons |
| Run | understand one failure and retry it | a run row or card | Runs, log | header, nav, status mark, buttons |

## Inputs
- Screenshots: `before/runs.png` → Runs (inferred: gradient header, 6-item nav, six equal KPI cards, a status pie, a "recent runs" table with colour-only status dots and a "View" button per row; ≈ #f4f6fa ground, ≈ #2b5fd9 accent, ≈ 13px table text, airy density) · `before/run.png` → Run (inferred: breadcrumb, a 10-row definition list with the error nowhere near the top, a dark log tail at 11px, four equal buttons including "Delete run" next to "Rerun")
- Existing code: none provided · Existing tokens: none
- Design system: create

## Constraints
- Fonts: system stacks; serif display for the situation headline; monospace for ids, times, durations and error lines
- Viewports: desktop 1280, mobile 390
- Themes: light and dark (on-call at night)
- Must keep: the four destinations Runs · Pipelines · Schedules · Alerts; run ids
- Accessibility: WCAG AA, keyboard, reduced motion

## Redesign: keep / change / remove
| Element | Decision | Reason (from the job, not taste) |
|---|---|---|
| Nav destinations | keep (4 of 6) | users know them; Settings and Admin are not on-call tasks and move behind the user menu |
| Six KPI cards | remove | "Avg duration" and "SLA" answer no top question; counts move into the headline as a sentence |
| Status pie | remove | a proportion of 41 runs never says which run failed |
| Recent runs table | change → dense table of all 41 | colour-only dots fail the colour-alone rule; status needs a word; "View" per row replaced by the row itself opening the run |
| Gradient header | remove | 70px of decoration above the fold on the phone |
| Run: definition list | change → situation headline + error first | the error line is the reason the user opened the page; it was below 10 facts |
| Run: log tail at 11px | change → error block at body size, full log one click away | unreadable on the phone |
| Run: "Delete run" next to "Rerun" | change → secondary, behind a confirmation | destructive action styled like the primary |
| Run id | keep | pager links carry it |

## Directions (round 1)
| Key | Name | The bet | Memorable element | Layout | Hierarchy (first, largest) | Primary action |
|---|---|---|---|---|---|---|
| A | Triage first | failures are the job; everything else is context | the headline reads like an incident line, in serif; each failure card is headed by its pipeline's last 24 runs | failures stacked on top, quiet table below; Run page error-first | the first failed run and its error line | Retry on each card and on the Run page |
| B | Dense console | the engineer wants every run at once and drills in without leaving the list | the list never leaves: the Run screen is the panel grown wide, the list a narrow rail | rail, dense table, detail panel | the table | Retry in the panel |
| C | Timeline | late and overlapping runs only show on a time axis | time is the axis on both screens: the day grid, and the run's stages on the same hour scale | tabs by day, pipelines × hours; Run page as a stage Gantt | the grid | Open failed (count) |

## Decisions log
- Round 1: A picked for hierarchy and the Run page; B's dense table with chips and search wanted under A's cards; C parked as a later Schedules screen. Comments in `round-1/comments.md`.
- Round 2: A2 = A with B's table, the strip promoted to the card's head (no coloured edges, no coloured word in the headline), a quieter late card, 44px actions on the phone, the Run page with B's last-14-runs bars. Accepted as final.
- Fixture clock: 14:32; every run's start + duration ends at or before it; counts 36 + 3 + 1 + 1 = 41.
