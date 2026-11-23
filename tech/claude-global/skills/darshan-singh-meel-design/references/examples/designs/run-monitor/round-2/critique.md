# Critique: round 2
Screenshots: `round-2/shots/` (per file: 1280 light, 390 light, 1280 dark) · Checker: 0 FAIL, 0 WARN · Screenshot warnings: 0

A2 keeps A's hierarchy and sentence headline, takes B's table with chips, search and message column, and quiets the late card; nothing structural is left open, so this round is the final.

## Per direction
| Key | First thing the eye lands on | The memorable element | Weakest spot | Fix applied | Still open |
|---|---|---|---|---|---|
| A2 | Runs: "3 failed" then the first error · Run: the sentence, then the error block | the situation as a sentence; the 24 h strip per failure | the Run page's facts and history compete at the same level below the stages | history first, facts second; both under the stages | two columns vs one on the Run page: decide after use |

## From comments
| Comment | Done · done differently · not done | Why |
|---|---|---|
| The late card should not look like a failure | done | the warning as plain `--warn-text`, no fill; the strip head shows one amber box |
| (critique) coloured edges and the red word in the headline are decoration | done | the strip is the card's head at full width: the differing box is the signal; the headline is one colour |
| (critique) finance button wrapped left, other cards' actions right | done | meta on its own line, actions right-aligned with nowrap labels |
| Buttons on the phone should say which pipeline they retry | done, on every width | "Retry events_hourly", "Retry finance_close_daily from failure": the label is the pipeline's, so it also reads right in a notification |
| Add B's last-14-runs bars to the Run page | done | under the stages, next to the facts |
| B's chips, search and message column under A's cards | done | the table is B's, with the "All runs" heading in the toolbar and no left rail |
| Don't want the left rail | done | nav stays in the header |
| Park C as a Schedules screen | done | brief → Out of scope; C's files stay in round 1 |

## Across directions
- Single direction: the canvas still shows Before next to it for the record.
- Dark theme: the late card's plain warning text reads at 10:1; the strip heads' `--ok-soft` boxes are visible against `--surface-2`.
- Fixture: clock 14:32; every start + duration ≤ 14:32; counts 36 + 3 + 1 + 1 = 41 on both screens.
- Mobile: card and Run actions 44px tall and full width; table drops Owner, Message and the bars; no overflow.
- Copy: counts add up; every primary names its pipeline.

## Measurements
- Overflow / small targets / tiny text / unlabelled inputs / placeholder contrast / accent-color / focus not visible: none.
