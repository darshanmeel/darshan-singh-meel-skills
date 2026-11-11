---
name: darshan-singh-meel-schule-chemie
description: Chemie teaching material for Gymnasium in Hessen - Mittelstufe (Sek I, Kerncurriculum) and Oberstufe (KCGO, E-Phase, Q1-Q4, Grundkurs and Leistungskurs) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations for students, experiment sheets with safety block (GHS, student restrictions, disposal) and expected observations, calculations with full solution steps, and step animations on the particle level (particle model, electron and proton transfer, equilibrium, reaction mechanisms). German text with the closest English sentence under every line, subject terms DE | EN (Bili option). Use for any request to plan, write or explain Chemie lessons or material; load darshan-singh-meel-schule alongside. Triggers - "Chemie", "Chemiestunde", "Chemieunterricht", "Arbeitsblatt Chemie", "Klausur Chemie", "Chemie LK", "Chemie GK", "Versuchsvorschrift", "Schülerversuch", "Gefährdungsbeurteilung", "Reaktionsgleichung", "Redoxreaktion", "Säure-Base", "Titration", "Teilchenmodell", "organische Chemie", "chemisches Gleichgewicht", "Bili Chemie"; "chemistry lesson", "chemistry worksheet", "chemistry test", "lab sheet", "risk assessment draft", "reaction equation", "particle model animation", "bilingual chemistry".
---

# Chemie (Gymnasium Hessen, Sek I and Oberstufe)

Adds the subject side to `darshan-singh-meel-schule` (base): KC content, chemistry notation, experiments and safety, calculations, terms, animations. Formats, folders, the German + English rule, grading, operators and the check script are the base's - not repeated here.

## Scope
| Level | Folder `<stufe>` | Reference |
|---|---|---|
| Sek I (from the first year of Chemie to Jg. 10) | `jg07` ... `jg10` | `references/sek1.md` |
| Einführungsphase | `e` | `references/oberstufe.md` |
| Q1-Q4, GK or LK | `q1-gk` ... `q4-lk` | `references/oberstufe.md` |

Output folder: `unterricht/chemie/<stufe>/<thema>/`. Not covered: Grundschule, Realschule and Hauptschule KC.

## Rules
- **KC citation.** Sek I: Kompetenzbereich + Teilbereich + Kompetenzerwartung (Ende Jg. 9/10) + Inhaltsfeld with its full name (`Verwandlungen - Chemische Reaktion`). Oberstufe: Bildungsstandard with code (`S 16`, `E 5`, `K 7`, `B 11`) + `<Kurshalbjahr>.<Nr> <Themenfeld>` + GK or LK. Wording only from the references; anything else: `check: <KC PDF>`.
- **GK never gets LK-only content.** In Q2-Q4 the binding content inside the Themenfelder is set by Erlass: check: Abiturerlass of the exam year before a Klausur.
- **Sek I has no year-by-year plan** in the KC (`1. Lernjahr` and `bis Ende Jg. 9/10`); the first year of Chemie depends on the school: ask.
- **Stoffebene and Teilchenebene never mixed** (KC Sek I; KCGO S 6). Observations name substances and properties (`rotbrauner Belag`); interpretations name particles (`Kupfer(II)-Ionen nehmen Elektronen auf`). Atoms have no colour, molecules do not melt.
- **Equations are balanced** in atoms and charges, with state symbols (s), (l), (g), (aq) from Jg. 9 on; formulas with real sub- and superscripts (`<sub>`, `<sup>`), never `H2O` or `Cu2+` in running text. Notation: `references/fachpraxis.md`.
- **Calculations**: given → wanted → formula → insert with units → result with unit and sensible digits → answer sentence. Molar masses and constants from the table printed on the sheet; every solution is recalculated before it is written.
- **Experiments**: every experiment sheet carries the safety block (student lines on the sheet, teacher lines in lesson plan or Lösung) and, in Lösung and lesson plan only, the expected observation (`references/sicherheit.md`, `references/fachpraxis.md`). GHS data come from DEGINTU or the safety data sheet; not looked up → marked `prüfen / check`, never stated as fact. The block is a draft; print: `Entwurf - ersetzt nicht die Gefährdungsbeurteilung der Lehrkraft.`
- **No experiment a student may not do** on a student sheet: check `references/sicherheit.md` (restrictions by Jahrgang); otherwise Lehrerdemonstration or video/data.
- **Model is not reality**: every particle picture and animation says which model it uses and one limit (from Jg. 9).
- **Terms**: KC wording (`Oxonium-Ion`, `Alkanole`, `Benzen (Benzol)`, `Stoffmengenkonzentration`); English from `references/begriffe.md`.

