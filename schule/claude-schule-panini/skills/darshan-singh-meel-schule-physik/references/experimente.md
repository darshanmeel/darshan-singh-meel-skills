# Experiments: safety, protocol, measurement

Legal frame (read; `sources.md`): in Hessen the "Verordnung über die Aufsicht über Schülerinnen und Schüler" makes Teil I of the KMK "Richtlinie zur Sicherheit im Unterricht" (RiSU) binding. Limits below are from RiSU, Stand 21.09.2023: Teil I (rules) and, where marked, Teil II (advice, Physik: II - 4). This file is planning help, not a hazard assessment: the teacher's Gefährdungsbeurteilung and the school's equipment decide. Anything not listed: check: RiSU Teil I, the section for the activity.

## Experiment types
| Type | Who acts | Use for |
|---|---|---|
| Schülerexperiment (SE) | students in groups of 2-4 | measuring, finding a relation, practising methods (KC Sek I: "führen ... Untersuchungen durch und protokollieren"; KCGO S 4) |
| Demonstrationsexperiment (DE) | teacher, students observe and record | anything above the student limits, expensive or single apparatus |
| Simulation / Animation | students at the screen | not observable, too fast, too slow, too dangerous, not available |
| Gedankenexperiment | all | idealisation, limiting cases |

The plan states the type, the group size, and the number of sets needed.

## Limits from RiSU (Teil I binding in Hessen)
| Area | Rule | RiSU |
|---|---|---|
| Any experiment | a Gefährdungsbeurteilung exists before the activity; protective measures follow from it | I - 0, I - 10.2 |
| Electricity, students | power sources for student experiments: only Schutzkleinspannung or Funktionskleinspannung with safe separation (safety transformer; batteries and accumulators count as equal) | I - 10.3 |
| Electricity, students | students do not experiment with touch-dangerous voltage; exceptions only in the Oberstufe when the goal cannot be reached otherwise, with special equipment (emergency stop at the workplace) - in practice a teacher experiment | I - 10.5 |
| Touch-safe means | below 25 V AC (effective) or 60 V DC; or above that with short-circuit current below 3 mA AC / 12 mA DC; or discharge energy below 350 mJ | I - 10.1 |
| Live parts | no work on parts under touch-dangerous voltage, including bringing measuring leads to them | I - 10.5 |
| Lasers | only classes 1, 1M, 2, 2M (old class 3A); 1M, 2, 2M, 3A: locked away, operated only under the teacher's supervision, students instructed about the eye hazard first, area marked with the laser warning sign and fenced off, set-up so that nobody looks into the direct or reflected beam; 1M, 2M, 3A never with converging optics (lens, magnifier) | I - 9.2 |
| Radioactive sources | licence-bound handling: student participation only under supervision of a fachkundige teacher; licence-free handling: student experiments allowed; X-ray: only Schulröntgeneinrichtungen | I - 8.8, I - 8.9 |
| Mercury | no student experiments with mercury thermometers or manometers | I - 3, Tabellen 3a/3b |
| Capacitors (advice, Teil II) | caution when charging capacitors above 60 V nominal voltage: even sources limited to a few milliamperes can charge them dangerously | II - 4.4 |
| Circuits (advice, Teil II) | do not touch the circuit once the voltage is on; switch off before changing the set-up and right after the experiment; detach leads at the source first; tell students that banana plugs never go into mains sockets; observe the load limits of components and the range of meters | II - 4.4 |

Not read, therefore `check: RiSU`: open flames and gas burners, pressure and vacuum vessels, rotating parts, strong magnets, UV and IR sources, noise levels, hot liquids, loads and falling bodies.

## Safety block (in every Versuchsanleitung and in the lesson plan)
Four lines, each with its English line:

| Line | Content | Example (Federpendel) |
|---|---|---|
| Gefahr / Hazard | what can hurt | Massestück kann herunterfallen; Feder kann zurückschnellen |
| Maßnahme / Measure | what prevents it | Stativ mit Tischklemme sichern; Auslenkung höchstens 5 cm; Füße nicht unter das Pendel |
| Wer / Who | SE or DE; who handles what | Schülerexperiment in Dreiergruppen; eine Person misst die Zeit |
| Stopp / Stop | when to stop and what to do | Feder überdehnt oder Stativ wackelt: Versuch beenden, Lehrkraft rufen |

