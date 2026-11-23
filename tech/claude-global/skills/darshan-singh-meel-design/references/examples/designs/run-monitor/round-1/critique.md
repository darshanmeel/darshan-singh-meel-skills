# Critique: round 1
Screenshots: `round-1/shots/` (per file: 1280 light, 390 light, 1280 dark) · Checker: 0 FAIL, 0 WARN · Screenshot warnings after fixes: 0

A serves the job best on both screens: the situation line and the first error are the first things seen at 1280 and 390, and the Run page opens on the error; B has the strongest table but its Run screen loses the list on the phone; C answers "is anything late" fastest and nothing else.

## Per direction
| Key | First thing the eye lands on | The memorable element | Weakest spot | Fix applied | Still open |
|---|---|---|---|---|---|
| A | Runs: "3 failed" in the serif line, then the first error · Run: the sentence "events_hourly failed at 13:30" | the situation as a sentence; the 24 h strip under each failure | the coloured left edges and the red "3 failed" in the headline are decoration the frontend rules ban; the late card uses the failure shape; "Retry" without the pipeline name; the long finance button wraps left while the other cards' actions sit right | strip captions state the counts; the strip became the card's head at full width | edges and headline colour (round 2); late card shape; row alignment; the table is thinner than B's |
| B | Runs: the chips, then the selected row · Run: the list rail, then the heading | the list never leaves: the Run screen keeps the rail | at 390 the rail and the list vanish, so the Run screen is a plain page; the panel's "Open run" duplicates the row click | table in a scroll container, message column ellipsized | mobile shape of the master-detail |
| C | the red cells on the hour axis · Run: the 30 min red stage bar against its 1 min ghost | time as the axis on both screens; the p50 ghost under each stage | ok cells carry a duration only; the failed run's error is one click away; "Open 3 failed" sends the user elsewhere | cells are links, so the grid itself navigates | the error line is never on the Runs screen |

## Across directions
- Structure: A (sentence, cards, list; Run as an error-first page), B (rail, table, panel; Run as the panel grown wide), C (tabs, hour grid; Run as a stage Gantt): no pair shares more than one of layout, hierarchy, primary action, navigation.
- Dark theme: shadows invisible, cards rely on `--border`; `--danger-soft` reads as a dark red block behind the error line with 9:1 text; the serif line holds in dark.
- Repeated cards: with meta and actions on separate lines the rows align whatever the button length; the 2×2 grid stretches cards to equal height, so `align-content: start` keeps the gaps equal.
- Mobile: no overflow in any file at 390 (B's table scrolls inside `.scroll`); C's grid scrolls inside `.grid` with the pipeline column sticky; card buttons 44px in A.
- Generic-look and default-console check: A is "cards above a table" without the sentence and the strips; with them it has a point of view. B and C are structural bets by nature.
- Copy: counts add up (36 ok + 3 failed + 1 late + 1 running = 41); "Retry from failure" is dbt's own term for a resumable job; "Delete run…" is quiet and ends in an ellipsis because it confirms.

## Measurements
- Overflow / small targets / tiny text / unlabelled inputs / placeholder contrast / accent-color / focus not visible: none after fixes. Keyboard walks: A Runs reaches nav → Open log → Retry; B Runs reaches rail → chips → select → search; C Runs reaches "Open 3 failed" → tabs → the cells.
