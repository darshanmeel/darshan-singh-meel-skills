---
name: darshan-singh-meel-schule-biologie-review
description: Reviews Biologie teaching material for the Gymnasium in Hessen (Sek I and Oberstufe) - lesson plans, worksheets and solutions, tests and Klausuren with Erwartungshorizont, experiment sheets, explanations, animations - against the shared school rubric plus biology checks - every task solved independently, facts and numbers (chromosome counts, equations, crossing schemes, data) rechecked, system levels and causal wording, model versus reality, observation versus interpretation, GK/LK level, experiment safety block (RiSU rules for Biostoffe, animals, human samples), sensitive topics, animation steps, and the German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-schule-biologie or on any existing biology material. Triggers - "Biologie-Material prüfen", "Bio Arbeitsblatt prüfen", "Klausur Biologie gegenlesen", "Erwartungshorizont Biologie prüfen", "Bio-Lösung prüfen", "Bio-Versuch Sicherheit prüfen", "Stammbaum prüfen"; "review biology worksheet", "check my biology test", "check the biology marking scheme", "verify the biology solutions", "check biology lab sheet safety".
---

# Biologie: review (Hessen)
Reviews only → fixes only when asked. Load `darshan-singh-meel-schule` (rubric, formats, grading, language) + `darshan-singh-meel-schule-biologie` (curriculum, conventions, safety).

## Rules
- Independent → solve every task from task text + material before opening Lösung/Erwartungshorizont · never copy numbers, genotypes, labels from it.
- Evidence → file · task/line · quote · corrected text/value.
- Severity per base `review.md` · biology Must in `references/checks.md` · `check:` line = Should ("verify with <page>"), never fact.
- Textbook-dependent values (ATP yield, Ruhepotenzial, phase durations) → OK if marked `ca.` and consistent · finding only if files disagree or outside usual range.
- Safety not certified → check block complete + consistent with `fachpraxis.md` · report says it does not replace the Gefährdungsbeurteilung.
- Scope = one topic folder · curriculum facts from the biology skill's references, not memory.
- Privacy → no names quoted · no named student work · pedigrees/cases invented.
- No rewrite until "fix".

## Process
1. Scope → folder (default every `.html` in `unterricht/biologie/<stufe>/<thema>/`) · level, GK/LK, Jahrgang, test type from files → ask only if unreadable.
2. Read base `review.md` · `bilingual.md` · `formate.md` · `bewertung.md` (if test) · biology `sek1.md`|`oberstufe.md` · `fachpraxis.md` · `references/checks.md`.
3. `python <base skill dir>/scripts/check_material.py <folder>` → FAIL = Must · `?` = check by hand → finding or false alarm.
4. Solve every task yourself → key-point answer · own counts/calculations (chromosomes vs chromatids, crossing ratios, codons, diagram readings, energy/population numbers) with a second way or estimate · expected observation → compare with Lösung, Erwartungshorizont, Erklärung, lesson plan, figure labels, animation captions → recompute every point sum, percentage, grade-key threshold.
5. `references/checks.md` B1-B12, file by file.
6. DE/EN pairs → 3-step test (`bilingual.md`) · terms vs `begriffe.md` · scientific names unchanged + italic in both lines · decimal comma/point.
7. Animation → step forward + back · every speed · EN toggle · print preview · count structures per step (B10) → no browser: read `STEPS`, count from code, list under "Not checked".
8. Base checklist → areas 1-12 of `review.md` (6 incl. author voice: no chat · request · requester in material).
9. Report → `reviews/darshan-singh-meel-schule-biologie-review-<YYYY-MM-DD-HHMM>.md`, base format + section "Nachgeprüft" (task · own answer/count · material's · match) → add `/reviews/` to `.gitignore` on first creation → reply: verdict · counts · report path · 3 key fixes.
10. Fixes on request only → Must first → re-run script → re-solve changed tasks → append "Nach Korrektur" + new verdict to same report.

## Reference
- `references/checks.md` · B1-B12 with "Must when", independent-solution table, frequent defects, verdict addition