- General lines that fit most rooms: long hair tied back, bags off the floor, no eating or drinking, set-up checked by the teacher before the power is switched on, power off before rebuilding.
- Never propose for students: mains voltage; open high-voltage sources (Bandgenerator and Influenzmaschine are teacher experiments); looking at the sun or into a laser, also through optics; heating closed vessels; self-built mains devices; liquids near power strips; sources with unknown activity.
- Outdoor and corridor measurements (speed, sound): route free of traffic, no running on stairs, supervision named.
- Electricity at home (homework): only batteries up to 9 V; never "an der Steckdose".
- A safety line is concrete for the set-up; "Vorsicht beim Experimentieren" is not a measure.

## Versuchsprotokoll (student lab report)
| Part (DE / EN) | Content |
|---|---|
| Fragestellung / Question | one question the experiment answers |
| Vermutung / Hypothesis | "Je ..., desto ..." or "Wenn ..., dann ...", with a reason |
| Material / Materials | list with quantities and measuring ranges |
| Aufbau / Set-up | labelled sketch; circuit diagram for circuits |
| Durchführung / Procedure | numbered steps; which quantity is changed, measured, kept constant |
| Sicherheit / Safety | the safety block |
| Beobachtung, Messwerte / Observation, measured values | table with quantity and unit in the header; raw values, not rounded twice |
| Auswertung / Evaluation | diagram, calculation, relation found |
| Genauigkeit / Accuracy | sources of uncertainty, their direction, improvement |
| Ergebnis / Result | answer to the question; hypothesis confirmed or rejected |

- Observation and interpretation stay apart (KC Sek I: "Unterscheidung zwischen Beobachtung und Deutung").
- Worksheet for an experiment: the table is pre-drawn with units; at least 5 measured points for a relation; one repeated measurement.

## Measurement and uncertainty
| Level | Expectation | Source |
|---|---|---|
| Sek I | name error sources, repeat and average, "erörtern die Genauigkeit von Untersuchungsergebnissen"; Stufe 2: "Beurteilung von Messgenauigkeit und dem Einfluss von Messfehlern" | KC Sek I |
| E-Phase | compare with the literature value, discuss the deviation (freier Fall: g) | KCGO E.1 |
| Q-Phase | "berücksichtigen Messunsicherheiten und analysieren die Konsequenzen für die Interpretation des Ergebnisses" | KCGO E 7 |

- Relative deviation = |measured − literature| / literature, in percent, two digits at most.
- Reading uncertainty: half the smallest division (analogue), last digit (digital); stopwatch by hand: about 0,2 s reaction time → measure 10 periods, not one.
- Invented data for a worksheet: generate from the law, add scatter of the size the instrument gives (not all points on the line), keep one digit count per column, label `erfundene Messwerte / invented measured values`.
- Evaluation through a best-fit line through the points; the slope carries a unit.

## Standard experiments by topic (ideas, original set-ups, no textbook copies)
| Topic | Experiment | Type |
|---|---|---|
| Geschwindigkeit | walk or roll 10 m, time with stopwatch; toy car on a marked track | SE |
| Dichte | mass and volume of cuboids, overflow method | SE |
| Stromkreis | lamp, switch, battery; conductors and insulators; series and parallel with two lamps | SE (≤ 12 V) |
| Ohm'sches Gesetz | U-I characteristic of a resistor and a lamp | SE |
| Optik | shadow, pinhole camera, reflection with mirror and light box, refraction at a half-disc, lens image | SE |
| Hebel, Flaschenzug | balance on a lever; force with spring balance | SE |
| Auftrieb | weight in air and in water | SE |
| Wärme | calibrate a thermometer; mixing temperatures; heat conduction of rods | SE (hot water ≤ 60 °C: check: RiSU) |
| Freier Fall, g | fall time with light gates or video analysis | SE/DE |
| Federpendel, Fadenpendel | T against m, D, ℓ; 10 periods | SE |
| Plattenkondensator, Entladekurve | U(t) with large R and C at low voltage | SE (≤ 25 V AC / 60 V DC) |
| Fadenstrahlrohr, Franck-Hertz, Fotoeffekt | high or anode voltage | DE |
| Doppelspalt, Gitter | laser class ≤ 2, beam below or above eye level, screen matt | DE or supervised SE |
| Radioaktivität | counting rate, absorption, distance law with school source | DE (licence rules) |
