---
name: darshan-singh-meel-schule-chemie-review
description: Reviews Chemie teaching material for the Gymnasium in Hessen (Sek I and Oberstufe) - lesson plans, worksheets and solutions, tests and Klausuren with Erwartungshorizont, experiment sheets, explanations, animations - against the shared school rubric plus chemistry checks - every task solved and every equation balanced independently (atoms, charges, electrons), calculations redone with units, Stoffebene and Teilchenebene kept apart, GK/LK level, safety block (GHS source, student restrictions by Jahrgang, disposal), expected observations, particle counts in animations, and the German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-schule-chemie or on any existing chemistry material. Triggers - "Chemie-Material prüfen", "Chemie Arbeitsblatt prüfen", "Klausur Chemie gegenlesen", "Erwartungshorizont Chemie prüfen", "Reaktionsgleichungen prüfen", "Chemie-Lösung nachrechnen", "Chemie-Versuch Sicherheit prüfen", "Gefährdungsbeurteilung gegenlesen"; "review chemistry worksheet", "check my chemistry test", "check the chemical equations", "verify the chemistry solutions", "check chemistry lab sheet safety".
---

# Chemie: review (Hessen)

Load `darshan-singh-meel-schule` (rubric, formats, grading, language rule) and `darshan-singh-meel-schule-chemie` (curriculum, notation, safety). This skill adds the chemistry checks and fixes the order of work. It reviews; it changes files only when the user asks for fixes.

## Rules
- **Independent.** Solve every task and balance every equation from the task text alone before opening Lösung or Erwartungshorizont. Never copy a number or a formula from the solution into your own work.
- **Evidence.** Every finding names file, task or line, quotes the wrong text and gives the corrected text, equation or value.
- **Severity** as in base `review.md`; chemistry Must conditions in `references/checks.md`. A `check:` line of a reference is a Should ("verify with <page>"), never a fact.
- **Safety is not certified.** The review checks that the safety block is complete, consistent with the chemistry skill's `sicherheit.md` and honest about what was not looked up. It never confirms a GHS classification from memory and never replaces the Gefährdungsbeurteilung - the report says so.
- **Scope.** The files of one topic folder. Curriculum facts come from the chemistry skill's references, not from memory.
- **Privacy.** The report quotes no names; filled-in student work is not reviewed with names.
- **No rewrite.** Findings carry a concrete fix; the files stay as they are until the user says "fix".

## Process (fixed)
1. **Scope** - folder and files (default: every `.html` in `unterricht/chemie/<stufe>/<thema>/`). Level, GK/LK, Jahrgang and type of test from the files; ask only if they cannot be read from them.
2. **Read** base `review.md`, `bilingual.md`, `formate.md`, and `bewertung.md` when a test is included; chemistry `sek1.md` or `oberstufe.md` for the level, `fachpraxis.md`, and `sicherheit.md` when anything is handled or heated; `references/checks.md` of this skill.
3. **Script** - `python <base skill dir>/scripts/check_material.py <folder>`. Each FAIL is a Must; each `?` is checked by hand and becomes a finding or is noted as a false alarm.
4. **Solve every task yourself** - per task: own equation with the balance check (elements, charges, electrons), own calculation (given, formula, result with unit and digits, second way or estimate), own expected observation and interpretation. Then compare with Lösung, Erwartungshorizont, Erklärung, lesson plan, figure labels and animation captions. Recompute every sum of points, every percentage and every threshold of the grade key.
5. **Chemistry checks** - walk `references/checks.md` (C1-C12) file by file.
6. **Language pairs** - every DE/EN pair with the 3-step test of base `bilingual.md`; terms against chemistry `begriffe.md`; decimal comma/point; same formulas, numbers and units in both lines.
7. **Animation** - step forwards and backwards through every step, play at each speed, toggle English, print preview; count atoms and charges in every step (`checks.md`, C10). No browser available → read `STEPS` and count from the code, and list the animation under "Not checked".
8. **Base checklist** - areas 1-12 of base `review.md`.
9. **Report** - write `reviews/darshan-singh-meel-schule-chemie-review-<YYYY-MM-DD-HHMM>.md` in the base report format, with the extra sections "Nachgerechnet" (equations and calculations: own result · material's result · match) and "Sicherheit: offen" (every classification, permission or disposal line that the teacher must still settle). Add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, report path, the three most important fixes.
10. **Fixes** only on request: apply Must first, re-run the script, re-solve the changed tasks, append "Nach Korrektur" with the new verdict to the same report.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | chemistry checks C1-C12 with "Must when", the table for the independent solutions, frequent defects, verdict addition |
