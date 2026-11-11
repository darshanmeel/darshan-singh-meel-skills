---
name: darshan-singh-meel-schule-psychologie-review
description: Review teaching material for Psychologie (Hessen, Oberstufe - Kerncurriculum berufliches Gymnasium, Schwerpunkt Erziehungswissenschaft, or a school-own course) - solves every task independently, checks curriculum fit (K1-K5 codes, Leitideen, Themenfelder E1-Q4), every study fact (year, sample, design, result, criticism, replication), models and their figures, wording about evidence (no "beweist", no cause from correlation), balance of paradigms, research ethics, safety (no diagnosis, no self-disclosure, clinical topics, classroom experiments), statistics, the German lines and their English lines, animations, and writes a report with verdict and Must / Should / Other findings to reviews/. Use with darshan-singh-meel-schule and darshan-singh-meel-schule-psychologie. Triggers - "Psychologie-Material prüfen", "Arbeitsblatt Psychologie überprüfen", "Klausur Psychologie gegenlesen", "Erwartungshorizont prüfen", "Studie richtig dargestellt", "ist das ethisch vertretbar", "Review Psychologie"; "review my psychology worksheet", "check the psychology test", "is the study described correctly", "check the memory model animation", "ethics check for a class experiment".
---

# Review: Psychologie

Reviews; does not rewrite. Fixes only when the user asks, then re-runs the checks.

## Load
1. `darshan-singh-meel-schule`: `references/review.md` (process, 12-area checklist, severity, report format, verdict), `references/bilingual.md`, `references/operatoren.md`, `references/bewertung.md` for tests.
2. `darshan-singh-meel-schule-psychologie`: `kcbg.md`, `fachregeln.md`, `studien.md` when a study appears, `modelle-animationen.md` when a model appears, `begriffe.md`.
3. `references/checks.md` of this skill.

## Process (fixed)
1. **Scope** - files to review (default: every `.html` in the topic folder). One question only if the Kurshalbjahr or the course type (berufliches Gymnasium · school-own course) cannot be read from the files.
2. **Check script** - `python <base skill dir>/scripts/check_material.py <folder>`. Every FAIL = Must. Every `?` line is checked by hand.
3. **Solve first** - work every task from the material alone, before opening `loesung.html` or `erwartungshorizont.html`. Write down the result and the explanatory chain; for case tasks the matching of terms to the case; recompute every number (percentages with their base, means, point totals, grade key).
4. **Compare** with the solution: differences are findings (wrong solution, ambiguous task, missing alternative, points not awardable).
5. **Fact check** - every study and model statement in every file against `studien.md` and `modelle-animationen.md`, row by row. A fact not covered there: verify in the primary publication if network use is allowed; otherwise list under "Not checked".
6. **Subject checks** - walk `references/checks.md` (Y1-Y10).
7. **Base checklist** areas 1-12; **DE/EN pairs** with the 3-step test, subject terms against `begriffe.md`.
8. **Animation** - step through forwards and backwards; captions against the picture; order of stores and arrows; end state against the solution.
9. **Report** - `reviews/darshan-singh-meel-schule-psychologie-review-<YYYY-MM-DD-HHMM>.md` in the base report format; add `/reviews/` to `.gitignore` on first use. Reply: verdict, counts, report path (relative), the three most important findings.

## Severity (subject additions to the base table)
| Finding | Level |
|---|---|
| Wrong study fact (year, n, design, result, who took part) or a result without its base that changes the answer | Must |
| Wrong model (order of stores, direction of an arrow, term swapped, NS/CS, reinforcement/punishment) | Must |
| `beweist`, cause read from a correlation, significance explained as effect size or certainty | Must |
| Task above the Grundkurs statistics limit (significance test, Standardabweichung, r or p computed) | Must |
| Task asks for self-diagnosis, diagnosis of classmates or real persons, or personal disclosure; real diagnostic test administered | Must |
| Classroom experiment with embarrassing deception, stress or pressure; re-enactment of Milgram or a prison role play | Must |
| Clinical content with stigma wording, method details of self-harm, or treatment advice | Must |
| Case not marked as invented, or recognisably a real person | Must |
| Study presented without any criticism or replication status; ethics part missing in a study task; one paradigm presented as the true one | Should |
| Contested theory (Freud, Maslow, stage models) not labelled; capacity or duration figure without "etwa" or study | Should |
| `check:` items of the references that the material relies on | Should |
| Stronger study or case available, clearer figure | Other |

## Report additions
- Section "Unabhängig gelöst / Solved independently": one line per task - own result · solution's result · `gleich` or the difference.
- Section "Studien und Modelle / Studies and models": each study or model fact in the material - statement · row in `studien.md` or `modelle-animationen.md` · `stimmt` / difference / `nicht prüfbar`.
- Study facts in the subject skill are not verified against primary publications: an exact figure a graded task depends on is reported as Should ("verify in <publication>") even when it matches the reference row.
