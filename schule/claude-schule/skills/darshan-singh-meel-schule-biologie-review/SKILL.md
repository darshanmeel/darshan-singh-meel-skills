---
name: darshan-singh-meel-schule-biologie-review
description: Reviews Biologie teaching material for the Gymnasium in Hessen (Sek I and Oberstufe) - lesson plans, worksheets and solutions, tests and Klausuren with Erwartungshorizont, experiment sheets, explanations, animations - against the shared school rubric plus biology checks - every task solved independently, facts and numbers (chromosome counts, equations, crossing schemes, data) rechecked, system levels and causal wording, model versus reality, observation versus interpretation, GK/LK level, experiment safety block (RiSU rules for Biostoffe, animals, human samples), sensitive topics, animation steps, and the German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-schule-biologie or on any existing biology material. Triggers - "Biologie-Material prüfen", "Bio Arbeitsblatt prüfen", "Klausur Biologie gegenlesen", "Erwartungshorizont Biologie prüfen", "Bio-Lösung prüfen", "Bio-Versuch Sicherheit prüfen", "Stammbaum prüfen"; "review biology worksheet", "check my biology test", "check the biology marking scheme", "verify the biology solutions", "check biology lab sheet safety".
---

# Biologie: review (Hessen)

Load `darshan-singh-meel-schule` (rubric, formats, grading, language rule) and `darshan-singh-meel-schule-biologie` (curriculum, conventions, safety). This skill adds the biology checks and fixes the order of work. It reviews; it changes files only when the user asks for fixes.

## Rules
- **Independent.** Solve every task from the task text and material alone before opening Lösung or Erwartungshorizont. Never copy a number, a genotype or a label from the solution into your own work.
- **Evidence.** Every finding names file, task or line, quotes the wrong text and gives the corrected text or value.
- **Severity** as in base `review.md`; biology Must conditions in `references/checks.md`. A `check:` line of a reference is a Should ("verify with <page>"), never a fact.
- **Textbook-dependent values** (ATP yield, Ruhepotenzial, phase durations) are not errors when marked `ca.` and consistent across the files; a finding only when files disagree or the value is outside the usual range.
- **Safety is not certified.** The review checks that the safety block is complete and consistent with the biology skill's `fachpraxis.md`; it never replaces the Gefährdungsbeurteilung - the report says so.
- **Scope.** The files of one topic folder. Curriculum facts come from the biology skill's references, not from memory.
- **Privacy.** The report quotes no names; filled-in student work is not reviewed with names; pedigrees and cases must be invented.
- **No rewrite.** Findings carry a concrete fix; the files stay as they are until the user says "fix".

## Process (fixed)
1. **Scope** - folder and files (default: every `.html` in `unterricht/biologie/<stufe>/<thema>/`). Level, GK/LK, Jahrgang and type of test from the files; ask only if they cannot be read from them.
2. **Read** base `review.md`, `bilingual.md`, `formate.md`, and `bewertung.md` when a test is included; biology `sek1.md` or `oberstufe.md` for the level, `fachpraxis.md`; `references/checks.md` of this skill.
3. **Script** - `python <base skill dir>/scripts/check_material.py <folder>`. Each FAIL is a Must; each `?` is checked by hand and becomes a finding or is noted as a false alarm.
4. **Solve every task yourself** - per task: own answer in key points, own counts and calculations (chromosomes and chromatids, crossing ratios, codon translation, diagram readings, energy or population numbers) with a second way or an estimate, own expected observation. Then compare with Lösung, Erwartungshorizont, Erklärung, lesson plan, figure labels and animation captions. Recompute every sum of points, every percentage and every threshold of the grade key.
5. **Biology checks** - walk `references/checks.md` (B1-B12) file by file.
6. **Language pairs** - every DE/EN pair with the 3-step test of base `bilingual.md`; terms against biology `begriffe.md`; scientific names unchanged and italic in both lines; decimal comma/point.
7. **Animation** - step forwards and backwards through every step, play at each speed, toggle English, print preview; count structures in every step (`checks.md`, B10). No browser available → read `STEPS` and count from the code, and list the animation under "Not checked".
8. **Base checklist** - areas 1-12 of base `review.md`.
9. **Report** - write `reviews/darshan-singh-meel-schule-biologie-review-<YYYY-MM-DD-HHMM>.md` in the base report format, with the extra section "Nachgeprüft" (task · own answer or count · material's answer · match). Add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, report path, the three most important fixes.
10. **Fixes** only on request: apply Must first, re-run the script, re-solve the changed tasks, append "Nach Korrektur" with the new verdict to the same report.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | biology checks B1-B12 with "Must when", the table for the independent solutions, frequent defects, verdict addition |
