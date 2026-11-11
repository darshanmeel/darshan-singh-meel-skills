---
name: darshan-singh-meel-schule-nwt
description: Teaching material for Naturwissenschaft und Technik (NWT, NaWi-Technik, MINT) in the Mittelstufe of the Gymnasium in Hessen, where it is not a state subject with its own Kerncurriculum but a school offer in the Wahlunterricht (usually Jg. 9-10 in G9) built on the Kerncurricula Physik, Chemie and Biologie - project-style lesson plans, worksheets with solutions, competence checks with marking scheme, explanations and step animations of technical systems (gears, levers, sensors, control loops, energy converters), in German with the closest natural English sentence under every line. Covers the design cycle, technical drawings and block diagrams, units and plausibility, tool and experiment safety. Use with darshan-singh-meel-schule whenever NWT, MINT-Wahlunterricht or science-and-technology project material is created or changed. Triggers - "NWT", "NwT", "Naturwissenschaft und Technik", "NaWi", "Naturwissenschaften", "MINT-Kurs", "Wahlunterricht Naturwissenschaften", "Technik-Projekt", "Konstruktionsaufgabe", "Brücke bauen", "Getriebe", "Sensor", "Messen Steuern Regeln", "Bionik", "Forscherauftrag"; "science and technology lesson", "STEM elective", "engineering design task", "build project worksheet", "technical system animation".
---


# Naturwissenschaft und Technik (Hessen, Gymnasium Mittelstufe)
Load `darshan-singh-meel-schule` first (formats, templates, folder, language, process, rubric) · this skill adds NWT: offer, anchors, technical methods, safety, assessment, terms, animations · physics inside a module → also physics skill references named below.

## What Hessen offers (details + sources: `references/hessen-nwt.md`)
- No state subject NWT at the Gymnasium (not in Sek I or Oberstufe KC lists) · Physik, Chemie, Biologie have own KC.
- Mittelstufe: NWT-type courses = Wahlunterricht (school offer tied to compulsory subjects) · G9: 4 hours over Mittelstufe, Jg. 9-10 · G8: 5 hours, Jg. 5-9 · only Wahlunterricht with state KC = Informatik · content = school's own curriculum.
- Assessment: no Noten outside foreign languages · report: "teilgenommen" · "mit Erfolg teilgenommen" · "mit gutem Erfolg teilgenommen" · no Klassenarbeiten.
- Oberstufe: no KCGO for NWT/Technik at general Gymnasium → route to Physik, Chemie, Biologie or Informatik skill (berufliches Gymnasium Technik: out of scope).
- So: Mittelstufe material, default Jg. 9-10 · cite KC of carrying science subject + school's NWT curriculum if user supplies it.

Folder: `unterricht/nawi-technik/<stufe>/<thema>/` · `jg09` · `jg10` · younger if school places it there.

## Rules
- Anchor: (1) carrying subject + KC reference (Kompetenzbereich, standard, Inhaltsfeld) from `references/module.md` · (2) line `Wahlunterricht - schulinternes Curriculum` + school's module name if known · never cite an "NWT-Kerncurriculum Hessen" (none exists).
- Not ahead: use what Physik/Chemie/Biologie taught by that year, or teach the missing piece in the lesson (under Lernvoraussetzungen) · no Oberstufe content.
- Ends in product or measured answer: model · data set + evaluation · justified design choice · tasks follow design or experiment cycle (`references/technik.md`).
- Science inside is exact: units, digits, plausibility per physics `konventionen.md` · chemistry/biology only as far as that subject's KC · invented data labelled.
- Technical representation: sketches with mm dimensions · block diagrams (Eingabe → Verarbeitung → Ausgabe) · circuit diagrams with standard symbols · requirement tables · drawing task states the scale.
- Safety block (hazard · measure · who · stop) on every practical task · tools, soldering, glue, cutting, electricity, organisms, chemicals within `references/technik.md` limits · uncovered hazard → `check: RiSU`.
- Assessment: criteria grid (product · process · documentation) mapped to the 3 Vermerke · no Noten key unless user says school grades the course · written check = `Lernkontrolle` in base test template with Vermerk key.
- Animation → technical system moves or signal flows (gear/chain drives, levers, pulleys, motor/generator, sensor → controller → actuator, control loop, energy chain) · rules: physics `animationen.md` + `technik.md` (system animations).
- Terms: `references/begriffe.md` · physics terms from physics `begriffe.md`.

## Process
1. Setup: base questions (Fach = NaWi-Technik) + (≤4 open per prompt):
   - Course frame: Wahlunterricht Jg. 9/10 ohne Noten (rec) · other Jahrgang · AG/Projektwoche · Kurs mit Noten (Schulbeschluss).
   - Module: 3 fitting modules from `references/module.md` or free text.
   - Work form: Konstruktionsaufgabe mit Produkt (rec) · Experiment mit Auswertung · Recherche und Bewertung.
   - Material: Standard-Sammlung Physik (rec) · Baukasten/Mikrocontroller · only Alltagsmaterial.
   - Ask school's NWT curriculum (module, year, hours) · none → module table, say so.
2. Read: `hessen-nwt.md` once · `module.md` (module) · `technik.md` always · physics `konventionen.md` (calculations), `experimente.md` (experiments), `animationen.md` (animations) · `begriffe.md`.
3. Plan: base 5 lines + product/question · 3-5 measurable requirements · quantities with units, expected values · tools, materials, hazards · carrying subject + KC anchor · assessment (criteria → Vermerk).
4. Create from base templates, DE line → EN line · practical work = double lesson (90 min), two Erarbeitung/Sicherung rounds.
5. Self-check every task and answer → solve twice (second way/estimate) · units · digits · plausibility vs real parts (tooth counts, voltages, loads, sizes) · every requirement testable · build instructions followed in head with listed material only · same values in all files, figures, captions · safety line per practical step.
6. Layout check: `python <base skill dir>/scripts/check_material.py <folder>` + `python <physics skill dir>/scripts/check_einheiten.py <folder>` → FAIL = fix · `?` = resolve · print preview: drawings, tables (columns wide enough to write in) · animation: open, → after click on Weiter, screenshot every step (caption shown, no label covered/cut) · no script checks this.
7. Hand over: files (relative) · KC anchor + "Wahlunterricht, schulinternes Curriculum" · self-check table · safety notes · open `check:` → offer `darshan-singh-meel-schule-nwt-review` · run only on yes.

## References
| File | Read when |
|---|---|
| `references/hessen-nwt.md` | always, once: offer, legal frame, assessment, citing |
| `references/module.md` | choosing/anchoring a module: 12 modules, KC anchors (Physik, Chemie, Biologie), product, animation idea |
| `references/technik.md` | always: design cycle, requirements, technical drawing, system diagrams, tool/material safety, assessment grid |
| `references/begriffe.md` | technology terms `DE | EN` |
| `references/examples/kettengetriebe-jg09/` | finished Jg. 9 set (Kettentrieb, 90 min): Stundenentwurf, Arbeitsblatt, Lösung, Animation |
| `references/sources.md` | fact sources · unverified items |
