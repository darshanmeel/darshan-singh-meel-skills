# Erdkunde review: subject checks

Used with the base rubric. Letters are cited in findings (`C3`). Subject references: `darshan-singh-meel-schule-erdkunde/references/`.

## A Numbers (recompute all)
| # | Check |
|---|---|
| A1 | Sums, means, differences, shares, rates in tasks and solutions recomputed from the printed values; rounding stated and applied the same way everywhere |
| A2 | Units present and right: °C, K (differences), mm, km², Einw./km², ‰ vs %, percentage points vs per cent |
| A3 | German decimal comma in German lines, decimal point in English lines; thousands separated consistently |
| A4 | Scale tasks: map length × scale number; unit conversion cm → m → km shown in the solution |
| A5 | Rates: natural increase = birth rate − death rate; density = inhabitants ÷ area; change in % relative to the old value |
| A6 | Time zones: 15° per hour, east ahead; date line direction |
| A7 | Orders of magnitude plausible (a city density of 40 Einw./km², a river 60 000 km long = finding) |
| A8 | Printed points added by hand: `/ n P` of every task, points column and sum of the Erwartungshorizont, AFB table (points and %, sum 100 %), grade key against the total; test and Erwartungshorizont carry the same points and AFB per task. `OK` from the script does not replace this |

## B Climate diagram
| # | Check |
|---|---|
| B1 | Re-run `klimadiagramm.py` with the values printed in the material; key values (annual mean, sum, range, warmest/coldest month, arid months) equal the solution |
| B2 | Scale 10 °C = 20 mm; compression above 100 mm marked, no °C label above 50; both axes labelled with unit; months J-D (southern hemisphere: stated when the year starts in July) |
| B3 | Header: station, height, annual mean, annual sum; under the material: source, reference period, rounding |
| B4 | Every reading a task asks for is possible at print size (grid lines every 10 °C / 20 mm, or the value table is given) |
| B5 | Humid/arid statements follow N < 2T month by month; "arid" not used for "hot", "humid" not for "wet" |
| B6 | Annual mean from rounded monthly values vs official annual value: which one is printed is stated |
| B7 | Classification into a climate zone uses the criteria taught (info box), not unstated thresholds |

## C Maps, profiles, diagrams
| # | Check |
|---|---|
| C1 | Own SVG; no raster map, no embedded screenshot (`<image>`, `data:image` of a map); sketch labelled as simplified |
| C2 | Title, legend complete (every symbol, pattern and line used), scale bar or "nicht maßstabsgetreu", north arrow or graticule, year, source |
| C3 | Scale bar length fits the drawing (measure two known points); distances asked in tasks give the solution's value |
| C4 | Places at the right relative position (N-S, W-E order, side of a river/coast, neighbouring states); coordinates given match the place |
| C5 | Areas not distinguished by colour alone; labels readable in black-and-white print, at least 10 pt |
| C6 | Diagram axes: quantity and unit, zero or marked break, equal intervals; pie shares sum to 100 % |
| C7 | Population pyramid: men left, women right, 5-year groups, unit, year, area |
| C8 | Profile: both scales, Überhöhung named, direction |
| C9 | Disputed borders dashed and labelled; current state names |

## D Sources and data
| # | Check |
|---|---|
| D1 | Every material has a source line: provider, data set, period/year, retrieval year; or "erfundene Daten / invented data" |
| D2 | Source is official (list in the subject `sources.md`); values spot-checked against it when reachable - else "not checked: source not opened" |
| D3 | Year of data fits the statement in the task ("heute", "aktuell" with data older than 5 years = Should) |
| D4 | Texts, cartoons, photo descriptions: written for the task or with author, medium, date; nothing copied from textbooks, atlases, Abitur papers |
| D5 | Same data set used in worksheet, solution, explanation, animation |

