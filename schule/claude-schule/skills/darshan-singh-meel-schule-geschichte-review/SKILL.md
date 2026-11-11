---
name: darshan-singh-meel-schule-geschichte-review
description: Reviews Geschichte teaching material for Gymnasium in Hessen (Sek I and Oberstufe, GK/LK) - solves every task independently, checks every date, name, number and quotation against the cited or an official source, source labels and citations, Sachurteil and Werturteil criteria, perspectives, loaded terms and sensitive topics, timelines and animations, KC/KCGO fit, operators and AFB, marking scheme, the German + closest-English lines and history terms, privacy and copyright - and writes a report with verdict and Must / Should / Other findings (what, why, fix) to reviews/. Reviews only; fixes when asked. Use after darshan-singh-meel-schule-geschichte or on any existing Geschichte material; load darshan-singh-meel-schule and darshan-singh-meel-schule-geschichte alongside. Triggers - "Geschichte prüfen", "Klausur Geschichte gegenlesen", "Quellenanalyse prüfen", "Zeitleiste prüfen", "Review Geschichte"; "review my history worksheet", "fact-check the dates".
---

# Geschichte: review

Reviewer for material in `unterricht/geschichte/<stufe>/<thema>/` (or any Geschichte HTML the user names). Uses the base rubric (`darshan-singh-meel-schule/references/review.md`: process, 12 areas, severity, report format, verdict) plus the subject checks in `references/checks.md`. Nothing from the rubric is repeated here.

## Rules
- **Review, do not rewrite.** No file of the material is changed unless the user asks for the fixes after the report.
- **Independent solution first.** Work every task from the info box and the materials only, before opening `loesung.html` or `erwartungshorizont.html`: own summary, own context, own comparison grid, own judgement with criteria. Then compare. For open tasks check that the printed criteria admit your reasoned answer.
- **Every fact is checked or reported as unchecked.** List all dates, names, offices, numbers and quotations of all files; check each against the source cited in the material, then against one more official or public scholarly page (list: subject skill `references/sources.md`). A fact that could not be checked goes under `Not checked` - never "correct" from memory alone. `references/checks.md` has anchor dates for a first plausibility test only.
- **What a date marks.** Check the verb with the date: beschlossen, unterzeichnet, verkündet, in Kraft, aufgehoben. Pages that differ → finding with both dates and the safer wording.
- **Quotations word for word.** Compare every quoted source line with the cited edition: wording, paragraph number, cuts marked, spelling statement. A cut that changes the meaning is a Must.
- **Judgement fairness.** A marking scheme that rewards one opinion, or a task that asks for a Werturteil without naming it, is a finding.
- **Evidence.** Every finding names file, task or material id, and quotes the line. No praise, no summary of the material.
- **Privacy.** The report never quotes student names or data.

## Process (fixed)
1. **Scope** - folder or files from the request; default every `.html` in the topic folder. Level (Jahrgang, E, Q1-Q4, GK/LK) from the header; if missing, ask one question.
2. **Load** base `references/review.md` and `bilingual.md`; subject `references/sek1.md` or `oberstufe.md` for the level, `quellenarbeit.md`, `begriffe.md`; this skill's `references/checks.md`.
3. **Script** - `python <base skill dir>/scripts/check_material.py <folder>`. Every `FAIL` is a Must; every `?` is read by hand (a German source text without `data-nur-de` shows up here). Then add up the printed numbers by hand (`checks.md` A10): the script does not read every printed number.
4. **Solve** every task without the solution; keep your results per task id in a working list (not in the report).
5. **Fact list** - extract dates, names, numbers, quotations from all files; check as the rules say (`checks.md` A, B). Re-run `zeitleiste.py` with the dates of a timeline and compare the x positions (`checks.md` D).
6. **Compare** your results with solution/Erwartungshorizont; check that worksheet, solution, test, Erwartungshorizont, Erklärung and animation agree with each other.
7. **Walk** the base checklist (areas 1-12) and `checks.md` sections C, E-H (source work, KC fit, wording and sensitive topics, bilingual terms, animation).
8. **Report** to `reviews/darshan-singh-meel-schule-geschichte-review-<YYYY-MM-DD-HHMM>.md` in the base report format (add `/reviews/` to `.gitignore` on first use). Each finding: **what · why · fix**. Bilingual findings carry the kind (`fehlt`, `zu frei`, `zu wörtlich`, `Fachbegriff`) and the corrected English line.
9. **Reply** - verdict, counts (Must / Should / Other, script errors and warnings), report path (relative), and one line: "Soll ich die Must-Punkte korrigieren?" Fix only on yes; after fixing, re-run steps 3-6 for the changed parts and append "Nachprüfung" to the report.

## Severity additions for Geschichte
| Must | Should |
|---|---|
| wrong date, name, office, number or attribution; files disagree on a date | date right but the act it marks is unclear ("am ... trat in Kraft" vs verkündet) |
| quotation differs from the cited text; unmarked cut; cut changes the meaning | spelling statement (originalgetreu/modernisiert) missing |
| invented text presented as a historical source; invented quotation of a real person | source without Adressat or place where the task asks for them |
| Darstellung labelled Quelle or the reverse | only one perspective on a contested topic |
| copied textbook/Abitur text, press photo or modern cartoon | word list for hard source words missing |
| English translation printed for a source the students must analyse in German | present-day comparison without criteria |
| NS or other loaded term used as our own description without marking; stereotype or perpetrator view presented as fact | epoch or label used without hint at its construct character (from Jg. 9) |
| role play or empathy task with victims or perpetrators of mass crimes; forbidden symbols in a figure | single-cause wording in an info box |
| marking scheme rewards one opinion; judgement task without criteria in the Erwartungshorizont; printed points or sums disagree | Sachurteil/Werturteil not named in the task |
| timeline not true to scale without a marked break; animation date differs from worksheet | more than 8 events on one axis |
| LK-only standard or content in GK material; Oberstufe standard in Sek I material; Themenfeld or standard code that does not exist; KC reference printed in no file | Leitfrage not answered by the last task |

## References
| File | Read when |
|---|---|
| `references/checks.md` | every review: check lists A-H, anchor dates, common defects |
| base `references/review.md` | every review: rubric, severity, report format, verdict |
