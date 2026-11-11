---
name: darshan-singh-meel-schule-chemie
description: Chemie teaching material for Gymnasium in Hessen - Mittelstufe (Sek I, Kerncurriculum) and Oberstufe (KCGO, E-Phase, Q1-Q4, Grundkurs and Leistungskurs) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations for students, experiment sheets with safety block (GHS, student restrictions, disposal) and expected observations, calculations with full solution steps, and step animations on the particle level (particle model, electron and proton transfer, equilibrium, reaction mechanisms). German text with the closest English sentence under every line, subject terms DE | EN (Bili option). Use for any request to plan, write or explain Chemie lessons or material; load darshan-singh-meel-schule alongside. Triggers - "Chemie", "Chemiestunde", "Chemieunterricht", "Arbeitsblatt Chemie", "Klausur Chemie", "Chemie LK", "Chemie GK", "Versuchsvorschrift", "Schülerversuch", "Gefährdungsbeurteilung", "Reaktionsgleichung", "Redoxreaktion", "Säure-Base", "Titration", "Teilchenmodell", "organische Chemie", "chemisches Gleichgewicht", "Bili Chemie"; "chemistry lesson", "chemistry worksheet", "chemistry test", "lab sheet", "risk assessment draft", "reaction equation", "particle model animation", "bilingual chemistry".
---

# Chemie (Hessen) · Sek I · Oberstufe
Load `darshan-singh-meel-schule` first (formats, folders, DE + EN rule, grading, operators, `check_material.py`) → this file adds the subject.

## Scope
- Sek I, first Chemie year to Jg. 10 · `jg07`…`jg10` · `references/sek1.md`
- E · `e` · Q1-Q4 GK/LK · `q1-gk`…`q4-lk` · `references/oberstufe.md`
- Output `unterricht/chemie/<stufe>/<thema>/` · not covered: Grundschule, Realschule, Hauptschule.

## Rules
- KC cite → Sek I: Kompetenzbereich · Teilbereich · Kompetenzerwartung (Ende Jg. 9/10) · Inhaltsfeld full name (`Verwandlungen - Chemische Reaktion`) → Oberstufe: Standard code (`S 16`, `E 5`, `K 7`, `B 11`) · `<Kurshalbjahr>.<Nr> <Themenfeld>` · GK/LK → wording only from references, else `check: <KC PDF>`.
- GK never gets LK-only content · Q2-Q4 binding content set by Erlass → check: Abiturerlass of the exam year before a Klausur.
- Sek I KC has no year plan (`1. Lernjahr`, `bis Ende Jg. 9/10`) → first Chemie year is school-specific: ask.
- Stoffebene ≠ Teilchenebene (KC Sek I; KCGO S 6) → observation = substances + properties (`rotbrauner Belag`) · interpretation = particles (`Kupfer(II)-Ionen nehmen Elektronen auf`) · atoms have no colour, molecules do not melt.
- Equations balanced in atoms + charges · state symbols (s) (l) (g) (aq) from Jg. 9 · real `<sub>`/`<sup>`, never `H2O`, `Cu2+` in running text · notation in `fachpraxis.md`.
- Calculation → given → wanted → formula → insert with units → result with unit, sensible digits → answer sentence · constants from the table on the sheet · recalculate every solution before writing.
- Experiment sheet → safety block (student lines on sheet, teacher lines in plan/Lösung) + expected observation in Lösung/plan only (`sicherheit.md`, `fachpraxis.md`) · GHS data from DEGINTU or safety data sheet, not looked up → `prüfen / check`, never fact · print: `Entwurf - ersetzt nicht die Gefährdungsbeurteilung der Lehrkraft.`
- No student experiment a student may not do (`sicherheit.md`, restrictions by Jahrgang) → Lehrerdemonstration or video/data.
- Model ≠ reality → every particle picture/animation names its model + one limit (from Jg. 9).
- Terms → KC wording (`Oxonium-Ion`, `Alkanole`, `Benzen (Benzol)`, `Stoffmengenkonzentration`) · English from `begriffe.md`.

## Process
1. Setup → base questions, one AskUserQuestion (max 4, rec first) + subject options:
   - Jahrgang/Kurs · Sek I year + which Chemie Lernjahr | E/Q1-Q4 + GK/LK
   - Thema · 3 topics from the Inhaltsfeld/Themenfeld
   - Versuch · Schülerversuch (rec if allowed for the Jahrgang) · Lehrerdemonstration · kein Versuch, Beobachtungen/Messwerte auswerten
   - Still open → 2nd prompt: Sprache · Zeit · Differenzierung (base defaults) · calculations: which Tafelwerk/PSE values
2. Read level reference · `sicherheit.md` (if heated, mixed, handled) · `fachpraxis.md` · `begriffe.md` · base files per its SKILL.md.
3. Plan in 5 lines (base step 3) + 1: description level (Stoff, Teilchen, Symbol) · model · experiment type or data source.
4. Create from base templates, pair by pair (DE line → EN line) · example `references/examples/redoxreihe-e/`.
5. Self-check → solve each task blind → compare · tick: equation balanced (atoms, charges) · states + names · calculation redone, units, digits · observation = Stoff, interpretation = Teilchen · operator + AFB · solvable from info box + earlier lessons · level (GK/LK, stage) · safety block complete, no restricted activity · figure + animation = text.
6. Layout → `python <base skill dir>/scripts/check_material.py unterricht/chemie/<stufe>/<thema>/` → fix every error, read every `?` → by eye: sub/superscripts everywhere · answer space fits (squared field for calculations, apparatus sketches) · nothing by colour alone · no task/observation table split (`class="aufgabe teil"`, table in `div.teil`) · A4 preview.
7. Hand over → files (relative) · KC ref · every `check:`/`prüfen` line the teacher must settle (GHS, GBU) · offer `darshan-singh-meel-schule-chemie-review` (rec for tests, Klausuren, every experiment sheet).

## References
- `references/sek1.md` · Sek I: Kompetenzbereiche, Kompetenzerwartungen Ende Jg. 9/10, 4 Basiskonzepte, 7 Inhaltsfelder
- `references/oberstufe.md` · E, Q1-Q4: Standards S/E/K/B + codes, Themenfelder GK/LK, binding rules
- `references/sicherheit.md` · any experiment: RiSU, GBU, student restrictions by Jahrgang, GHS pictograms, safety block, disposal
- `references/fachpraxis.md` · notation, constants, calculation + protocol form, standard experiments + expected observations, typical errors, animations
- `references/begriffe.md` · glossary DE | EN, false friends
- `references/examples/redoxreihe-e/` · finished lesson plan + experiment worksheet + solution
- `references/sources.md` · official pages, verified vs `check:`
