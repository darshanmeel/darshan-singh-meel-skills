---
name: darshan-singh-meel-schule-physik
description: Physics teaching material for the Gymnasium in Hessen - Sekundarstufe I (Kerncurriculum Physik, 9 Inhaltsfelder) and Oberstufe (KCGO Physik, E-Phase and Q1-Q4, Grundkurs and Leistungskurs) - as lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations for students and step animations (motion, waves, circuits, fields), in German with the closest natural English sentence under every line. Checks units, significant figures and plausibility of every number and adds a safety block to every experiment. Use with darshan-singh-meel-schule whenever physics material is created or changed. Triggers - "Physik", "Physikstunde", "Physik Arbeitsblatt", "Physik Klausur", "Physik Lernkontrolle", "Physik-Versuch", "Physik Schülerexperiment", "Physik Versuchsprotokoll", "Mechanik", "Elektrizitätslehre", "Stromkreis", "Optik", "Schwingungen", "Wellen", "elektrisches Feld", "Induktion", "Quantenphysik", "Kernphysik", "t-s-Diagramm", "Physik zweisprachig"; "physics lesson", "physics worksheet", "physics test", "physics exam with marking scheme", "physics experiment", "physics lab report", "circuit", "waves animation", "bilingual physics".
---

# Physik (Hessen, Gymnasium: Sek I + Oberstufe)

Load `darshan-singh-meel-schule` first: it owns formats, templates, folder, language rule, grading, operators, process and review rubric. This skill adds the physics: curriculum content, conventions, experiments, animations, terms. Nothing from the base is repeated here.

## Scope
| Level | Curriculum | Read |
|---|---|---|
| Sek I, Jg. 5/6-10 (G9) | KC Hessen, Sekundarstufe I - Gymnasium, Physik: 4 Kompetenzbereiche, 9 Inhaltsfelder, two stages | `references/sek1.md` |
| Einführungsphase | KCGO Physik, E.1-E.7 (E.1-E.3 binding) | `references/oberstufe.md` |
| Q1-Q4, GK and LK | KCGO Physik, Q1.1-Q4.5 (9 binding Themenfelder; Q4.6: check: KCGO PDF); grundlegendes / erhöhtes Niveau | `references/oberstufe.md` |

Output folder: `unterricht/physik/<stufe>/<thema>/` (base convention; `<stufe>` = `jg07`, `e`, `q2-gk`, `q3-lk`).

## Rules
- **Curriculum.** Sek I: cite Kompetenzbereich + Teilbereich + Bildungsstandard (end of Jg. 9/10) + Inhaltsfeld + stage. The KC sets no year for a topic: take the year from the user's Fachcurriculum or place it by stage and say so. Oberstufe: cite Kurshalbjahr.Themenfeld, GK or LK, and the Bildungsstandard code (`S 7`, `E 4`). LK-only content (erhöhtes Niveau) never appears in GK material.
- **Quantities.** Every number that is a quantity carries its unit, in every line of every file. SI units and the notation in `references/konventionen.md`. Formula symbols as in the KCGO and the school's Formelsammlung; a new symbol is named on first use.
- **Significant figures.** Data are written with the digits that are meant (`0,200 kg`, not `200 g`, when three digits count). Results carry as many significant digits as the least precise input; intermediate values keep extra digits; rounding only at the end. Sek I stage 1: "sinnvoll runden" with the same logic, without the term.
- **Decimal sign.** German line: comma (`1,26 s`). English line: point (`1.26 s`). Same digits in both.
- **Plausibility.** Every result is compared with a known size (`konventionen.md`, table "Größenordnungen"). Invented measurement data follow the law they illustrate, with realistic scatter, and are labelled `erfundene Messwerte`.
- **Models.** Name the model in use (Strahlenmodell, Teilchenmodell, Feldlinienbild, Massepunkt) and, from Jg. 9 on, one limit of it. Model drawings are not pictures of reality - say so in the caption.
- **Experiments.** Every experiment in a plan, worksheet or test has: type (Schülerexperiment, Demonstrationsexperiment, Simulation), material list, set-up sketch, and a safety block (hazard · measure · who acts · stop rule). Limits and bans: `references/experimente.md`. No experiment is proposed that the reference forbids for students.
- **Formulas in tests.** State under "Hilfsmittel" what is allowed (Taschenrechner, Formelsammlung). A formula that is neither in the allowed aid nor to be known by heart at that point is given in the material.
- **Animation** when the content is motion or change over time: bodies moving with their diagram, a wave travelling or standing, charge carriers in a circuit, a field building up, a technical system working. A static law (formula, unit table) gets a figure. `references/animationen.md`.
- **Terms.** `DE | EN` from `references/begriffe.md`; false friends there are binding (`Impuls` = momentum, `Spannung` = voltage, `Leistung` = power).

