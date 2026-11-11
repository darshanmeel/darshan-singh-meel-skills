---
name: darshan-singh-meel-schule-mathe-review
description: Reviews mathematics teaching material for Hessen (Grundschule Jg. 1-4, Gymnasium Sek I and Oberstufe GK/LK) - lesson plans, worksheets and solutions, Klassenarbeiten and Klausuren with Erwartungshorizont, explanations, animations - against the shared school rubric plus maths checks - every task solved independently, solvability, numbers and content fit for the level, notation, GK/LK, calculator rules, figures to scale, animation geometry, points and grade key, German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-schule-mathe or on any existing maths material. Triggers - "Mathe-Material prüfen", "Mathe Arbeitsblatt prüfen", "Mathearbeit gegenlesen", "Klausur Mathe prüfen", "Lösungen nachrechnen", "Erwartungshorizont prüfen", "Punkteverteilung prüfen"; "review maths worksheet", "check my math test", "verify the solutions", "check the marking scheme", "recalculate the answers".
---

# Mathematik: review (Hessen)

Load `darshan-singh-meel-schule` (rubric, formats, grading, language rule) and `darshan-singh-meel-schule-mathe` (curriculum, conventions, terms, check script). This skill adds the maths checks and fixes the order of work. It reviews; it changes files only when the user asks for fixes.

## Rules
- **Independent.** Solve every task from the task text alone before opening Lösung or Erwartungshorizont. Never copy a number, a step or a `data-check` expression from the material into your own calculation; compute with your own script or by hand, by a way of your choice.
- **Evidence.** Every finding names file and task or line, quotes the wrong text and gives the corrected text or value. No finding from memory of "what such material usually contains".
- **Severity** as in base `review.md`; maths Must conditions in `references/checks.md`. A `check:` line of a reference is a Should ("verify with <page>"), never a fact.
- **Curriculum facts** come from the maths skill's references (`grundschule.md`, `sek1.md`, `oberstufe.md`), not from memory. School decisions (calculation method, calculator, grade key) that the files do not state are listed under "Not checked", not judged. Exception: Sek I content of a later double year is a Must (M1) unless the material states that the school's curriculum places it earlier.
- **Privacy.** The report quotes no names; filled-in student work is not reviewed with names.
- **No rewrite.** Findings carry a concrete fix; the files stay as they are until the user says "fix".

## Process (fixed)
1. **Scope** - folder and files (default: every `.html` in `unterricht/mathematik/<stufe>/<thema>/`). Level, GK/LK, type of test and aids are read from the files; ask only if they cannot be read.
2. **Read** base `review.md`, `bilingual.md`, `formate.md`, and `bewertung.md` when a test is included; maths reference of the level, `konventionen.md`, `begriffe.md`, `animationen.md` when an animation is included; `references/checks.md` of this skill.
3. **Scripts** - `python <base skill dir>/scripts/check_material.py <folder>` (one topic folder per run) and `python <maths skill dir>/scripts/check_rechnung.py <folder>` (searches subfolders; also sub-points, AFB shares, grade key, test against Erwartungshorizont). Each FAIL is a Must; each `?` is checked by hand and becomes a finding or is noted as a false alarm. A passing `data-check` proves only that the material agrees with itself - it does not replace step 4.
4. **Solve every task yourself** - for each task and sub-task: data, own way, result (exact and rounded), second way or estimate. For "find all" tasks: enumerate or prove the full solution set. Then compare with Lösung, Erwartungshorizont, Erklärung, figure labels and animation captions - result, every printed intermediate step, unit, rounding. Check that at least one `data-check` per task tests the final answer against the given data. Recompute the sub-points of every part, every sum of points, every percentage and every threshold of the grade key.
5. **Maths checks** - walk `references/checks.md` (M1-M13) file by file.
6. **Language pairs** - every DE/EN pair with the 3-step test of base `bilingual.md`; terms against maths `begriffe.md`; decimal comma in German lines and formula-only lines, point in English sentences incl. formulas inside them; otherwise same numbers, units and formulas in both lines; operator pair from base `operatoren.md`.
7. **Figures and animation** - recompute at least three coordinates of every figure from its stated scale. In a headless browser (Playwright for Python with Chromium or the installed Chrome; a short script of your own, local files only): no external request, no JS error; step forwards and backwards through the animation, play at each speed, toggle English, print preview; compare every part, value and caption with the worksheet numbers (`checks.md`, M9-M10).
8. **Print** - PDF of every file from the same headless browser (`page.pdf`, A4) or `chrome --headless --print-to-pdf`: page count, no task or formula split, squared fields large enough for the model solution, sum row and grade key in one piece. "Not checked" for steps 7-8 only when no browser can be started; say which was tried.
9. **Base checklist** - areas 1-12 of base `review.md`.
10. **Report** - write `reviews/darshan-singh-meel-schule-mathe-review-<YYYY-MM-DD-HHMM>.md` in the base report format, with the extra section "Nachgerechnet" (table from `checks.md`). Add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, report path, the three most important fixes.
11. **Fixes** only on request: apply Must first, re-run both scripts, re-solve the changed tasks, append "Nach Korrektur" with the new verdict to the same report.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | maths checks M1-M13 with "Must when", the table for the independent solutions, frequent defects, verdict rule |
| `references/examples/review-beispiel.md` | one real report (three levels: Jg. 3, Jg. 6, Q1 GK) as a model for form and depth |
