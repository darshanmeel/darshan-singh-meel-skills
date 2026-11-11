---
name: darshan-singh-meel-schule-erdkunde-review
description: Reviews Erdkunde / Geographie teaching material for Gymnasium in Hessen (Sek I and Oberstufe, GK/LK) - solves every task independently from the materials, recomputes every value (climate diagram, scale, rates, shares), checks maps and diagrams (legend, scale, north, source), data sources and years, KC/KCGO fit, operators and AFB, marking scheme, the German + closest-English lines and geography terms, animations, privacy and copyright - and writes a report with verdict and Must / Should / Other findings (what, why, fix) to reviews/. Reviews only; fixes when asked. Use after darshan-singh-meel-schule-erdkunde or on any existing Erdkunde material; load darshan-singh-meel-schule and darshan-singh-meel-schule-erdkunde alongside. Triggers - "Erdkunde prüfen", "Geographie-Arbeitsblatt prüfen", "Klausur Geographie gegenlesen", "Klimadiagramm prüfen", "Review Erdkunde"; "review my geography worksheet", "check this geography test", "check the climate diagram".
---

# Erdkunde / Geographie: review

Reviewer for material in `unterricht/erdkunde/<stufe>/<thema>/` (or any Erdkunde HTML the user names). Uses the base rubric (`darshan-singh-meel-schule/references/review.md`: process, 12 areas, severity, report format, verdict) plus the subject checks in `references/checks.md`. Nothing from the rubric is repeated here.

## Rules
- **Review, do not rewrite.** No file of the material is changed unless the user asks for the fixes after the report.
- **Independent solution first.** Solve every task from the info box and the materials only, before opening `loesung.html` or `erwartungshorizont.html`. Then compare. A task you solve differently is a finding even if the printed solution looks plausible.
- **Recompute, never trust.** Every number in tasks, materials, solutions, figures and captions is recomputed or re-read: sums, means, ranges, scale distances, rates, shares, dates. Climate diagrams are re-run with the skill's script from the printed values.
- **Read the figure as a student.** Every value a task asks for must be readable in the figure at print size; check the SVG coordinates against the values, not only the caption.
- **Facts against official sources.** Data with a source line are checked against that source when it is an official page (list: subject skill `references/sources.md`); otherwise the finding is "source not verifiable". No fact from memory is reported as verified - mark `not checked`.
- **Evidence.** Every finding names file, task or material id, and quotes the line. No praise, no summary of the material.
- **Privacy.** The report never quotes student names or data; it says "personal data in <file>, line <n>".

## Process (fixed)
1. **Scope** - folder or files from the request; default every `.html` in the topic folder. Level (Jahrgang, E, Q1-Q4, GK/LK) from the header; if missing, ask one question.
2. **Load** base `references/review.md` and `bilingual.md`; subject `references/sek1.md` or `oberstufe.md` for the level, `fachpraxis.md`, `begriffe.md`; this skill's `references/checks.md`.
3. **Script** - `python <base skill dir>/scripts/check_material.py <folder>`. Every `FAIL` is a Must; every `?` is read by hand. Then add up the printed numbers by hand (`checks.md` A8): the script does not read every printed number.
4. **Solve** every task without the solution; write your result per task id in a working list (not in the report).
5. **Recompute and re-read** per `references/checks.md` sections A-D: numbers, climate diagram re-run, map and diagram form, sources and years.
6. **Compare** your results with solution/Erwartungshorizont; check that worksheet, solution, test, Erwartungshorizont, Erklärung and animation agree with each other.
7. **Walk** the base checklist (areas 1-12) and `checks.md` sections E-H (KC fit, wording, bilingual terms, animation).
8. **Report** to `reviews/darshan-singh-meel-schule-erdkunde-review-<YYYY-MM-DD-HHMM>.md` in the base report format (add `/reviews/` to `.gitignore` on first use). Each finding: **what · why · fix**. Bilingual findings carry the kind (`fehlt`, `zu frei`, `zu wörtlich`, `Fachbegriff`) and the corrected English line.
9. **Reply** - verdict, counts (Must / Should / Other, script errors and warnings), report path (relative), and one line: "Soll ich die Must-Punkte korrigieren?" Fix only on yes; after fixing, re-run steps 3-6 for the changed tasks and append "Nachprüfung" to the report.

## Severity additions for Erdkunde
| Must | Should |
|---|---|
| a value or printed point number in task, material, solution or figure is wrong or they disagree | source line lacks period or retrieval year |
| a reading the task needs cannot be made from the figure | scale level or year not named in a task |
| real data without source, or invented data not marked | map lacks north arrow but orientation is clear from labels |
| copied map, photo, cartoon or textbook figure | model shown without the word "Modell" or without a limit (from Jg. 9) |
| map without legend or without scale information when a task measures or locates | wording from "avoid" list in `begriffe.md` |
| LK-only content in GK material; Oberstufe-only content or KCGO standard in Sek I material; Themenfeld or standard code that does not exist; KC reference printed in no file | Raumbeispiel differs from the one named in the plan |
| deterministic or stereotyping statement presented as fact | description and explanation mixed in the solution |

## References
| File | Read when |
|---|---|
| `references/checks.md` | every review: check lists A-H, facts for recomputing, common defects |
| base `references/review.md` | every review: rubric, severity, report format, verdict |
