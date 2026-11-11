---
name: darshan-singh-meel-schule-powi
description: Teaching material for Politik und Wirtschaft (Hessen, Gymnasium Sek I Jg. 5-10 and Oberstufe E-Q4, Grundkurs and Leistungskurs) and for Wirtschaftswissenschaften (Oberstufe) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations for students, and animations of models (market, circular flow, business cycle, legislation). German with the closest natural English sentence under every line. Covers the Hessen Kerncurriculum (Inhaltsfelder, Themenfelder, Bildungsstandards A/U/H/M), the Beutelsbacher Konsens, current data with source and date, case studies, Sachurteil and Werturteil. Use with darshan-singh-meel-schule. Triggers - "Politik und Wirtschaft", "PoWi", "Wirtschaftswissenschaften", "Wirtschaft Unterricht", "Sozialkunde", "Gemeinschaftskunde", "Marktmodell", "Angebot und Nachfrage", "Wirtschaftskreislauf", "Konjunktur", "Soziale Marktwirtschaft", "Grundgesetz", "Gesetzgebung", "Wahlen", "Parteien", "EU", "Globalisierung", "Karikatur analysieren", "Fallanalyse", "Urteilsbildung", "Pro-Kontra-Debatte"; "economics lesson", "politics lesson", "civics", "supply and demand worksheet", "circular flow animation", "case study economics", "bilingual economics German English".
---

# Politik und Wirtschaft · Wirtschaftswissenschaften (Hessen)

Load `darshan-singh-meel-schule` first: it owns formats, folders, the German + English line rule, grading, the setup questions and the check script. This skill adds subject content only.

## Scope
| Level | Subject | Curriculum | Reference |
|---|---|---|---|
| Gymnasium Sek I, Jg. 5-10 | Politik und Wirtschaft | KC Sek I Gymnasium: 4 Kompetenzbereiche, 6 Inhaltsfelder, standards for the end of Jg. 9/10 only | `references/sek1.md` |
| Oberstufe E1-Q4, GK and LK | Politik und Wirtschaft | KCGO, PDF: Ausgabe 2024, Stand 21.04.2026; official list: "Ausgabe April 2026" | `references/oberstufe.md` |
| Oberstufe E1-Q4, GK and LK | Wirtschaftswissenschaften | KCGO, PDF: Ausgabe 2024, Stand 21.04.2026 | `references/wirtschaftswissenschaften.md` |

- Output folder `<fach>`: `wirtschaft` (base convention) for both subjects.
- Not covered: Grundschule (Sachunterricht), Wirtschaftslehre of the berufliches Gymnasium, Arbeitslehre.

## Rules (on top of the base rules)
- **Beutelsbacher Konsens in every file.** No overwhelming, controversy stays controversial, students analyse their own interests. Every judgement task has at least two defensible positions in the solution; the material never states which party, policy or economic school is right. Details and the test: `references/fachregeln.md`.
- **Real data only with source and date.** Every real figure carries `Quelle: <institution>, <table or publication>, Stand: <date>, abgerufen: <date>` under the material. Fetch from the official statistics pages listed in `references/fachregeln.md` only when the user allows network use; otherwise ask the user for the figures. No figure from memory.
- **Model data are labelled.** Invented numbers (market table, firm, household budget) carry `Modellzahlen (erfunden)` / `model figures (invented)`. Never mix model and real data in one table.
- **Persons and parties.** Office holders, majorities, coalitions, party positions and laws in force change: write them only from a dated official source, or keep the task structural (roles, not names). Invented persons, firms and towns are marked as invented.
- **Sachurteil before Werturteil.** Judgement tasks name the criteria (e.g. Effizienz, Gerechtigkeit, Legitimität, Nachhaltigkeit) or ask the student to choose and name them. The Erwartungshorizont rewards criteria, weighing and coherence - never the position taken.
- **Model ≠ reality.** Each model is taught with its assumptions and limits; a task that applies a model is followed by one that names a limit (`references/modelle-animationen.md`).
- **Material-bound tasks.** AFB II and III tasks refer to numbered material (M1, M2 ...): text, statistic, chart, cartoon description, legal text, case. Cartoons and press texts are copyrighted: write an original text or describe an invented cartoon; legal texts (Grundgesetz, laws) may be quoted with article and date of the version.
- **KC citation.** Sek I: Kompetenzbereich + Kompetenzerwartung (Ende Jg. 9/10) + Inhaltsfeld. Oberstufe: Bildungsstandard code (A3, U5 ...) + `Q2.1` + GK or LK. LK-only content never in GK material.