## Process (fixed)
1. **Setup** - the base's questions (one AskUserQuestion prompt, max 4, recommended first), with these subject options:
   - Jahrgang/Kurs: Sek I Jahrgang (and which Lernjahr of Chemie), or E / Q1-Q4 with GK or LK.
   - Thema: 3 topics from the Inhaltsfeld (Sek I) or Themenfeld (Oberstufe) of that level.
   - Versuch: Schülerversuch (Recommended when allowed for the Jahrgang) · Lehrerdemonstration · kein Versuch, Auswertung gegebener Beobachtungen oder Messwerte.
   - Second prompt only if still open: Sprache, Zeit, Differenzierung (base defaults); for calculations: which Tafelwerk/PSE values the class uses.
2. **Read** `references/sek1.md` or `references/oberstufe.md` for the level; `references/sicherheit.md` when anything is heated, mixed or handled; `references/fachpraxis.md` for notation, calculations, expected observations, typical errors, animation choice; `references/begriffe.md`; base files as its SKILL.md says.
3. **Plan in 5 lines** (base step 3) plus one line: level of description (Stoff, Teilchen, Symbol), model used, experiment with Versuchsart or data source.
4. **Create** each output from the base templates, pair by pair (German line, then its English line). Example of a finished set: `references/examples/redoxreihe-e/`.
5. **Self-check every task and answer** - solve each task without looking at the solution, then compare. Per task tick: equation balanced (atoms, charges) · states and names right · calculation redone, units carried, digits sensible · observation on the substance level, interpretation on the particle level · operator and AFB fit · solvable with the info box and earlier lessons · level (GK/LK, stage) · safety block complete and no restricted activity · figure and animation show the same as the text.
6. **Layout check** - run `python <base skill dir>/scripts/check_material.py unterricht/chemie/<stufe>/<thema>/`; fix every error, read every `?` line. By eye: sub-/superscripts everywhere, answer space fits (squared field for calculations and apparatus sketches), nothing told apart by colour alone, no task or observation table split across pages (`class="aufgabe teil"`, table in `div.teil`), print preview A4.
7. **Hand over** - reply with files (relative paths), KC reference, every `check:` and `prüfen` line the teacher must settle (GHS data, GBU), and offer the review: `darshan-singh-meel-schule-chemie-review` (optional; recommended for tests, Klausuren and every experiment sheet).

## References
| File | Read when |
|---|---|
| `references/sek1.md` | Sek I: Kompetenzbereiche, Kompetenzerwartungen Ende Jg. 9/10, 4 Basiskonzepte, 7 Inhaltsfelder with content per stage |
| `references/oberstufe.md` | E, Q1-Q4: Bildungsstandards S/E/K/B with codes, Themenfelder with GK/LK content, binding rules |
| `references/sicherheit.md` | any experiment: RiSU duties, GBU, student restrictions by Jahrgang, GHS pictograms, the safety block, disposal |
| `references/fachpraxis.md` | notation, quantities and constants, calculation form, protocol form, standard experiments with expected observations, typical errors, animations |
| `references/begriffe.md` | glossary DE \| EN per field; false friends |
| `references/examples/redoxreihe-e/` | a finished lesson plan, experiment worksheet and solution (E-Phase, Redoxreihe) to copy the level of detail from |
| `references/sources.md` | official pages used, what is verified, what is `check:` |
