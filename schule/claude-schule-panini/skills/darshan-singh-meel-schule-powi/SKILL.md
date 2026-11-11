---
name: darshan-singh-meel-schule-powi
description: Teaching material for Politik und Wirtschaft (Hessen, Gymnasium Sek I Jg. 5-10 and Oberstufe E-Q4, Grundkurs and Leistungskurs) and for Wirtschaftswissenschaften (Oberstufe) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations for students, and animations of models (market, circular flow, business cycle, legislation). German with the closest natural English sentence under every line. Covers the Hessen Kerncurriculum (Inhaltsfelder, Themenfelder, Bildungsstandards A/U/H/M), the Beutelsbacher Konsens, current data with source and date, case studies, Sachurteil and Werturteil. Use with darshan-singh-meel-schule. Triggers - "Politik und Wirtschaft", "PoWi", "Wirtschaftswissenschaften", "Wirtschaft Unterricht", "Sozialkunde", "Gemeinschaftskunde", "Marktmodell", "Angebot und Nachfrage", "Wirtschaftskreislauf", "Konjunktur", "Soziale Marktwirtschaft", "Grundgesetz", "Gesetzgebung", "Wahlen", "Parteien", "EU", "Globalisierung", "Karikatur analysieren", "Fallanalyse", "Urteilsbildung", "Pro-Kontra-Debatte"; "economics lesson", "politics lesson", "civics", "supply and demand worksheet", "circular flow animation", "case study economics", "bilingual economics German English".
---

# Politik und Wirtschaft · Wirtschaftswissenschaften (Hessen)
Load `darshan-singh-meel-schule` first (formats, folders, DE + EN rule, grading, setup, `check_material.py`) → this file adds the subject.

## Scope
- Sek I Gymnasium Jg. 5-10 · PoWi · KC Sek I: 4 Kompetenzbereiche, 6 Inhaltsfelder, standards end Jg. 9/10 only · `references/sek1.md`
- E1-Q4 GK/LK · PoWi · KCGO (Ausgabe 2024, Stand 21.04.2026; official list "Ausgabe April 2026") · `references/oberstufe.md`
- E1-Q4 GK/LK · Wirtschaftswissenschaften · KCGO same Stand · `references/wirtschaftswissenschaften.md`
- Output folder `<fach>` = `wirtschaft` (both subjects) · not covered: Grundschule Sachunterricht, Wirtschaftslehre berufliches Gymnasium, Arbeitslehre.

## Rules
- Beutelsbacher Konsens in every file → no overwhelming · controversy stays controversial · students analyse own interests. Each judgement task: ≥2 defensible positions in the solution · never say which party, policy or school is right · test in `references/fachregeln.md`.
- Real data → only with `Quelle: <institution>, <table/publication>, Stand: <date>, abgerufen: <date>` under the material · fetch only from official statistics pages (`fachregeln.md`) and only if network allowed, else ask user for figures · never from memory.
- Invented numbers → `Modellzahlen (erfunden)` / `model figures (invented)` · never mix model and real data in one table.
- Persons, parties, majorities, coalitions, laws in force → only from dated official source, or stay structural (roles, not names) · invented persons, firms, towns marked invented.
- Sachurteil before Werturteil → task names criteria (Effizienz · Gerechtigkeit · Legitimität · Nachhaltigkeit) or asks student to choose + name them · Erwartungshorizont rewards criteria, weighing, coherence, never the position.
- Model ≠ reality → teach assumptions + limits · a model-application task is followed by a task naming a limit (`modelle-animationen.md`).
- AFB II/III tasks → numbered material (M1, M2 …): text · statistic · chart · cartoon description · legal text · case · cartoons/press copyrighted → original text or invented cartoon described · laws (GG) may be quoted with article + version date.
- KC cite → Sek I: Kompetenzbereich · Kompetenzerwartung (Ende Jg. 9/10) · Inhaltsfeld → Oberstufe: Standard code (A3, U5 …) · `Q2.1` · GK/LK · LK-only content never in GK.

## Process
1. Setup → base questions, one AskUserQuestion + subject options:
   - Fach · PoWi (rec) · Wirtschaftswissenschaften
   - Thema · 3 topics from the Inhaltsfeld/Themenfeld
   - Daten (only if real figures needed) · Modellzahlen (rec for models) · aktuelle amtliche Daten abrufen (needs network) · Daten liefere ich
   - Q-phase → Themenfelder per Abiturerlass of exam year: ask, or `check: Abiturerlass`
2. Read level reference · `fachregeln.md` · `modelle-animationen.md` (model/animation).
3. Plan in 5 lines (base step 3) + controversy (positions A, B) · material list M1… each with source or `erfunden` · model + its limit.
4. Create from base templates → material → tasks → solution → lesson plan → animation.
5. Self-check → solve each task from material alone · recompute every number, sum, %, intersection · each real figure has source + Stand + Abrufdatum, each invented one labelled · each judgement task: 2 positions, criteria named, no position rewarded · institution/law statements vs GG article or `check:` · operator from FB II list (base `operatoren.md`), AFB fits · EN: `auswerten` → analyse, `beurteilen` → assess · GK: nothing from the erhöhtes-Niveau column · neutrality test passed.
6. Layout → `python <base skill dir>/scripts/check_material.py <folder>` → fix every FAIL, read every `?`.
7. Hand over → files (relative) · KC ref · data sources with dates · every `check:` · offer `darshan-singh-meel-schule-powi-review` (optional).

## Animation
- Use for change over time · cause → effect: price finding · supply/demand shifts · circular flow · business cycle · multiplier rounds · path of a bill · seat allocation steps · static chart/organigram → `erklaerung.html` · step plans `modelle-animationen.md`.

## References
- `references/sek1.md` · Jg. 5-10: Kompetenzbereiche, Kompetenzerwartungen, Inhaltsfelder, year placement
- `references/oberstufe.md` · E1-Q4 PoWi: standards, Themenfelder, GK/LK split, what is binding
- `references/wirtschaftswissenschaften.md` · E1-Q4 WiWi: differences to PoWi
- `references/fachregeln.md` · always: Konsens, data sources, material types, case study, judgement, typical mistakes
- `references/modelle-animationen.md` · model, diagram, animation
- `references/begriffe.md` · glossary DE | EN, mistranslations
- `references/examples/marktpreis/` · finished Jg. 9 worksheet + solution + animation
- `references/sources.md` · where each fact comes from, what is unverified