## Process (fixed)
1. **Setup** - the base questions (subject = Physik is already answered). Add, in the same prompt while at most 4 are open, otherwise in a second prompt:

   | Question | Options |
   |---|---|
   | Experiment | Schülerexperiment in Gruppen (Recommended) · Demonstrationsexperiment · Simulation/Animation statt Versuch · kein Versuch |
   | Oberstufe only: course | GK (Recommended) · LK · E-Phase |
   | Tests only: aids | Taschenrechner + eingeführte Formelsammlung (Recommended) · nur Taschenrechner · keine |

   Sek I: ask for the Jahrgang of the topic in the school's Fachcurriculum only when the user did not give a year.
2. **Read** `references/sek1.md` or `references/oberstufe.md` for the level; `konventionen.md` always; `experimente.md` when an experiment is planned; `animationen.md` when an animation is planned; `begriffe.md` for the glossary.
3. **Plan** - the base 5 lines plus 4 physics lines: quantities with symbol and unit · data and expected results with their digits · experiment with hazards and measures · model used. Fix all numbers here; files only copy them.
4. **Create** each output from the base template, pair by pair (German line, then its English line).
5. **Self-check every task and answer** - before the layout check, for each task and each number:
   - solve it a second time by another way (other formula, energy instead of force, estimate, graph) - both results agree;
   - carry the units through the calculation - the result's unit follows from the inputs;
   - count significant digits of data and result; German comma, English point;
   - compare with a known size (plausibility);
   - same value in Arbeitsblatt, Lösung, Test, Erwartungshorizont, Erklärung, animation captions and figure labels;
   - operator fits what the task demands; the task is solvable with the info box, the allowed aids and what the plan says was taught.
   A task that fails is rewritten, then checked again. Keep the check as a table (task · result · second way · unit · digits · plausible) for the reply.
6. **Layout check** - `python <base skill dir>/scripts/check_material.py <folder>` (fix every FAIL, read every `?`), then `python <this skill dir>/scripts/check_einheiten.py <folder>` (every `?` line: fix it or state why it is right). Then look at each file once: formulas readable (sub/superscripts, no line break between number and unit), figure labels match the text, answer space fits a calculation, print preview on A4 (no task split over two pages, no page left mostly empty by a box that cannot break). Animation: open it, press → after a click on Weiter, and screenshot every step - each shows its caption, and no label is covered by a moving part or cut off (`references/animationen.md`; no script checks this).
7. **Hand over** - reply with: files (relative paths), KC reference, the self-check table, safety notes, every `check:` that applies. Offer the review: "Soll `darshan-singh-meel-schule-physik-review` das Material prüfen?" - run it only on a yes.

## References (load only what the task needs)
| File | Read when |
|---|---|
| `references/sek1.md` | Sek I material: Kompetenzbereiche, Bildungsstandards, Inhaltsfelder with both stages, how to cite |
| `references/oberstufe.md` | E-Phase and Q1-Q4: Themenfelder, GK/LK split, Bildungsstandards S/E/K/B, Basiskonzepte, Landesabitur frame |
| `references/konventionen.md` | always: units, notation, digits, constants, solution layout, sizes for plausibility, typical student ideas |
| `references/experimente.md` | any experiment: safety limits, safety block, Versuchsprotokoll, measurement uncertainty |
| `references/animationen.md` | an animation is planned: what to show per topic, recipes for the base engine |
| `references/begriffe.md` | glossary and English lines: `DE | EN` terms, false friends |
| `references/examples/geschwindigkeit-jg07/` | finished set Sek I (Jg. 7, Geschwindigkeit): Stundenentwurf, Arbeitsblatt with Schülerexperiment and safety block, Lösung with t-s diagram, Animation - copy the level of detail |
| `references/examples/federpendel-q2-gk/` | finished Klausur task Oberstufe (Q2.1 GK, Federpendel, 30 BE): Test + Erwartungshorizont with part points, AFB table, 15-point key |
| `references/sources.md` | where each fact comes from; what is not verified |

Script: `scripts/check_einheiten.py <file-or-folder>` - decimal sign per language, number glued to unit, non-SI unit spellings, missing superscripts, numbers that differ between a German line and its English line.
