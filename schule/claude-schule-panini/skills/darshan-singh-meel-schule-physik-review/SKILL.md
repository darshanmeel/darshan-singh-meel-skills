---
name: darshan-singh-meel-schule-physik-review
description: Reviews physics teaching material for the Gymnasium in Hessen (Sek I and Oberstufe) - lesson plans, worksheets and solutions, tests and Klausuren with Erwartungshorizont, explanations, animations - against the shared school rubric plus physics checks - every task solved independently, units, significant figures, plausibility, GK/LK level, experiment safety, models, diagrams, animation physics, and the German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-schule-physik or on any existing physics material. Triggers - "Physik-Material prüfen", "Physik Arbeitsblatt prüfen", "Klausur Physik gegenlesen", "Erwartungshorizont prüfen", "Lösung nachrechnen", "Einheiten prüfen", "Versuch Sicherheit prüfen"; "review physics worksheet", "check my physics test", "check the marking scheme", "verify the solutions", "check units and significant figures".
---


# Physik review (Hessen)
Load `darshan-singh-meel-schule` (rubric, formats, grading, language) + `darshan-singh-meel-schule-physik` (curriculum, conventions). Reviews only · edits files only on "fix".

## Rules
- Independent: solve every task from task text alone before opening Lösung/EH · never copy a number from the solution.
- Evidence: file + task/line · quote wrong text · give corrected text/value · nothing from memory of "what such material contains".
- Severity: base `review.md` · physics Must conditions → `references/checks.md` · `check:` line = Should ("verify with <page>"), never fact.
- Scope: files of one topic folder · curriculum facts from physics references (`sek1.md`/`oberstufe.md`), not memory.
- Privacy: no names in report · no filled-in student work with names.
- No rewrite: every finding carries a concrete fix.

## Process
1. Scope: folder/files (default every `.html` in `unterricht/physik/<stufe>/<thema>/`) · level, GK/LK, test type from files · ask only if unreadable.
2. Read: base `review.md` · `bilingual.md` · `formate.md` · `bewertung.md` (if test) · physics `sek1.md` | `oberstufe.md` · `konventionen.md` · `experimente.md` (if experiment) · `references/checks.md`.
3. Scripts: `python <base skill dir>/scripts/check_material.py <folder>` + `python <physics skill dir>/scripts/check_einheiten.py <folder>` → FAIL = Must · `?` = by hand: finding or noted false alarm.
4. Solve every task and sub-task: given · formula · result with unit and digits · second way or estimate → compare with Lösung, EH, Erklärung, figure labels, animation captions · recompute every point sum, percentage, key threshold.
5. Walk `checks.md` P1-P12 file by file.
6. Language pairs: base `bilingual.md` 3-step test · terms vs `begriffe.md` · comma/point · same numbers and units.
7. Animation: `node --check` on last `<script>` block (unescaped apostrophe in caption stops player; scripts miss it) · steps forward/back with buttons and ← → after click on Weiter · screenshot every step (labels covered/cut) · each speed · English toggle · print preview · positions, values, captions vs worksheet numbers (P10).
8. Base checklist areas 1-12 of `review.md` (6 incl. author voice: no chat · request · requester in material).
9. Report `reviews/darshan-singh-meel-schule-physik-review-<YYYY-MM-DD-HHMM>.md`: base format + section "Nachgerechnet" (task · own result · material's result · match) · add `/reviews/` to `.gitignore` on first creation · reply: verdict · counts · path · 3 top fixes.
10. Fixes only on request: Must first → re-run both scripts → re-solve changed tasks → append "Nach Korrektur" + new verdict to same report.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | P1-P12 + "Must when" · independent-solution table · frequent defects |
| `references/examples/review-beispiel.md` | real report (Jg. 7 Geschwindigkeit + Q2 GK Federpendel) as model |
