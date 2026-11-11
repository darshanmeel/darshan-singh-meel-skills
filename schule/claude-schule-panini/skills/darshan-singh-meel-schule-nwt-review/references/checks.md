# NWT checks (added to the base rubric)

Base areas 1-12 stay in force (`darshan-singh-meel-schule/references/review.md`). N1-N10 sharpen them for Naturwissenschaft und Technik. Files named below: `hessen-nwt.md`, `module.md`, `technik.md`, `begriffe.md` belong to `darshan-singh-meel-schule-nwt`; `konventionen.md`, `experimente.md`, `animationen.md`, `sek1.md` to `darshan-singh-meel-schule-physik`.

## Checks
| # | Area | Check | Must when |
|---|---|---|---|
| N1 | Curriculum anchor | Quelle names the Wahlunterricht (schulinternes Curriculum) and one carrying subject KC; Kompetenzbereich, standard and Inhaltsfeld exist as printed (`sek1.md`, `module.md`); level is Mittelstufe; the anchor content is taught or stated as Lernvoraussetzung | an "NWT-Kerncurriculum Hessen" or any invented reference is cited; Oberstufe content or course labels (GK/LK, Q-Phase) appear; anchor does not fit the tasks |
| N2 | Every result | own result = material's result: value, unit, digits; tables and figures of merit recomputed; ratios the right way round (driving/driven) | a wrong value, unit or ratio; inverted transmission ratio; a solution that does not answer the question |
| N3 | Science inside | physical, chemical and biological statements correct at the level of the carrying KC; efficiency never above 100 %; "Goldene Regel" respected; no confusion of Kraft, Energie, Leistung; models marked | a false statement of science; a machine that yields more work than is put in |
| N4 | Units, digits, plausibility | as P4-P6 of the physics review: units in every line, conversions right, digits of the weakest input, values match real parts (tooth counts 11-52, hobby motors 1,5-12 V, paper bridge loads in the kg range, mm for workshop dimensions) | wrong conversion; result without unit; value impossible for the named part |
| N5 | Requirements and task design | 3-5 requirements, each measurable with value and unit, Muss/Wunsch marked, a test per requirement, one figure of merit; open tasks have more than one valid solution and criteria to compare them; the step of the cycle is stated | a construction task without measurable requirements in assessed work; a "design" task with exactly one hidden answer and no criteria |
| N6 | Buildable and testable | parts list complete (count, size, material); steps in an order that works; dimensions and scale present; time per step realistic for the group size; the test can be done with the school's equipment; data table prepared | a part or tool used that is not listed; an order of steps that cannot be built; the stated test cannot produce the stated data |
| N7 | Technical representation | sketches and drawings with dimensions in mm and scale; block diagrams with one function per box and labelled flows; control loops closed; circuit diagrams with standard symbols, meters connected right; flow charts consistent with the described behaviour; figure agrees with text and solution | a diagram that contradicts the text or shows a system that cannot work; a task depending on a figure unreadable in print |
| N8 | Safety | every practical task has hazard · measure · who · stop; tools and machines within `technik.md` (machines students never operate; soldering lead-free; student voltage limits; laser classes); per-device permission not asserted where the reference says `check:`; supervision of parallel stations named; home tasks without tools, mains or chemicals | a practical task without safety block; a forbidden machine or voltage for students; a home task with a hazard |
| N9 | Assessment | frame matches the course: Vermerke by default, Noten only with a stated school decision; criteria grid covers product, process, documentation with observable criteria; weights add to 100 %; key printed as proposal; Lernkontrolle: points, AFB table and thresholds recomputed; no Klassenarbeit label. Script coverage: `check_material.py` compares printed points, the AFB table's points and the key's printed points with the `data-*` values, and sums the parts. It does not check the `data-*` values themselves, the AFB shares in %, or key thresholds against percentage × total: recompute these by hand | a Noten key 1-6 or Oberstufe points for an ungraded Wahlunterricht without the school decision; sums or thresholds wrong; criteria that cannot be observed |
| N10 | Animation of systems | ratio of turns exact in every step; sense of rotation right (chain/belt: same; meshing gears: opposite); cause before effect in control chains; energy bars add up; values equal worksheet and solution; scale and instant stated; needed (motion or signal flow) | a step that shows a wrong ratio, direction or order; values that differ from the worksheet |

Bilingual, operators, time, differentiation, accessibility, privacy, copyright, files: base areas 3, 4, 6-9, 11, 12. Subject terms: `begriffe.md` of the NWT skill (`Übersetzung` = transmission ratio, `Entfaltung` = development, `Technik` = technology, `regeln` ≠ `steuern`).

## Table for the independent solutions ("Nachgerechnet" in the report)
```markdown
| Task | Given | Own result (way 1) | Check (way 2 or estimate) | Material says | Match |
|---|---|---|---|---|---|
| 2 | z₁ = 44, z₂ = 22, U = 2,10 m | 4,20 m | 2 Umdrehungen · 2,10 m | 4,20 m | yes |
```
Open design tasks: list all valid solutions you find and the best by the stated criterion; the model solution must be among them and must name the criterion.

## Frequent defects
- Transmission ratio upside down (z₂/z₁ used as turns per crank turn); "größeres Ritzel = schneller".
- Wheel circumference confused with diameter; km/h from m/min without ×60 ÷ 1000.
- "Stabil", "schnell", "gut" as requirements without a number.
- Parts list lacks glue, wire, battery clip, or the tool to cut.
- Solar or motor tasks with efficiency above 100 % after rounding; power computed from open-circuit voltage and short-circuit current.
- Control loop drawn as a chain (no feedback arrow); sensor and actuator swapped in the text.
- Safety line generic ("vorsichtig arbeiten"); hot-glue or soldering without stand and cooling time; cutting knife in Jg. 5/6 without supervision note.
- Grade key 1-6 printed in a Wahlunterricht check; Vermerk thresholds without "Vorschlag".
- English: "technique" for Technik, "translation" for Übersetzung, "construction" for the design activity, "regulate" for both steuern and regeln.
- Animation: both wheels turn by the same angle; meshing gears turning the same way; caption box empty (apostrophe in a caption string); label covered by crank, spoke or mark in some step (screenshot every step; no script sees it); → and ← dead after a click on a button; axis label cut off at the edge.
- English calques: "it holds", "Count on the bicycle the teeth", "Calculate for z1 = 44 ... the number" (German word order).
- Table to fill in with columns too narrow to write a number in.

## Verdict
Base rule unchanged. N2, N3 and N9 belong to base areas 2 and 5; N1 to area 1. A Must in N8 (unsafe task) → "Überarbeiten" until the task is changed.
