---
name: darshan-singh-meel-schule-nwt
description: Teaching material for Naturwissenschaft und Technik (NWT, NaWi-Technik, MINT) in the Mittelstufe of the Gymnasium in Hessen, where it is not a state subject with its own Kerncurriculum but a school offer in the Wahlunterricht (usually Jg. 9-10 in G9) built on the Kerncurricula Physik, Chemie and Biologie - project-style lesson plans, worksheets with solutions, competence checks with marking scheme, explanations and step animations of technical systems (gears, levers, sensors, control loops, energy converters), in German with the closest natural English sentence under every line. Covers the design cycle, technical drawings and block diagrams, units and plausibility, tool and experiment safety. Use with darshan-singh-meel-schule whenever NWT, MINT-Wahlunterricht or science-and-technology project material is created or changed. Triggers - "NWT", "NwT", "Naturwissenschaft und Technik", "NaWi", "Naturwissenschaften", "MINT-Kurs", "Wahlunterricht Naturwissenschaften", "Technik-Projekt", "Konstruktionsaufgabe", "Brücke bauen", "Getriebe", "Sensor", "Messen Steuern Regeln", "Bionik", "Forscherauftrag"; "science and technology lesson", "STEM elective", "engineering design task", "build project worksheet", "technical system animation".
---

# Naturwissenschaft und Technik (Hessen, Gymnasium Mittelstufe)

Load `darshan-singh-meel-schule` first (formats, templates, folder, language rule, process, review rubric). This skill adds what NWT needs: what Hessen offers, curriculum anchors, technical working methods, safety, assessment in the Wahlunterricht, terms, animations. For the physics inside a module also read the references of `darshan-singh-meel-schule-physik` named below.

## What Hessen offers (found on the official pages; details and sources: `references/hessen-nwt.md`)
- **No state subject "Naturwissenschaft und Technik"** at the Gymnasium: neither the Sek I list nor the Oberstufe list of Kerncurricula contains it. Physik, Chemie and Biologie are separate subjects with their own KC.
- **Mittelstufe:** NWT-type courses run as **Wahlunterricht** - a school offer tied to the content of the compulsory subjects; G9: four hours over the Mittelstufe, intended for Jg. 9 and 10; G8: five hours, Jg. 5-9. The only Wahlunterricht with a state KC is Informatik. Content is set by the school's own curriculum.
- **Assessment:** Wahlunterricht outside the foreign languages is not graded with Noten; the report carries "teilgenommen", "mit Erfolg teilgenommen" or "mit gutem Erfolg teilgenommen". No Klassenarbeiten.
- **Oberstufe:** no KCGO for NWT or Technik at the general Gymnasium → not offered as a course there. Oberstufe requests go to the Physik, Chemie, Biologie or Informatik skill. (Technical courses of the berufliches Gymnasium have their own KC: out of scope.)
- Consequence: this skill writes **Mittelstufe** material, default Jg. 9-10, and cites the KC of the science subject that carries the module plus the school's NWT curriculum when the user supplies it.

Output folder: `unterricht/nawi-technik/<stufe>/<thema>/` (`jg09`, `jg10`; younger groups when the school places the course there).

## Rules
- **Curriculum anchor.** Every module names (1) the carrying subject and its KC reference (Kompetenzbereich, Bildungsstandard, Inhaltsfeld) from `references/module.md`, and (2) the line `Wahlunterricht - schulinternes Curriculum` with the school's module name if known. Never cite an "NWT-Kerncurriculum Hessen": none exists.
- **Not ahead of the compulsory subject.** A module uses what Physik, Chemie and Biologie have taught by that year, or teaches the missing piece itself in the lesson (stated under Lernvoraussetzungen). It does not pre-empt Oberstufe content.
- **A product or a measured answer.** Each module ends in something built, measured or decided: a model, a data set with evaluation, a justified design choice. Tasks follow the design cycle or the experiment cycle (`references/technik.md`).
- **Science inside is exact.** Quantities with units, digits, plausibility as in the physics skill's `konventionen.md`; chemical and biological statements only as far as the KC of that subject goes. Invented data are labelled.
- **Technical representation.** Sketches with dimensions in mm, block diagrams (Eingabe → Verarbeitung → Ausgabe), circuit diagrams with standard symbols, tables of requirements. A drawing task states the scale.
- **Safety.** Every practical task has the safety block (hazard · measure · who · stop). Tools, soldering, glue, cutting, electricity, living organisms and chemicals within the limits of `references/technik.md`; a hazard not covered there → `check: RiSU`.
- **Assessment fits the Wahlunterricht.** Default: criteria grid for product, process and documentation, mapped to the three Vermerke; no Noten key unless the user says the school grades the course. A written check is a `Lernkontrolle` in the base test template with the Vermerk key.
- **Animation** when a technical system moves or a signal flows: gear and chain drives, levers and pulleys, motor and generator, sensor → controller → actuator, a control loop settling, an energy chain. Rules: physics skill `animationen.md` plus `technik.md` (system animations).
- **Terms.** `references/begriffe.md` for technology terms; physics terms from the physics skill's `begriffe.md`.

