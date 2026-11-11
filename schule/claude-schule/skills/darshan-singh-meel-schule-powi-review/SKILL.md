---
name: darshan-singh-meel-schule-powi-review
description: Review teaching material for Politik und Wirtschaft and Wirtschaftswissenschaften (Hessen, Gymnasium Sek I and Oberstufe) - solves every task independently, checks curriculum fit (Inhaltsfelder, KCGO Themenfelder, GK/LK), neutrality (Beutelsbacher Konsens), sources and dates of every real figure, labels on model data, institutions and law, models and diagrams, judgement tasks and their marking, the German lines and their English lines, animations, and writes a report with verdict and Must / Should / Other findings to reviews/. Use with darshan-singh-meel-schule and darshan-singh-meel-schule-powi. Triggers - "PoWi-Material prüfen", "Arbeitsblatt Politik und Wirtschaft überprüfen", "Klausur PoWi gegenlesen", "Erwartungshorizont prüfen", "ist das neutral", "Beutelsbacher Konsens prüfen", "Daten und Quellen prüfen", "Review Wirtschaft"; "review my economics worksheet", "check the politics test", "is this material balanced", "check sources and dates", "review the market animation".
---

# Review: Politik und Wirtschaft · Wirtschaftswissenschaften

Reviews; does not rewrite. Fixes only when the user asks, then re-runs the checks.

## Load
1. `darshan-singh-meel-schule`: `references/review.md` (process, 12-area checklist, severity, report format, verdict), `references/bilingual.md`, `references/operatoren.md`, `references/bewertung.md` for tests.
2. `darshan-singh-meel-schule-powi`: the level reference (`sek1.md`, `oberstufe.md` or `wirtschaftswissenschaften.md`), `fachregeln.md`, `modelle-animationen.md` when a model appears, `begriffe.md`.
3. `references/checks.md` of this skill.

## Process (fixed)
1. **Scope** - files to review (default: every `.html` in the topic folder). One question only if the level or GK/LK cannot be read from the files.
2. **Check script** - `python <base skill dir>/scripts/check_material.py <folder>`. Every FAIL = Must. Every `?` line is checked by hand.
3. **Solve first** - work every task from the material alone, before opening `loesung.html` or `erwartungshorizont.html`. Write down result, steps and, for judgement tasks, two defensible positions with criteria. Recompute every number: table rows against the curve, intersections, sums of flows, percentages, percentage points, point totals, grade key thresholds.
4. **Compare** with the solution: differences are findings (wrong solution, ambiguous task, missing alternative, points not awardable).
5. **Subject checks** - walk `references/checks.md` (P1-P10).
6. **Base checklist** areas 1-12; **DE/EN pairs** with the 3-step test, subject terms against `begriffe.md`.
7. **Animation** - step through forwards and backwards; captions against the picture; end state against the solution.
8. **Report** - `reviews/darshan-singh-meel-schule-powi-review-<YYYY-MM-DD-HHMM>.md` in the base report format; add `/reviews/` to `.gitignore` on first use. Reply: verdict, counts, report path (relative), the three most important findings.

## Severity (subject additions to the base table)
| Finding | Level |
|---|---|
| One-sided material or a solution that rewards one political position | Must |
| Real figure without source, Stand or retrieval date; real and model data mixed; figure cannot be traced | Must |
| Wrong statement about an institution, a legal rule, a model mechanism, a number | Must |
| Real person, party or firm shown in a way that judges them, or outdated office holder / majority presented as current | Must |
| Copied cartoon, press text or textbook task | Must |
| Model used without any limit named; categories of judgement missing in the task but demanded in the marking | Should |
| Data older than 2 years without a note; `check:` items of the references that the material relies on | Should |
| Stronger controversy available, better material type, clearer diagram | Other |

## Report additions
- Section "Unabhängig gelöst / Solved independently": one line per task - own result · solution's result · `gleich` or the difference.
- Section "Daten und Quellen / Data and sources": each real figure - value · source line present · date · could it be verified (yes / no, why).
- Verification of real figures needs network permission and official pages only (`fachregeln.md` list). Without it: list them under "Not checked".
