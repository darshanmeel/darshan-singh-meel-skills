---
name: darshan-singh-meel-schule-geschichte-review
description: Reviews Geschichte teaching material for Gymnasium in Hessen (Sek I and Oberstufe, GK/LK) - solves every task independently, checks every date, name, number and quotation against the cited or an official source, source labels and citations, Sachurteil and Werturteil criteria, perspectives, loaded terms and sensitive topics, timelines and animations, KC/KCGO fit, operators and AFB, marking scheme, the German + closest-English lines and history terms, privacy and copyright - and writes a report with verdict and Must / Should / Other findings (what, why, fix) to reviews/. Reviews only; fixes when asked. Use after darshan-singh-meel-schule-geschichte or on any existing Geschichte material; load darshan-singh-meel-schule and darshan-singh-meel-schule-geschichte alongside. Triggers - "Geschichte prüfen", "Klausur Geschichte gegenlesen", "Quellenanalyse prüfen", "Zeitleiste prüfen", "Review Geschichte"; "review my history worksheet", "fact-check the dates".
---

# Geschichte: review
Reviews `unterricht/geschichte/<stufe>/<thema>/` (or named HTML). Base rubric `darshan-singh-meel-schule/references/review.md` (process, 12 areas, severity, report, verdict) + `references/checks.md`.

## Rules
- Review only; change files only if asked after the report.
- Solve every task from info box + material before opening `loesung.html`/`erwartungshorizont.html`: own summary, context, comparison grid, judgement with criteria → compare. Open tasks: printed criteria must admit your reasoned answer.
- Every fact checked or `Not checked`: list all dates, names, offices, numbers, quotations; check vs cited source, then one more official/scholarly public page (`references/sources.md` of subject skill). Never "correct" from memory. `checks.md` anchor dates = plausibility test only.
- Check the verb with a date: beschlossen · unterzeichnet · verkündet · in Kraft · aufgehoben. Pages differ → finding with both dates + safer wording.
- Quotations word for word vs cited edition: wording · paragraph · marked cuts · spelling statement. Meaning-changing cut = Must.
- Judgement fairness: scheme rewarding one opinion, or Werturteil asked without naming it = finding.
- Every finding: file · task/material id · quoted line. No praise, no summary.
- Privacy: never quote student data.

## Process
1. Scope: folder/files, default all `.html` in topic folder. Level from header; missing → one question.
2. Load base `review.md` + `bilingual.md` · level ref · `quellenarbeit.md` · `begriffe.md` · `checks.md`.
3. `python <base skill dir>/scripts/check_material.py <folder>` → FAIL = Must, `?` = read by hand (German source without `data-nur-de` shows here). Add printed numbers by hand (`checks.md` A10).
4. Solve all tasks without solution; keep a working list (not in report).
5. Fact list from all files → check per rules (`checks.md` A, B). Re-run `zeitleiste.py` with a timeline's dates → compare x positions (`checks.md` D).
6. Compare with solution/Erwartungshorizont; worksheet, solution, test, Erklärung, animation must agree.
7. Walk base areas 1-12 + `checks.md` C, E-H (source work, KC fit, wording/sensitive topics, bilingual terms, animation).
8. Report → `reviews/darshan-singh-meel-schule-geschichte-review-<YYYY-MM-DD-HHMM>.md` (add `/reviews/` to `.gitignore` first time). Finding = **what · why · fix**; bilingual findings add kind (`fehlt`, `zu frei`, `zu wörtlich`, `Fachbegriff`) + corrected EN line.
9. Reply: verdict · counts (Must/Should/Other, script errors/warnings) · report path (relative) · "Soll ich die Must-Punkte korrigieren?" Fix only on yes → re-run steps 3-6 for changed parts → append "Nachprüfung".

## Severity (adds to base)
- Must:
  - wrong date, name, office, number, attribution; files disagree on a date
  - quotation differs from cited text; unmarked or meaning-changing cut
  - invented text as source; invented quotation of a real person
  - Darstellung labelled Quelle or reverse
  - copied textbook/Abitur text, press photo, modern cartoon
  - EN translation printed for a source to analyse in German
  - loaded term as own description unmarked; stereotype/perpetrator view as fact
  - role play/empathy task with victims or perpetrators of mass crimes; forbidden symbols in figure
  - scheme rewards one opinion; judgement task without criteria in Erwartungshorizont; printed points/sums disagree
  - timeline not to scale without marked break; animation date ≠ worksheet
  - LK content in GK; Oberstufe standard in Sek I; nonexistent Themenfeld/code; KC ref in no file
- Should:
  - date right but marked act unclear
  - spelling statement missing
  - source lacks Adressat/place where task asks
  - one perspective on contested topic
  - word list for hard source words missing
  - present-day comparison without criteria
  - epoch/label without construct hint (from Jg. 9)
  - single-cause wording in info box
  - Sach-/Werturteil not named in task
  - >8 events on one axis
  - Leitfrage not answered by last task

## References
- `references/checks.md` · every review: lists A-H, anchor dates, common defects
- base `references/review.md` · every review: rubric, severity, report, verdict