## Process (fixed)
1. **Setup** - the base questions (one AskUserQuestion prompt). Subject additions inside those questions:
   - Fach: Politik und Wirtschaft (Recommended) · Wirtschaftswissenschaften.
   - Thema: offer 3 topics from the Inhaltsfeld / Themenfeld of the level.
   - Daten (only when the topic needs real figures): Modellzahlen (Recommended for models) · aktuelle amtliche Daten abrufen (needs network permission) · Daten liefere ich.
   - Q-phase: which Themenfelder the Abiturerlass of the exam year set - ask, or mark `check: Abiturerlass`.
2. **Read** the level reference, `references/fachregeln.md`, and `references/modelle-animationen.md` when a model or animation is involved.
3. **Plan in 5 lines** (base step 3) plus: the controversy (positions A and B), the material list (M1 ...) each with its source or `erfunden`, the model and its limit.
4. **Create** from the base templates. Order: material → tasks → solution → lesson plan → animation.
5. **Self-check every task and answer** before the layout check:
   - solve each task from the material alone; recompute every number, sum, percentage and point of intersection;
   - each real figure has source + Stand + Abrufdatum; each invented one is labelled;
   - each judgement task: two positions in the solution, criteria named, no position rewarded;
   - each statement about institutions and law checked against the Grundgesetz article or marked `check:`;
   - operator from the FB II list (base `references/operatoren.md`), AFB matches the demand; English line: `auswerten` → analyse, `beurteilen` → assess;
   - GK material: no content from the erhöhtes-Niveau column of the Themenfeld;
   - neutrality test of `references/fachregeln.md` passed.
6. **Layout check** - `python <base skill dir>/scripts/check_material.py <folder>`; fix every FAIL, read every `?`.
7. **Reply** with files (relative paths), KC reference, data sources with dates, every `check:`. Offer the review by `darshan-singh-meel-schule-powi-review` (optional).

## Animation: when
Use for change over time or cause → effect chains: price finding on a market, shifts of supply or demand, the circular flow of money and goods, the business cycle, multiplier rounds, the path of a bill, seat allocation step by step. A static chart or organigram goes into `erklaerung.html`. Step plans: `references/modelle-animationen.md`.

## References
| File | Read when |
|---|---|
| `references/sek1.md` | Jg. 5-10: Kompetenzbereiche, Kompetenzerwartungen, Inhaltsfelder, placing a topic in a year |
| `references/oberstufe.md` | E1-Q4 Politik und Wirtschaft: Bildungsstandards, Themenfelder, GK/LK split, what is binding |
| `references/wirtschaftswissenschaften.md` | E1-Q4 Wirtschaftswissenschaften: what differs from Politik und Wirtschaft |
| `references/fachregeln.md` | always: Beutelsbacher Konsens, data sources, material types, case study, judgement, typical mistakes |
| `references/modelle-animationen.md` | a model, a diagram or an animation |
| `references/begriffe.md` | glossary `DE | EN`; terms that are often translated wrongly |
| `references/examples/marktpreis/` | one worked output (Jg. 9, Marktpreis: Arbeitsblatt, Lösung, Animation) to copy the level of detail from |
| `references/sources.md` | where each fact comes from; what is not verified |
