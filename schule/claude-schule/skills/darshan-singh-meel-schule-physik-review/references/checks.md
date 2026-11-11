# Physics checks (added to the base rubric)

Base areas 1-12 stay in force (`darshan-singh-meel-schule/references/review.md`). P1-P12 sharpen areas 1, 2, 3, 5, 7 and 10 for Physik. References named below belong to `darshan-singh-meel-schule-physik`.

## Checks
| # | Area | Check | Must when |
|---|---|---|---|
| P1 | Curriculum level | Sek I: Kompetenzbereich + Teilbereich + Bildungsstandard + Inhaltsfeld + stage as in `sek1.md`, wording as printed. Oberstufe: Kurshalbjahr.Themenfeld, GK/LK, standard code as in `oberstufe.md`. Content belongs to the stated stage or course | reference missing or invented; LK-only content (erhöhtes Niveau) in GK material; Sek I task needs Oberstufe maths or content that the plan does not teach |
| P2 | Every result | own result = material's result for every task: value, unit, sign, direction, digits; solution steps lead to the result; no step skipped that a student needs | any wrong value, unit or sign; a solution that does not answer the question asked |
| P3 | Solvable and unambiguous | all needed data are given (incl. g, constants, sign convention, "Reibung vernachlässigt"); no surplus data that changes the answer; exactly one reading; formula available (known, in the allowed aid, or given) | missing datum; two valid readings with different results; a needed formula neither taught nor given |
| P4 | Units | every quantity with unit in every line; SI spellings; unit carried through the calculation; conversions right (km/h ↔ m/s, cm ↔ m, g ↔ kg, °C ↔ K, eV ↔ J); axis and table headers `Größe in Einheit` | wrong conversion; a result without unit in Lösung or Erwartungshorizont; unit that does not follow from the inputs |
| P5 | Significant figures | data carry the meant digits; result has the digits of the weakest input; no rounding chain (result computed from rounded intermediates differs in the last digit); constants precise enough; Erwartungshorizont states the tolerance | result changes in a counted digit through wrong rounding; more digits demanded than the data allow in a graded task |
| P6 | Plausibility | every value within the known sizes (`konventionen.md`); invented measured data fit the law with realistic scatter and are labelled; contexts are physically possible (a cyclist at 25 m/s is not) | a value off by a power of ten or impossible in the context |
| P7 | Concepts and models | terms used correctly (Kraft/Energie/Leistung, Spannung/Stromstärke, Masse/Gewichtskraft, Wärme/Temperatur, Geschwindigkeit/Beschleunigung); model named, not confused with reality; no wording that plants a known wrong idea ("Strom wird verbraucht", "Kraft des Körpers", "Fliehkraft zieht nach außen" without frame of reference) | a statement that is physically wrong or teaches a known misconception as fact |
| P8 | Figures and diagrams | axes with quantity and unit, zero, even scale; plotted points match the table; slope read from the graph gives the stated value; circuit symbols standard and circuit closed/meters connected right (A in series, V in parallel); rays with arrows, angles from the normal; force arrows to scale; figure agrees with the text | a figure that contradicts the data or shows wrong physics; a task that depends on a figure which cannot be read in print |
| P9 | Experiments | type stated (SE/DE); safety block with hazard, measure, who, stop; within the limits of `experimente.md` (student voltage, laser class, radioactive sources, mercury); material realistic for a school; protocol parts complete; measured quantity, changed quantity, constants named; time fits the phase | a student experiment above the limits; an experiment without safety block; a procedure that cannot yield the stated data |
| P10 | Animation physics | positions and values in each step follow the law and the worksheet numbers; equal time steps look equal; scales stated; vectors proportional; model marked as model; last step = solution; captions say which instant is shown; needed at all (motion or change) | a step that shows false physics; values that differ from worksheet or solution |
| P11 | Operators, AFB, marking | operator from the science list, du-form in Sek I, Sie-form in the Oberstufe; AFB fits (routine calculation = I even with "Bestimmen"); Oberstufe Klausur has all three AFB and material; points split so that Ansatz, Rechnung, Ergebnis with unit can be awarded; Folgefehler and tolerance stated; grade key recomputed from the percentages. Script coverage: `check_material.py` compares printed points, the AFB table's points and the key's printed points with the `data-*` values, and sums the parts. It does not check the `data-*` values themselves, the AFB shares in %, or key thresholds against percentage × total: recompute these by hand | AFB III missing in a Klausur; points that cannot be awarded from the description; key thresholds wrong |
| P12 | Bilingual, physics side | English term from `begriffe.md` (momentum, voltage, power ...); same numbers, units and digits in both lines; decimal comma in German, point in English; formula symbols identical; operator pair from base `operatoren.md` | wrong subject term or different number in the English line |

## Table for the independent solutions (goes into the report as "Nachgerechnet")
```markdown
| Task | Given | Own result (way 1) | Check (way 2 or estimate) | Material says | Match |
|---|---|---|---|---|---|
| 1 | s = 120 m, t = 15 s | v = 8,0 m/s | 8 m/s · 15 s = 120 m | 8,0 m/s | yes |
```
- Keep full calculator precision until the end; round once.
- "Match" = value, unit, digits and sign. A difference in the last digit: find the cause (intermediate rounding, constant, calculator mode) before writing the finding.
- Explanations and judgements: list the expected key points first, then compare; a missing key point in the Erwartungshorizont is a finding.
- Drawing tasks: recompute the coordinates of at least three points of the model drawing.

## Frequent defects (look for these first)
- ×3,6 / ÷3,6 swapped; cm not converted to m in ½·D·s²; g instead of kg.
- Calculator in degrees for sin(ω·t); ω·t given a unit.
- `g = 10` in one file and `9,81` in another.
- Result of part b) built on the rounded result of part a).
- t-s diagram that does not start where the text says; graph through points that the table does not contain.
- Lamp circuits: voltmeter drawn in series; current "used up" in the wording.
- Solution uses a formula that the info box of the worksheet does not contain.
- Points: sub-points add to more than the task's points; AFB table not updated after a change.
- Grade key: threshold rounded down in the student's favour against the base rule; Oberstufe key with 6 rows.
- English line: "impulse" for Impuls, "tension" for Spannung, "performance" for Leistung, decimal comma kept.
- Animation: bodies move equal distances although speeds differ; last caption states a value without unit; caption box empty in every step (script error: apostrophe in a caption string); a label covered by a moving body or cut off at the edge of the stage (screenshot every step; no script sees it); → and ← dead after a click on a button.
- English calques: "it holds" (es gilt → the following holds), "stop the time" (Zeit stoppen → time the walk, take the time), "form the mean" (bilden → work out), "Determine with ... the ..." (object moved behind the adverbial as in German), plural verb after a quantity ("6.0 m/s are").
- Print: a box that cannot break pushed to the next page; a task split over two pages.

## Verdict
Base rule. Physics addition: one Must in P2, P3 or P9 that changes a task or makes an experiment unsafe → at best "Einsatzbereit nach Must-Korrekturen"; a wrong grade key or more than three Must → "Überarbeiten".
