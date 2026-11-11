---
name: darshan-singh-meel-schule-physik-review
description: Reviews physics teaching material for the Gymnasium in Hessen (Sek I and Oberstufe) - lesson plans, worksheets and solutions, tests and Klausuren with Erwartungshorizont, explanations, animations - against the shared school rubric plus physics checks - every task solved independently, units, significant figures, plausibility, GK/LK level, experiment safety, models, diagrams, animation physics, and the German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-schule-physik or on any existing physics material. Triggers - "Physik-Material prüfen", "Physik Arbeitsblatt prüfen", "Klausur Physik gegenlesen", "Erwartungshorizont prüfen", "Lösung nachrechnen", "Einheiten prüfen", "Versuch Sicherheit prüfen"; "review physics worksheet", "check my physics test", "check the marking scheme", "verify the solutions", "check units and significant figures".
---

# Physik: review (Hessen)

Load `darshan-singh-meel-schule` (rubric, formats, grading, language rule) and `darshan-singh-meel-schule-physik` (curriculum and conventions). This skill adds the physics checks and fixes the order of work. It reviews; it changes files only when the user asks for fixes.

## Rules
- **Independent.** Solve every task from the task text alone before opening Lösung or Erwartungshorizont. Never copy a number from the solution into your own calculation.
- **Evidence.** Every finding names file, task or line, quotes the wrong text and gives the corrected text or value. No finding from memory of "what such material usually contains".
- **Severity** as in base `review.md`; physics Must conditions in `references/checks.md`. A `check:` line of a reference is a Should ("verify with <page>"), never a fact.
- **Scope.** The files of one topic folder. Curriculum facts come from the physics skill's references, not from memory; KC wording is compared with `sek1.md` / `oberstufe.md`.
- **Privacy.** The report quotes no names; filled-in student work is not reviewed with names.
- **No rewrite.** Findings carry a concrete fix; the files stay as they are until the user says "fix".

## Process (fixed)
1. **Scope** - folder and files (default: every `.html` in `unterricht/physik/<stufe>/<thema>/`). Level, GK/LK, and type of test from the files; ask only if they cannot be read from them.
2. **Read** base `review.md`, `bilingual.md`, `formate.md`, and `bewertung.md` when a test is included; physics `sek1.md` or `oberstufe.md` for the level, `konventionen.md`, and `experimente.md` when an experiment occurs; `references/checks.md` of this skill.
3. **Scripts** - `python <base skill dir>/scripts/check_material.py <folder>` and `python <physics skill dir>/scripts/check_einheiten.py <folder>`. Each FAIL is a Must; each `?` is checked by hand and either becomes a finding or is noted as a false alarm.
4. **Solve every task yourself** - for each task and sub-task write: given values, formula, result with unit and digits, and a second way or an estimate. Then compare with Lösung, Erwartungshorizont, Erklärung, figure labels and animation captions. Recompute every sum of points, every percentage and every threshold of the grade key.
5. **Physics checks** - walk `references/checks.md` (P1-P12) file by file.
6. **Language pairs** - every DE/EN pair with the 3-step test of base `bilingual.md`; terms against physics `begriffe.md`; decimal comma/point; same numbers and units in both lines.
7. **Animation** - run `node --check` on the page's last `<script>` block (a caption with an unescaped apostrophe stops the player; the check scripts do not see it); step forwards and backwards through every step with the buttons and with ← → after a click on Weiter, screenshot every step (labels covered or cut off), play at each speed, toggle English, print preview; compare every position, value and caption with the worksheet numbers (`checks.md`, P10).
8. **Base checklist** - areas 1-12 of base `review.md`.
9. **Report** - write `reviews/darshan-singh-meel-schule-physik-review-<YYYY-MM-DD-HHMM>.md` in the base report format, with the extra section "Nachgerechnet" (table: task · own result · material's result · match). Add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, report path, the three most important fixes.
10. **Fixes** only on request: apply Must first, re-run both scripts, re-solve the changed tasks, append "Nach Korrektur" with the new verdict to the same report.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | physics checks P1-P12 with "Must when", the table for the independent solutions, frequent defects |
| `references/examples/review-beispiel.md` | one real report (Jg. 7 Geschwindigkeit + Q2 GK Federpendel) as a model for form and depth |
