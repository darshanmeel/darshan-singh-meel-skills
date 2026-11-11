---
name: darshan-singh-meel-schule-psychologie-review
description: Review teaching material for Psychologie (Hessen, Oberstufe - Kerncurriculum berufliches Gymnasium, Schwerpunkt Erziehungswissenschaft, or a school-own course) - solves every task independently, checks curriculum fit (K1-K5 codes, Leitideen, Themenfelder E1-Q4), every study fact (year, sample, design, result, criticism, replication), models and their figures, wording about evidence (no "beweist", no cause from correlation), balance of paradigms, research ethics, safety (no diagnosis, no self-disclosure, clinical topics, classroom experiments), statistics, the German lines and their English lines, animations, and writes a report with verdict and Must / Should / Other findings to reviews/. Use with darshan-singh-meel-schule and darshan-singh-meel-schule-psychologie. Triggers - "Psychologie-Material prüfen", "Arbeitsblatt Psychologie überprüfen", "Klausur Psychologie gegenlesen", "Erwartungshorizont prüfen", "Studie richtig dargestellt", "ist das ethisch vertretbar", "Review Psychologie"; "review my psychology worksheet", "check the psychology test", "is the study described correctly", "check the memory model animation", "ethics check for a class experiment".
---

# Review: Psychologie
Reviews, never rewrites → fixes only on ask, then re-run checks.

## Load
- `darshan-singh-meel-schule`: `references/review.md` (process, 12-area checklist, severity, report, verdict) · `bilingual.md` · `operatoren.md` · `bewertung.md` (tests).
- `darshan-singh-meel-schule-psychologie`: `kcbg.md` · `fachregeln.md` · `studien.md` (study) · `modelle-animationen.md` (model) · `begriffe.md`.
- This skill: `references/checks.md`.

## Process
1. Scope → files (default every `.html` in topic folder) · ask only if Kurshalbjahr or course type (berufliches Gymnasium · school-own) unreadable from files.
2. `python <base skill dir>/scripts/check_material.py <folder>` → every FAIL = Must · every `?` by hand.
3. Solve first → every task from material alone, before opening `loesung.html` / `erwartungshorizont.html` · note result + explanatory chain · case tasks: term-to-case matching · recompute numbers (% with base, means, point totals, grade key).
4. Compare with solution → differences = findings (wrong solution · ambiguous task · missing alternative · points not awardable).
5. Fact check → every study + model statement in every file vs `studien.md` / `modelle-animationen.md`, row by row · not covered → verify in primary publication if network allowed, else "Not checked".
6. Subject checks → `references/checks.md` Y1-Y10.
7. Base checklist areas 1-12 · DE/EN pairs (3-step test) · terms vs `begriffe.md`.
8. Animation → step forwards + backwards · captions vs picture · store order + arrows · end state vs solution.
9. Report → `reviews/darshan-singh-meel-schule-psychologie-review-<YYYY-MM-DD-HHMM>.md` (base format) · first use → add `/reviews/` to `.gitignore` · reply: verdict · counts · report path (relative) · 3 top findings.

## Severity (adds to base table)
- Must → wrong study fact (year, n, design, result, participants), or result without base that changes the answer · wrong model (store order, arrow direction, swapped term, NS/CS, reinforcement/punishment) · `beweist`, cause from correlation, significance read as effect size/certainty · task above Grundkurs statistics (significance test, Standardabweichung, r/p computed) · task asks self-diagnosis, diagnosis of classmates/real persons, personal disclosure, or real diagnostic test administered · classroom experiment with embarrassing deception, stress, pressure, Milgram re-enactment, prison role play · clinical content with stigma wording, self-harm method details, treatment advice · case not marked invented or recognisably real.
- Should → study without criticism or replication status · ethics part missing in study task · one paradigm presented as true · contested theory unlabelled · capacity/duration figure without "etwa" or study · `check:` items the material relies on.
- Other → stronger study/case · clearer figure.

## Report additions
- "Unabhängig gelöst / Solved independently" → per task: own result · solution's result · `gleich` or difference.
- "Studien und Modelle / Studies and models" → per fact: statement · row in `studien.md` / `modelle-animationen.md` · `stimmt` / difference / `nicht prüfbar`.
- Subject-skill study facts are unverified against primary publications → exact figure a graded task depends on = Should ("verify in <publication>") even if it matches the reference row.
