---
name: darshan-singh-meel-schule-biologie
description: Biologie teaching material for Gymnasium in Hessen - Mittelstufe (Sek I, Jg. 5-10, Kerncurriculum) and Oberstufe (KCGO, E-Phase, Q1-Q4, Grundkurs and Leistungskurs) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations for students, experiment sheets with safety block and expected observations, and step animations of processes (cell division, osmosis, enzymes, protein biosynthesis, action potential). German text with the closest English sentence under every line, subject terms DE | EN (Bili option). Use for any request to plan, write or explain Biologie lessons or material; load darshan-singh-meel-schule alongside. Triggers - "Biologie", "Bio-Stunde", "Biologieunterricht", "Arbeitsblatt Biologie", "Klausur Biologie", "Bio LK", "Bio GK", "Versuchsprotokoll", "Mikroskopieren", "Zellbiologie", "Genetik", "Evolution", "Ökologie", "Neurobiologie", "Stoffwechsel", "Mitose", "Bili Biologie"; "biology lesson", "biology worksheet", "biology test", "lab sheet", "cell division animation", "bilingual biology".
---

# Biologie (Gymnasium Hessen, Sek I and Oberstufe)

Adds the subject side to `darshan-singh-meel-schule` (base): KC content, biology conventions, experiments and safety, terms, animations. Formats, folders, the German + English rule, grading, operators and the check script are the base's - not repeated here.

## Scope
| Level | Folder `<stufe>` | Reference |
|---|---|---|
| Sek I, Jg. 5-10 | `jg05` ... `jg10` | `references/sek1.md` |
| Einführungsphase | `e` | `references/oberstufe.md` |
| Q1-Q4, GK or LK | `q1-gk` ... `q4-lk` | `references/oberstufe.md` |

Output folder: `unterricht/biologie/<stufe>/<thema>/`. Not covered: Grundschule (Sachunterricht), Realschule and Hauptschule KC.

## Rules
- **KC citation.** Sek I: Kompetenzbereich + Teilbereich + Kompetenzerwartung (stage: Ende Jg. 6 or Ende Jg. 9/10) + Inhaltsfeld. Oberstufe: Bildungsstandard with code (`S 7`, `E 4`, `K 9`, `B 8`) + `<Kurshalbjahr>.<Nr> <Themenfeld>` + GK or LK. Wording only from `references/sek1.md` / `references/oberstufe.md`; anything else: `check: <KC PDF>`.
- **GK never gets LK-only content** (erhöhtes Niveau). LK material may use both.
- **Sek I has no year-by-year plan** in the KC (only "Jg. 5/6" and "bis Ende Jg. 9/10"). The year comes from the school's Fachcurriculum: ask, or place by stage and say so.
- **System levels named.** Every explanation says on which level it argues (Molekül, Zelle, Gewebe, Organ, Organismus, Population, Ökosystem) and marks a change of level.
- **Causal, not final.** No purpose wording for evolution or physiology (`damit`, `um zu`, "die Giraffe will ...", "die Natur hat ..."). Proximate and ultimate causes are kept apart (KCGO K 7, K 8).
- **Model is not reality.** Every model, scheme and animation is labelled as a model, with one limit named from Jg. 9 on.
- **Observation before interpretation.** In protocols and tasks `Beobachtung` and `Deutung` are separate fields; a solution never puts an explanation into the observation.
- **Data and diagrams.** Axes with quantity and unit, independent variable on the x-axis, source or "erfundene Daten / invented data" under every data set. Data must be biologically plausible (order of magnitude checked).
- **Experiments.** Every experiment sheet carries the safety block and the expected observation (`references/fachpraxis.md`). The block is a draft for the teacher; it never replaces the Gefährdungsbeurteilung - print that sentence.
- **Sensitive topics** (Sexualität des Menschen, Humangenetik, Trisomie 21, Schwangerschaftsabbruch, Sucht, Evolution and religion): factual, respectful wording; invented families and pedigrees only; no judgement of persons. Sexualerziehung: check: HSchG § 7 and the Hessen Lehrplan Sexualerziehung (parents are informed beforehand).
- **Terms.** German school term first, English from `references/begriffe.md`; scientific names in italics (`<i>Drosophila melanogaster</i>`), genes italic, proteins not.

## Process (fixed)
1. **Setup** - the base's questions (one AskUserQuestion prompt, max 4, recommended first), with these subject options:
   - Jahrgang/Kurs: Sek I Jahrgang, or E / Q1-Q4 with GK or LK.
   - Thema: 3 topics from the Inhaltsfeld (Sek I) or Themenfeld (Oberstufe) of that level.
   - If the topic allows an experiment: Schülerversuch (Recommended when listed for students in `fachpraxis.md`) · Lehrerdemonstration · kein Versuch, Auswertung gegebener Daten.
   - Second prompt only if still open: Sprache, Zeit, Differenzierung (base defaults).
2. **Read** `references/sek1.md` or `references/oberstufe.md` for the level; `references/fachpraxis.md` for experiments, protocols, typical errors and animation choice; `references/begriffe.md` for the glossary; base files as its SKILL.md says.
3. **Plan in 5 lines** (base step 3) plus one line: system level(s), model used, experiment or data source.
4. **Create** each output from the base templates, pair by pair (German line, then its English line). Example of a finished set: `references/examples/mitose-jg09/`.
5. **Self-check every task and answer** - solve each task without looking at the solution, then compare. Per task tick: fact correct · operator and AFB fit · solvable with the info box and the lessons before · level (GK/LK, stage) · observation and interpretation separate · numbers, units, chromosome counts, equations balanced · figure and animation show the same as the text.
6. **Layout check** - run `python <base skill dir>/scripts/check_material.py unterricht/biologie/<stufe>/<thema>/`; fix every error, read every `?` line. Then check by eye: answer space fits the expected answer, figures labelled inside the picture, nothing told apart by colour alone (also not in captions: `dicke Striche`, not `blaue Striche`), picture labels readable in the printed key frames (22 units or more), no task split across pages (`class="aufgabe teil"`), print preview A4.
7. **Hand over** - reply with files (relative paths), KC reference, every `check:` line used, and offer the review: `darshan-singh-meel-schule-biologie-review` (optional; recommended for tests and Klausuren).

## References
| File | Read when |
|---|---|
| `references/sek1.md` | Jg. 5-10: Kompetenzbereiche, Kompetenzerwartungen (Ende Jg. 6, Ende Jg. 9/10), Basiskonzepte, 8 Inhaltsfelder with content per stage |
| `references/oberstufe.md` | E, Q1-Q4: Bildungsstandards S/E/K/B with codes, Themenfelder with GK/LK content, binding rules, Basiskonzepte |
| `references/fachpraxis.md` | experiments and safety (RiSU, Biostoffe, animals, human material), protocol form, diagram and drawing rules, typical student errors, which animation for which process |
| `references/begriffe.md` | glossary DE \| EN per field; false friends |
| `references/examples/mitose-jg09/` | a finished worksheet, solution and animation (Jg. 9, Mitose) to copy the level of detail from |
| `references/sources.md` | official pages used, what is verified, what is `check:` |