## E Curriculum fit
| # | Check |
|---|---|
| E1 | Sek I: Kompetenzbereich and Kompetenzerwartung quoted as in `sek1.md`, stage "Ende Jg. 9/10"; Inhaltsfeld is one of the six |
| E2 | Oberstufe: standard code exists (RO1-5, MA1-7, BB1-4, K1-5); Themenfeld number and title as in `oberstufe.md`; half-year fits the course |
| E3 | GK material has no `L` content; LK Klausur includes it only if taught |
| E4 | Binding status claimed for a Themenfeld is right (E: 1, 2, 4, 5; Q1-Q3: 1 and 2; rest by Erlass → `check:`) |
| E5 | Year placement in Sek I marked as Fachcurriculum decision when the default table was used |
| E6 | Basiskonzept named fits the task (scale change, Raumkonzept, sustainability dimensions) |
| E7 | Sek I material: no KCGO standard code (RO, MA, BB, K) and no content that `oberstufe.md` gives only for a Themenfeld of the Oberstufe or as `L` |
| E8 | KC reference is printed in a teacher file (Stundenentwurf, Lösung or Erwartungshorizont), not only in the hand-over text |

## F Tasks and wording
| # | Check |
|---|---|
| F1 | Each task names Raum, scale level and year, or the material does and the task names the material |
| F2 | Order AFB I → III; describe, explain and judge are separate sub-tasks; the solution to "beschreibe" contains no cause |
| F3 | Judgement tasks name or ask for criteria; solution gives criteria, both directions where open, and one model answer |
| F4 | Sustainability judgements use the four dimensions; missing dimension named |
| F5 | No determinism ("wegen des Klimas sind die Menschen ..."), no single-cause migration, no continent as a country, no wording from the avoid list |
| F6 | Models labelled as models; limit named from Jg. 9 |
| F7 | Each material is used by a task; no task needs knowledge that neither info box, material nor the stated earlier lessons give |

## G Bilingual and terms
| # | Check |
|---|---|
| G1 | Terms as in `begriffe.md` (scale, key, precipitation, annual temperature range, natural increase, location factor ...); false friends list |
| G2 | Operators: official pair from the base list (beschreiben → describe, erklären → explain, beurteilen → assess, überprüfen → check critically ...) |
| G3 | Place names: German in the German line; English exonym only where established (Köln → Cologne; Frankfurt am Main stays) |
| G4 | Map and diagram labels DE / EN or carried by the caption; legend bilingual |
| G5 | Numbers: `20,5 °C` ↔ `20.5 °C`; `1 : 50 000` identical |

## H Animation
| # | Check |
|---|---|
| H1 | Process, not a still: each step changes the picture |
| H2 | Directions and order right (plate motion arrows, wind direction, sun position, sequence of phases) |
| H3 | Values in captions equal worksheet and solution |
| H4 | Label "Modell" and the stated limit; time compression or missing scale named |
| H5 | Base area 10 (controls, captions, reduced motion, print frames) |

## Facts for recomputing (school level; verify beyond this in an official source)
- Earth: axis tilt about 23.5°; rotation 24 h → 15° per hour; equator about 40 000 km; mean radius about 6 370 km.
- Layers (rounded): crust 5-70 km; mantle to about 2 900 km; outer core (liquid) to about 5 100 km; inner core (solid).
- Plate motion: a few centimetres per year.
- Latitude circles: tropics about 23.5° N/S; polar circles about 66.5° N/S.
- Climate diagram: 10 °C = 20 mm; arid when N < 2T.
- Anything else (population figures, HDI values, areas, heights, record values): open the source named in the material; if none or not reachable → `not checked`.

## Common defects found in Erdkunde material
- Diagram drawn with other values than the table next to it.
- Annual sum or mean copied from a different reference period than the monthly values.
- "Describe" solution that explains; "explain" task answerable by copying the info box.
- Legend missing one pattern; scale bar copied from another drawing.
- English line uses "card" for Karte, "measure" for Maßstab, "humid" explained as "wet".
- Push/pull table mixing causes and consequences.
- Raumbeispiel data from different years compared without saying so.
