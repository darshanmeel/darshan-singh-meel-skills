# Technical working methods, safety, assessment

Didactic lines are working rules of this skill, not Hessen law. Safety lines: RiSU (KMK, Stand 21.09.2023), Teil I binding in Hessen; section named per line; anything else `check: RiSU`.

## Two cycles
| Design cycle (Konstruieren) | Experiment cycle (Forschen) |
|---|---|
| 1 Problem / Auftrag | 1 Fragestellung |
| 2 Anforderungen (messbar) | 2 Hypothese |
| 3 Ideen sammeln, Skizzen | 3 Planung: was wird verändert, gemessen, konstant gehalten |
| 4 Entscheiden (Kriterien) und Entwurf mit Maßen | 4 Durchführung, Protokoll |
| 5 Bauen | 5 Auswertung |
| 6 Testen gegen die Anforderungen | 6 Genauigkeit, Deutung |
| 7 Optimieren (eine Änderung pro Test) | 7 Antwort auf die Frage |
| 8 Dokumentieren, Präsentieren | 8 Dokumentieren, Präsentieren |

- A lesson states which step it serves. A worksheet covers one or two steps, not the whole cycle.
- English lines: design cycle = problem, requirements, ideas, design, build, test, optimise, document.

## Requirements (Anforderungsliste)
| Rule | Example (Brücke) |
|---|---|
| 3-5 requirements, each measurable, with value and unit | Spannweite 40 cm · trägt 1,0 kg in der Mitte · Eigenmasse höchstens 100 g · nur Papier A4 und Klebstoff · Bauzeit 60 min |
| Mark each as `Muss` or `Wunsch` | Muss: Spannweite, Last · Wunsch: Eigenmasse unter 60 g |
| Each requirement has its test | Last: Massestücke in 100-g-Schritten, 10 s halten |
| One figure of merit for comparison | Tragfähigkeit ÷ Eigenmasse |

A task "Baue eine stabile Brücke" without numbers is rewritten.

## Technical representation
| Form | Rules |
|---|---|
| Skizze | by hand, pencil, proportional, main dimensions in mm, parts labelled; one view is enough in Jg. 5-8 |
| Technische Zeichnung (Jg. 9-10) | views (Vorderansicht, Draufsicht, Seitenansicht), scale stated (`M 1:2`), dimensions in mm without the unit at each number, dimension lines outside the part, visible edges thick, hidden edges dashed, centre lines dash-dotted |
| Stückliste | Pos. · Anzahl · Benennung · Werkstoff · Maße |
| Blockdiagramm | boxes with one function each; arrows labelled with what flows: Stoff, Energie, Information; Eingabe → Verarbeitung → Ausgabe |
| Regelkreis | Sollwert → Regler → Stellglied → Strecke → Sensor → Vergleich; closed loop drawn as a loop |
| Schaltplan | standard symbols, lines horizontal/vertical, supply at the left or top; pin names for microcontrollers |
| Programmablauf | flow chart or pseudocode before code; code in one language, comments German + English line |
| Wirkungskette / Energieflussdiagramm | arrow width proportional to the energy; losses branch off |
| Messprotokoll | table with quantity and unit in the header, at least 5 values, repeat measurement |

Drawings in files are inline SVG with `aria-label` (German / English); dimensions as text inside the SVG.

## System thinking
- Describe every technical system by purpose, input, output, parts, and what flows between parts.
- Transmission ratios: state the definition used. Convention-free form for gears and chain drives: `n₁·z₁ = n₂·z₂` (n = turns, z = teeth; 1 = driving, 2 = driven). Belt and friction drives: `n₁·d₁ = n₂·d₂`. The engineering ratio `i = n₁/n₂ = z₂/z₁` only when introduced, with the sentence "i > 1 = ins Langsame".
- "Goldene Regel der Mechanik": what is saved in force is added in distance; work stays the same without friction. Efficiency below 100 % in every real machine - a task that yields more is wrong.
- Sensors deliver a value with a unit and a range; a threshold needs a hysteresis or the actuator flutters - mention it from Jg. 9.

## Safety (practical work)
Every practical task carries the safety block of the physics skill (`experimente.md`): Gefahr · Maßnahme · Wer · Stopp.

