---
name: darshan-singh-meel-schule-chemie-review
description: Reviews Chemie teaching material for the Gymnasium in Hessen (Sek I and Oberstufe) - lesson plans, worksheets and solutions, tests and Klausuren with Erwartungshorizont, experiment sheets, explanations, animations - against the shared school rubric plus chemistry checks - every task solved and every equation balanced independently (atoms, charges, electrons), calculations redone with units, Stoffebene and Teilchenebene kept apart, GK/LK level, safety block (GHS source, student restrictions by Jahrgang, disposal), expected observations, particle counts in animations, and the German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-schule-chemie or on any existing chemistry material. Triggers - "Chemie-Material prüfen", "Chemie Arbeitsblatt prüfen", "Klausur Chemie gegenlesen", "Erwartungshorizont Chemie prüfen", "Reaktionsgleichungen prüfen", "Chemie-Lösung nachrechnen", "Chemie-Versuch Sicherheit prüfen", "Gefährdungsbeurteilung gegenlesen"; "review chemistry worksheet", "check my chemistry test", "check the chemical equations", "verify the chemistry solutions", "check chemistry lab sheet safety".
---

# Chemie: review (Hessen)
Reviews only → fixes only when asked. Load `darshan-singh-meel-schule` (rubric, formats, grading, language) + `darshan-singh-meel-schule-chemie` (curriculum, notation, safety).

## Rules
- Independent → solve every task + balance every equation from task text alone before opening Lösung/Erwartungshorizont · never copy numbers or formulas from it.
- Evidence → file · task/line · quote · corrected text/equation/value.
- Severity per base `review.md` · chemistry Must in `references/checks.md` · `check:` line = Should ("verify with <page>"), never fact.
- Safety not certified → check block complete, consistent with `sicherheit.md`, honest about what was not looked up · never confirm a GHS classification from memory · report says it does not replace the Gefährdungsbeurteilung.
- Scope = one topic folder · curriculum facts from the chemistry skill's references, not memory.
- Privacy → no names quoted · no named student work.
- No rewrite until "fix".

## Process
1. Scope → folder (default every `.html` in `unterricht/chemie/<stufe>/<thema>/`) · level, GK/LK, Jahrgang, test type from files → ask only if unreadable.
2. Read base `review.md` · `bilingual.md` · `formate.md` · `bewertung.md` (if test) · chemistry `sek1.md`|`oberstufe.md` · `fachpraxis.md` · `sicherheit.md` (if handled/heated) · `references/checks.md`.
3. `python <base skill dir>/scripts/check_material.py <folder>` → FAIL = Must · `?` = check by hand → finding or false alarm.
4. Solve every task yourself → own equation + balance check (elements, charges, electrons) · own calculation (given, formula, result with unit + digits, second way or estimate) · own expected observation + interpretation → compare with Lösung, Erwartungshorizont, Erklärung, lesson plan, figure labels, animation captions → recompute every point sum, percentage, grade-key threshold.
5. `references/checks.md` C1-C12, file by file.
6. DE/EN pairs → 3-step test (`bilingual.md`) · terms vs `begriffe.md` · decimal comma/point · same formulas, numbers, units in both lines.
7. Animation → step forward + back · every speed · EN toggle · print preview · count atoms + charges per step (C10) → no browser: read `STEPS`, count from code, list under "Not checked".
8. Base checklist → areas 1-12 of `review.md`.
9. Report → `reviews/darshan-singh-meel-schule-chemie-review-<YYYY-MM-DD-HHMM>.md`, base format + sections "Nachgerechnet" (own · material's · match) and "Sicherheit: offen" (every classification, permission, disposal line the teacher must settle) → add `/reviews/` to `.gitignore` on first creation → reply: verdict · counts · report path · 3 key fixes.
10. Fixes on request only → Must first → re-run script → re-solve changed tasks → append "Nach Korrektur" + new verdict to same report.

## Reference
- `references/checks.md` · C1-C12 with "Must when", independent-solution table, frequent defects, verdict addition
