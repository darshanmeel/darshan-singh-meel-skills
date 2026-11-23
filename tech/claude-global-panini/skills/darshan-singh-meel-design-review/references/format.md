# Review file format

File: `reviews/design-<YYYY-MM-DD-HHMM>.md` in the project root; name taken → `...-<HHMM>-<name>.md`, never overwrite. Screenshots in `reviews/shots/design-<YYYY-MM-DD-HHMM>/`. Paths relative to the project root. Omit empty sections except "Job", "Runs" and "Not checked".

```markdown
# Design review: <name or file>
Date: <YYYY-MM-DD HH:MM> · Skill: darshan-singh-meel-design-review · Input: <designs/<name>/final | round-2 | file.html | 3 screenshots | http://localhost:8501 | src/pages/Runs.tsx>
Verdict: <Ship | Fix first | Redesign>
Counts: Must <n> · Should <n> · Other <n> · Checker: <n FAIL, n WARN | not applicable>

<One sentence: the verdict and the finding that decides it.>

## Job
- Product · user · main job: <from brief/spec | inferred: …>
- Top 3 questions: 1. … 2. … 3.
- Five-second test (1280, light): saw <a, b, c> → <answers question 1 | does not>

## Must
- **[<area>] <screenshot path> (<region>) | <selector or file:line>** - what: <quoted or measured> · why: <the job or rule> · fix (local | structural): <one line>

## Should
- ...

## Other
- ...

## Screens
<!-- several screenshots or screens -->
| Screen | Job (inferred) | First thing seen | Shared parts | Inconsistent with |
|---|---|---|---|---|

## Directions
<!-- a round with several directions -->
| Key | Layout | Hierarchy | Primary action | Navigation | Differs from the others in |
|---|---|---|---|---|---|

## Measurements
| What | Where | Value | Limit | Source |
|---|---|---|---|---|
| contrast --ink-2 on --surface-2, dark | tokens.css | 7.30:1 | 4.5 | check_design.py |
| horizontal overflow | b-console 390 light | 447 > 390 px | none | screenshot.py |
| smallest target | final 390 | chip 72×28 | 24 | screenshot.py |
| keyboard stops | final 1280 | 14, all visible | all | screenshot.py KEYS |

## Spec vs design
<!-- final/ only -->
- In spec, not in HTML: <none | list>
- In HTML, not in spec: <none | list>
- Maps to: <n paths, n missing>
- Tokens: root vs final <equal | differ: names>

## Runs
| What | Command | Exit | Result |
|---|---|---|---|
| checker | `python <design skill dir>/scripts/check_design.py designs/run-monitor --final` | 0 | 0 FAIL, 0 WARN |
| screenshots | `python <design skill dir>/scripts/screenshot.py designs/run-monitor/final --out reviews/shots/design-…/ --keyboard 20` | 0 | 8 images, 0 WARN |

## Checked without findings
<areas 1-12 that passed, one line>

## Not checked
<what could not be verified and why: no browser (command for the user), app not started (reason), screenshot-only input (no states, no keyboard), spec absent>
```

## Rules for the sections
- Area tags: Job, Hierarchy, Layout, Type, Colour, Spacing, States, Accessibility, Copy, Generic, Consistency, Spec (areas 1–12 of the checklist, in that order); Privacy findings use the Spec area with "Privacy" in the what.
- A finding's place names a screenshot the report produced, not one given as input, whenever the state renders; input screenshots are cited as `input: <path>`.
- Values that look personal are never quoted: kind + `<redacted>`.
- No finding without a row in Measurements or a quoted line.

## After fixes (only when the user asked for them)
Append:
```markdown
## Fixed <YYYY-MM-DD HH:MM>
- Must 1 - <what changed in designs/…> · rerun: <command> exit 0
- Should 2 - not changed: <reason>
Verdict after fixes: <...>
```
