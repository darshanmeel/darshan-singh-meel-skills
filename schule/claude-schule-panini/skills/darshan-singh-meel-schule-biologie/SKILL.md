---
name: darshan-singh-meel-schule-biologie
description: Biologie teaching material for Gymnasium in Hessen - Mittelstufe (Sek I, Jg. 5-10, Kerncurriculum) and Oberstufe (KCGO, E-Phase, Q1-Q4, Grundkurs and Leistungskurs) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations for students, experiment sheets with safety block and expected observations, and step animations of processes (cell division, osmosis, enzymes, protein biosynthesis, action potential). German text with the closest English sentence under every line, subject terms DE | EN (Bili option). Use for any request to plan, write or explain Biologie lessons or material; load darshan-singh-meel-schule alongside. Triggers - "Biologie", "Bio-Stunde", "Biologieunterricht", "Arbeitsblatt Biologie", "Klausur Biologie", "Bio LK", "Bio GK", "Versuchsprotokoll", "Mikroskopieren", "Zellbiologie", "Genetik", "Evolution", "Ökologie", "Neurobiologie", "Stoffwechsel", "Mitose", "Bili Biologie"; "biology lesson", "biology worksheet", "biology test", "lab sheet", "cell division animation", "bilingual biology".
---

# Biologie (Hessen) · Sek I · Oberstufe
Load `darshan-singh-meel-schule` first (formats, folders, DE + EN rule, grading, operators, `check_material.py`) → this file adds the subject.

## Scope
- Sek I Jg. 5-10 · `jg05`…`jg10` · `references/sek1.md`
- E · `e` · Q1-Q4 GK/LK · `q1-gk`…`q4-lk` · `references/oberstufe.md`
- Output `unterricht/biologie/<stufe>/<thema>/` · not covered: Grundschule, Realschule, Hauptschule.

## Rules
- KC cite → Sek I: Kompetenzbereich · Teilbereich · Kompetenzerwartung (Ende Jg. 6 | Ende Jg. 9/10) · Inhaltsfeld → Oberstufe: Standard code (`S 7`, `E 4`, `K 9`, `B 8`) · `<Kurshalbjahr>.<Nr> <Themenfeld>` · GK/LK → wording only from references, else `check: <KC PDF>`.
- GK never gets LK-only content · LK may use both.
- Sek I KC has no year plan → year from school Fachcurriculum: ask, or place by stage and say so.
- Name the system level (Molekül · Zelle · Gewebe · Organ · Organismus · Population · Ökosystem) → mark each change.
- Causal, not final: no `damit`, `um zu`, "die Natur hat…" · proximate ≠ ultimate cause (KCGO K 7, K 8).
- Model ≠ reality → label every model, scheme, animation · name one limit from Jg. 9.
- `Beobachtung` and `Deutung` = separate fields · no explanation in the observation.
- Diagrams → axis = quantity + unit · independent variable on x · source or "erfundene Daten / invented data" under each set · plausible magnitude.
- Experiment sheet → safety block + expected observation (`fachpraxis.md`) → draft only; print: does not replace the Gefährdungsbeurteilung.
- Sensitive topics (Sexualität, Humangenetik, Trisomie 21, Schwangerschaftsabbruch, Sucht, Evolution + Religion) → factual, respectful · invented families/pedigrees · no judging persons · Sexualerziehung → check: HSchG § 7 + Hessen Lehrplan (parents informed first).
- Terms → German first, English from `begriffe.md` · scientific names italic (`<i>…</i>`) · genes italic, proteins not.

## Process
1. Setup → base questions, one AskUserQuestion (max 4, rec first) + subject options:
   - Jahrgang/Kurs · Sek I year | E/Q1-Q4 + GK/LK
   - Thema · 3 topics from the Inhaltsfeld/Themenfeld
   - Versuch (if topic allows) · Schülerversuch (rec if student-allowed in `fachpraxis.md`) · Lehrerdemonstration · kein Versuch, Daten auswerten
   - Still open → 2nd prompt: Sprache · Zeit · Differenzierung (base defaults)
2. Read level reference · `fachpraxis.md` · `begriffe.md` · base files per its SKILL.md.
3. Plan in 5 lines (base step 3) + 1: system level(s) · model · experiment or data source.
4. Create from base templates, pair by pair (DE line → EN line) · example `references/examples/mitose-jg09/`.
5. Self-check → solve each task blind → compare · tick: fact · operator + AFB · solvable from info box + earlier lessons · level (GK/LK, stage) · observation ≠ interpretation · numbers, units, chromosome counts, equations balanced · figure + animation = text.
6. Layout → `python <base skill dir>/scripts/check_material.py unterricht/biologie/<stufe>/<thema>/` → fix every error, read every `?` → by eye: answer space fits · labels inside figures · nothing by colour alone (also captions: `dicke Striche`) · labels readable in key frames (≥22 units) · no task split (`class="aufgabe teil"`) · A4 preview.
7. Hand over → files (relative) · KC ref · every `check:` used · offer `darshan-singh-meel-schule-biologie-review` (rec for tests, Klausuren).

## References
- `references/sek1.md` · Jg. 5-10: Kompetenzbereiche, Kompetenzerwartungen, Basiskonzepte, 8 Inhaltsfelder
- `references/oberstufe.md` · E, Q1-Q4: Standards S/E/K/B + codes, Themenfelder GK/LK, binding rules
- `references/fachpraxis.md` · experiments, safety (RiSU, Biostoffe, animals, human material), protocol, diagram rules, typical errors, animation choice
- `references/begriffe.md` · glossary DE | EN, false friends
- `references/examples/mitose-jg09/` · finished worksheet + solution + animation
- `references/sources.md` · official pages, verified vs `check:`
