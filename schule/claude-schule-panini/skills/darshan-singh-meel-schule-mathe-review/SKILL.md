---
name: darshan-singh-meel-schule-mathe-review
description: Reviews mathematics teaching material for Hessen (Grundschule Jg. 1-4, Gymnasium Sek I and Oberstufe GK/LK) - lesson plans, worksheets and solutions, Klassenarbeiten and Klausuren with Erwartungshorizont, explanations, animations - against the shared school rubric plus maths checks - every task solved independently, solvability, numbers and content fit for the level, notation, GK/LK, calculator rules, figures to scale, animation geometry, points and grade key, German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-schule-mathe or on any existing maths material. Triggers - "Mathe-Material prüfen", "Mathe Arbeitsblatt prüfen", "Mathearbeit gegenlesen", "Klausur Mathe prüfen", "Lösungen nachrechnen", "Erwartungshorizont prüfen", "Punkteverteilung prüfen"; "review maths worksheet", "check my math test", "verify the solutions", "check the marking scheme", "recalculate the answers".
---

# Mathematik: review (Hessen)
Load `darshan-singh-meel-schule` (rubric, formats, grading, language rule) + `darshan-singh-meel-schule-mathe` (curriculum, conventions, terms, check script). Reviews only; edits files only on request.

## Rules
- Independent: solve every task from the task text alone before opening Lösung/Erwartungshorizont · never copy a number, step or `data-check` from the material · own script or by hand, own way.
- Evidence: each finding → file + task/line · quote the wrong text · give corrected text/value · nothing from "what such material usually has".
- Severity as base `review.md`; maths Must conditions → `references/checks.md`. A reference `check:` line = Should ("verify with <page>"), never fact.
- Curriculum facts from maths references only (`grundschule.md` · `sek1.md` · `oberstufe.md`), not memory. Unstated school decisions (method, calculator, grade key) → "Not checked", not judged. Exception: Sek I content of a later double year = Must (M1) unless the material states the school's curriculum places it earlier.
- Privacy: no names in report; no filled-in student work with names.
- No rewrite: findings carry a concrete fix; files unchanged until "fix".

## Process
1. Scope → folder/files (default: every `.html` in `unterricht/mathematik/<stufe>/<thema>/`) · level, GK/LK, test type, aids read from files; ask only if unreadable.
2. Read → base `review.md` · `bilingual.md` · `formate.md` · `bewertung.md` (test included) · level maths reference · `konventionen.md` · `begriffe.md` · `animationen.md` (animation included) · `references/checks.md`.
3. Scripts → `python <base skill dir>/scripts/check_material.py <folder>` (one topic folder per run) · `python <maths skill dir>/scripts/check_rechnung.py <folder>` (subfolders; sub-points, AFB, grade key, test vs Erwartungshorizont). FAIL = Must · `?` = check by hand → finding or false alarm. Pass proves self-consistency only, never replaces step 4.
4. Solve every task and sub-task yourself → data · own way · result (exact + rounded) · second way or estimate; "find all" → enumerate or prove full set. Compare with Lösung, Erwartungshorizont, Erklärung, figure labels, animation captions: result · every printed step · unit · rounding. ≥1 `data-check` per task tests the answer against the given data. Recompute sub-points, point sums, percentages, grade-key thresholds.
5. Maths checks → `references/checks.md` M1-M13, file by file.
6. Language pairs → every DE/EN pair with the 3-step test of base `bilingual.md` · terms vs `begriffe.md` · comma in German and formula-only lines, point in English sentences incl. their formulas · otherwise same numbers, units, formulas · operator pair per base `operatoren.md`.
7. Figures + animation → recompute ≥3 coordinates per figure from stated scale · headless browser (Playwright Python with Chromium/installed Chrome; own short script, local files only): no external request, no JS error · step forward/back, each speed, English toggle, print preview · compare parts, values, captions with worksheet numbers (M9-M10).
8. Print → PDF per file via same browser (`page.pdf`, A4) or `chrome --headless --print-to-pdf` → page count · no split task/formula · answer squares fit model solution · sum row + grade key whole. "Not checked" for 7-8 only if no browser starts; say which was tried.
9. Base checklist → areas 1-12 of base `review.md`.
10. Report → `reviews/darshan-singh-meel-schule-mathe-review-<YYYY-MM-DD-HHMM>.md` in base report format + section "Nachgerechnet" (table from `checks.md`) · first creation of `reviews/` → add `/reviews/` to `.gitignore` · reply: verdict · counts · report path · top 3 fixes.
11. Fixes (only on request) → Must first · rerun both scripts · re-solve changed tasks · append "Nach Korrektur" with new verdict to the same report.

## References
- `references/checks.md` · M1-M13 with "Must when", independent-solution table, frequent defects, verdict rule
- `references/examples/review-beispiel.md` · one real report (Jg. 3, Jg. 6, Q1 GK): form and depth model