| Area | Rule | RiSU |
|---|---|---|
| Machines, general | students work only on machines allowed for their year (Tabelle 4: per device and Jahrgangsstufe 5/6, 7/8, from 9: under supervision, partly independent, independent); instruction by a fachkundige teacher first, repeated regularly; visual and function check of the device before use | I - 4.3.3, Tabelle 4 |
| Machines students never operate | electric sawing machines of every kind (exceptions: hand-held jigsaw and Dekupiersäge), electric planing machines, electric milling machines (exception: coordinate table with cutter shank ≤ 3 mm), chopping and splitting machines, lever plate shears | I - 4.3.2 |
| Per-device permission | which year may use drill, hot-glue gun, soldering iron, 3D printer, hot-wire cutter and how closely supervised | check: RiSU Tabelle 4 (the table was read; its columns could not be assigned to the rows reliably) |
| Soldering | ordinary soft soldering is allowed at schools; window ventilation is normally enough; lead-free solder only | I - 4.5 |
| 3D printing | follow the manual; printer in a separate room where possible; avoid ABS (more ultrafine particles and vapours) | I - 4.7.1 |
| Electricity | students: only safety extra-low voltage sources; touch-safe below 25 V AC / 60 V DC; batteries count as equal sources | I - 10.1, I - 10.3, I - 10.5 |
| Lasers (pointer, cutter) | classes 1, 1M, 2, 2M only; rules as in the physics skill | I - 9.2; cutters: check: I - 4.8 |
| Hazardous substances | household substances only by default; anything with a hazard pictogram needs the teacher's Gefährdungsbeurteilung and the student restrictions | check: RiSU I - 3, Tabelle 3b |
| Organisms, water samples, food | hygiene, no tasting, hand washing; living animals | check: RiSU I - 6, I - 7 |
| Wood, metal, plastics by hand | clamped workpiece, cut away from the body, eye protection when chips fly, no loose sleeves or hair at rotating tools | check: RiSU II - 5 |
| Load tests | loads low above the table or floor, feet and hands out of the fall line, catch box under the load, eye protection for brittle material | skill rule |
| Batteries and accumulators | no short circuit; lithium cells only in devices or with protection circuit; damaged cells are not used | skill rule; check: RiSU |
| Hot glue, hot wire, soldering iron | heat-resistant base, stand for the hot tool, cooling time, burns: cool with water, tell the teacher | I - 4.3.3 (general); II - 1 advice: check |

- Home tasks: only cutting with scissors, cold glue, batteries up to 9 V. Never mains, never power tools.
- The plan names who supervises which station when stations with tools run in parallel.

## Assessment in the Wahlunterricht
Law: report entry "teilgenommen", "mit Erfolg teilgenommen" or "mit gutem Erfolg teilgenommen" (`hessen-nwt.md`). No state rule maps performance to the three Vermerke: the grid below is a proposal - print "Vorschlag - an den Beschluss der Schule anpassen" under it.

| Area (weight) | Criteria (each 0-3 points) |
|---|---|
| Produkt (40 %) | meets the Muss requirements · figure of merit · workmanship · function shown in the test |
| Prozess (30 %) | planning visible (requirements, sketch) · tests documented, one change per test · safe and careful work · teamwork with roles |
| Dokumentation (30 %) | drawing or diagram correct and labelled · measured values with units · evaluation and conclusion · subject terms, sources |

| Vermerk | Proposal |
|---|---|
| mit gutem Erfolg teilgenommen | from 80 % of the points |
| mit Erfolg teilgenommen | from 50 % |
| teilgenommen | below |

- Written `Lernkontrolle`: base `test.html` + `erwartungshorizont.html`; key rows = the three Vermerke (`data-ab` falling, last row 0); AFB mix as in the base; no Noten row unless the school grades the course.
- Group products: one product mark for the group, process and documentation per student.
- Self-assessment sheet with the same criteria before the teacher's assessment.

## System animations (in addition to the physics skill's `animationen.md`)
| System | Show | Must be true |
|---|---|---|
| Gear, chain, belt drive | marks on both wheels turn; counter of turns | turn ratio = z₁/z₂ exactly in every step; chain drive: same sense of rotation; meshing gears: opposite sense |
| Lever, pulley, crane | load and hand move; distances drawn | force × distance equal on both sides (ideal); arrow lengths proportional |
| Motor, generator | coil turns, current direction switches | commutator switches at the dead point; force direction from field and current |
| Sensor → controller → actuator | value on a scale crosses the threshold, signal runs along the arrow, actuator switches | order of cause and effect; delay shown as its own step |
| Control loop | measured value approaches the set value, overshoot optional | value changes only after the actuator acts |
| Energy chain | bars or arrow widths per stage | sum of useful and lost energy equals the input in every step |
| Build sequence | parts appear in assembly order | order can really be built with the listed tools |
