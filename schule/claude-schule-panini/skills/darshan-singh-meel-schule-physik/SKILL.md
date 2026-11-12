---
name: darshan-singh-meel-schule-physik
description: Physics teaching material for the Gymnasium in Hessen - Sekundarstufe I (Kerncurriculum Physik, 9 Inhaltsfelder) and Oberstufe (KCGO Physik, E-Phase and Q1-Q4, Grundkurs and Leistungskurs) - as lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations for students and step animations (motion, waves, circuits, fields), in German with the closest natural English sentence under every line. Checks units, significant figures and plausibility of every number and adds a safety block to every experiment. Use with darshan-singh-meel-schule whenever physics material is created or changed. Triggers - "Physik", "Physikstunde", "Physik Arbeitsblatt", "Physik Klausur", "Physik Lernkontrolle", "Physik-Versuch", "Physik Schülerexperiment", "Physik Versuchsprotokoll", "Mechanik", "Elektrizitätslehre", "Stromkreis", "Optik", "Schwingungen", "Wellen", "elektrisches Feld", "Induktion", "Quantenphysik", "Kernphysik", "t-s-Diagramm", "Physik zweisprachig"; "physics lesson", "physics worksheet", "physics test", "physics exam with marking scheme", "physics experiment", "physics lab report", "circuit", "waves animation", "bilingual physics".
---


# Physik (Hessen, Gymnasium: Sek I + Oberstufe)
Load `darshan-singh-meel-schule` first (formats, templates, folder, language, grading, operators, process, rubric) · this skill adds physics only.

## Scope
| Level | Curriculum | Read |
|---|---|---|
| Sek I, Jg. 5/6-10 (G9) | KC Hessen Sek I Gymnasium Physik: 4 Kompetenzbereiche, 9 Inhaltsfelder, 2 stages | `references/sek1.md` |
| E-Phase | KCGO Physik E.1-E.7 (E.1-E.3 binding) | `references/oberstufe.md` |
| Q1-Q4, GK/LK | KCGO Q1.1-Q4.5 (9 binding Themenfelder; Q4.6: check: KCGO PDF) | `references/oberstufe.md` |

Folder: `unterricht/physik/<stufe>/<thema>/` · `<stufe>` = `jg07` · `e` · `q2-gk` · `q3-lk`.

## Rules
- Curriculum: Sek I → Kompetenzbereich + Teilbereich + Bildungsstandard (end Jg. 9/10) + Inhaltsfeld + stage · KC sets no year → take Fachcurriculum of user or place by stage → placement stated in Stundenentwurf as fact (`sek1.md`). Oberstufe → Kurshalbjahr.Themenfeld · GK/LK · standard code (`S 7`, `E 4`) · LK-only content never in GK.
- Quantity = number + unit, every line, every file · SI + `references/konventionen.md` · symbols as KCGO/Formelsammlung · new symbol named on first use.
- Digits: write the digits meant (`0,200 kg`) · result = least precise input · rounding only at end · Sek I stage 1: "sinnvoll runden", no term.
- Decimal: DE comma (`1,26 s`) · EN point (`1.26 s`) · same digits.
- Plausibility: compare every result with a known size (`konventionen.md` "Größenordnungen") · invented data follow the law, realistic scatter, label `erfundene Messwerte`.
- Model: name it (Strahlenmodell, Teilchenmodell, Feldlinienbild, Massepunkt) · from Jg. 9 one limit · drawings are not reality → say so in caption.
- Experiment: type (Schüler · Demonstration · Simulation) · material · set-up sketch · safety block (hazard · measure · who acts · stop rule) · limits `references/experimente.md` · never propose what it forbids for students.
- Test: "Hilfsmittel" lists aids (Taschenrechner, Formelsammlung) · formula neither allowed nor known by heart → given in material.
- Animation → motion/change over time (bodies + diagram, waves, charge carriers, fields, technical systems) · static law (formula, unit table) → figure · `references/animationen.md`.
- Terms `DE | EN` from `references/begriffe.md` · false friends binding (`Impuls` = momentum, `Spannung` = voltage, `Leistung` = power).

## Process
1. Setup: base questions (subject = Physik answered) + in same prompt (≤4 open, else second prompt):
   - Experiment: Schülerexperiment in Gruppen (rec) · Demonstration · Simulation/Animation instead · none.
   - Oberstufe: course GK (rec) · LK · E-Phase.
   - Tests: aids Taschenrechner + Formelsammlung (rec) · Taschenrechner only · none.
   - Sek I: ask Jahrgang only if user gave no year.
2. Read: `sek1.md` | `oberstufe.md` · `konventionen.md` always · `experimente.md` (experiment) · `animationen.md` (animation) · `begriffe.md`.
3. Plan: base 5 lines + quantities (symbol, unit) · data and expected results with digits · experiment with hazards, measures · model → fix all numbers here, files only copy.
4. Create from base template, pair by pair (DE line → EN line).
5. Self-check every task and answer → each number: solve a second way (other formula, energy vs force, estimate, graph) · carry units through · count digits, comma/point · plausibility · same value in Arbeitsblatt, Lösung, Test, EH, Erklärung, captions, figure labels · operator fits demand · solvable with info box, aids, taught content → fail = rewrite, re-check · keep table (task · result · second way · unit · digits · plausible) for reply.
6. Layout check: `python <base skill dir>/scripts/check_material.py <folder>` (FAIL = fix · `?` = read) → `python <this skill dir>/scripts/check_einheiten.py <folder>` (`?` = fix or justify) → each file once: formulas readable, no break between number and unit, figure labels match text, answer space fits, A4 preview (no task split, no mostly empty page) · animation: open, → after click on Weiter, screenshot every step (caption shown, no label covered/cut) · no script checks this.
7. Hand over: files (relative) · KC reference · self-check table · safety notes · every `check:` → offer "Soll `darshan-singh-meel-schule-physik-review` das Material prüfen?" · run only on yes.

## References (load only what the task needs)
| File | Read when |
|---|---|
| `references/sek1.md` | Sek I: Kompetenzbereiche, standards, Inhaltsfelder, citing |
| `references/oberstufe.md` | E/Q: Themenfelder, GK/LK split, standards S/E/K/B, Basiskonzepte, Landesabitur frame |
| `references/konventionen.md` | always: units, notation, digits, constants, solution layout, sizes, student ideas |
| `references/experimente.md` | any experiment: limits, safety block, Versuchsprotokoll, uncertainty |
| `references/animationen.md` | animation: content per topic, engine recipes |
| `references/begriffe.md` | glossary, English lines, false friends |
| `references/examples/geschwindigkeit-jg07/` | finished Sek I set (Stundenentwurf, Arbeitsblatt + Schülerexperiment, Lösung, Animation) |
| `references/examples/federpendel-q2-gk/` | finished Klausur Q2.1 GK (Test + EH, AFB table, 15-point key) |
| `references/sources.md` | fact sources · unverified items |

Script `scripts/check_einheiten.py <file-or-folder>` → decimal sign per language · number glued to unit · non-SI spellings · missing superscripts · numbers differing DE vs EN.
