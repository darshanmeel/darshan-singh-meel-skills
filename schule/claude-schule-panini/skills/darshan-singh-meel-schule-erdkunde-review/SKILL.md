---
name: darshan-singh-meel-schule-erdkunde-review
description: Reviews Erdkunde / Geographie teaching material for Gymnasium in Hessen (Sek I and Oberstufe, GK/LK) - solves every task independently from the materials, recomputes every value (climate diagram, scale, rates, shares), checks maps and diagrams (legend, scale, north, source), data sources and years, KC/KCGO fit, operators and AFB, marking scheme, the German + closest-English lines and geography terms, animations, privacy and copyright - and writes a report with verdict and Must / Should / Other findings (what, why, fix) to reviews/. Reviews only; fixes when asked. Use after darshan-singh-meel-schule-erdkunde or on any existing Erdkunde material; load darshan-singh-meel-schule and darshan-singh-meel-schule-erdkunde alongside. Triggers - "Erdkunde prüfen", "Geographie-Arbeitsblatt prüfen", "Klausur Geographie gegenlesen", "Klimadiagramm prüfen", "Review Erdkunde"; "review my geography worksheet", "check this geography test", "check the climate diagram".
---

# Erdkunde / Geographie: review
Reviews `unterricht/erdkunde/<stufe>/<thema>/` (or named HTML). Base rubric `darshan-singh-meel-schule/references/review.md` (process, 12 areas, severity, report, verdict) + `references/checks.md`.

## Rules
- Review only; change files only if asked after the report.
- Solve every task from info box + material before opening `loesung.html`/`erwartungshorizont.html` → compare. Different result = finding.
- Recompute every number (sums, means, ranges, scale, rates, shares, dates); re-run climate diagrams with the skill script.
- Read figures as a student: every asked value readable at print size; check SVG coordinates vs values.
- Facts vs official sources (`references/sources.md` of subject skill); else "source not verifiable". Memory ≠ verified → `not checked`.
- Every finding: file · task/material id · quoted line. No praise, no summary.
- Privacy: never quote student data; "personal data in <file>, line <n>".

## Process
1. Scope: folder/files, default all `.html` in topic folder. Level from header; missing → one question.
2. Load base `review.md` + `bilingual.md` · level ref · `fachpraxis.md` · `begriffe.md` · `checks.md`.
3. `python <base skill dir>/scripts/check_material.py <folder>` → FAIL = Must, `?` = read by hand. Add printed numbers by hand (`checks.md` A8).
4. Solve all tasks without solution; keep a working list (not in report).
5. Recompute/re-read per `checks.md` A-D: numbers, climate re-run, map/diagram form, sources, years.
6. Compare with solution/Erwartungshorizont; worksheet, solution, test, Erklärung, animation must agree.
7. Walk base areas 1-12 + `checks.md` E-H (KC fit, wording, bilingual terms, animation).
8. Report → `reviews/darshan-singh-meel-schule-erdkunde-review-<YYYY-MM-DD-HHMM>.md` (add `/reviews/` to `.gitignore` first time). Finding = **what · why · fix**; bilingual findings add kind (`fehlt`, `zu frei`, `zu wörtlich`, `Fachbegriff`) + corrected EN line.
9. Reply: verdict · counts (Must/Should/Other, script errors/warnings) · report path (relative) · "Soll ich die Must-Punkte korrigieren?" Fix only on yes → re-run steps 3-6 for changed tasks → append "Nachprüfung".

## Severity (adds to base)
- Must:
  - value or printed points wrong, or files disagree
  - asked reading not possible from figure
  - real data without source; invented data unmarked
  - copied map, photo, cartoon, textbook figure
  - map without legend/scale when task measures or locates
  - LK content in GK; Oberstufe content in Sek I; nonexistent Themenfeld/code; KC ref in no file
  - deterministic/stereotyping statement as fact
- Should:
  - source line lacks period or retrieval year
  - scale level or year missing in a task
  - no north arrow but orientation clear
  - model without "Modell" or limit (from Jg. 9)
  - wording from `begriffe.md` avoid list
  - Raumbeispiel differs from plan
  - description and explanation mixed in solution

## References
- `references/checks.md` · every review: lists A-H, recompute facts, common defects
- base `references/review.md` · every review: rubric, severity, report, verdict