## Process (fixed)
1. **Setup** - base questions (Fach = NaWi-Technik). Add, at most 4 open questions per prompt:

   | Question | Options |
   |---|---|
   | Course frame | Wahlunterricht Jg. 9/10, ohne Noten (Recommended) · Wahlunterricht in anderem Jahrgang · AG/Projektwoche · Kurs mit Noten (Schulbeschluss) |
   | Module | 3 modules from `references/module.md` that fit the year, or free text |
   | Work form | Konstruktionsaufgabe mit Produkt (Recommended) · Experiment mit Auswertung · Recherche und Bewertung |
   | Material at hand | Standard-Sammlung Physik (Recommended) · Baukasten/Mikrocontroller vorhanden · nur Alltagsmaterial |

   Ask for the school's NWT curriculum (module title, year, hours); without it use the module table; the Stundenentwurf states module and year as facts (`Modul der Schule: Mobilität - Fahrradgetriebe`, Jg. 9) and the hand-over reply names the table as the basis.
2. **Read** `references/hessen-nwt.md` once, `references/module.md` for the module, `references/technik.md` always; physics `konventionen.md` for calculations, `experimente.md` for experiments, `animationen.md` for animations; `references/begriffe.md` for the glossary.
3. **Plan** - base 5 lines plus: product or question · requirements (3-5, measurable) · quantities with units and expected values · tools, materials and hazards · carrying subject and KC anchor · how it is assessed (criteria → Vermerk).
4. **Create** from the base templates, German line then English line. Double lessons (90 min) are the default for practical work: two Erarbeitung/Sicherung rounds.
5. **Self-check every task and answer** - solve each task twice (second way or estimate); units carried through; digits; plausibility against real parts (tooth counts, voltages, loads, sizes); every requirement testable; build instructions followed step by step in the head with the listed material only; same values in all files, figures and animation captions; each practical step has its safety line.
6. **Layout check** - `python <base skill dir>/scripts/check_material.py <folder>`; `python <physics skill dir>/scripts/check_einheiten.py <folder>`; fix FAIL lines, resolve `?` lines; look at drawings and tables in the print preview (table columns wide enough to write in); animation: open it, press → after a click on Weiter, and screenshot every step - each shows its caption, no label covered by a moving part or cut off (physics `animationen.md`; no script checks this).
7. **Hand over** - reply with files (relative paths), KC anchor and the note "Wahlunterricht, schulinternes Curriculum", self-check table, safety notes, open `check:` lines. Offer `darshan-singh-meel-schule-nwt-review`; run it only on a yes.

## References
| File | Read when |
|---|---|
| `references/hessen-nwt.md` | always, once: what Hessen offers, legal frame, assessment, how to cite |
| `references/module.md` | choosing and anchoring a module: 12 modules with KC anchors in Physik, Chemie, Biologie, product, animation idea |
| `references/technik.md` | always: design cycle, requirement lists, technical drawing, system diagrams, tool and material safety, assessment grid |
| `references/begriffe.md` | glossary and English lines: technology terms `DE | EN` |
| `references/examples/kettengetriebe-jg09/` | finished set (Jg. 9, Kettentrieb am Fahrrad, 90 min): Stundenentwurf with Wahlunterricht anchor, Arbeitsblatt with measuring experiment and open design task, Lösung, Animation of the drive - copy the level of detail |
| `references/sources.md` | where each fact comes from; what is not verified |
