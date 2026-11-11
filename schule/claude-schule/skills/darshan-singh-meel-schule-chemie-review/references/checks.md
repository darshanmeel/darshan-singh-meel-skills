# Chemistry checks (added to the base rubric)

Base areas 1-12 stay in force (`darshan-singh-meel-schule/references/review.md`). C1-C12 sharpen areas 1, 2, 3, 5, 7 and 10 for Chemie. References named below belong to `darshan-singh-meel-schule-chemie`.

## Checks
| # | Area | Check | Must when |
|---|---|---|---|
| C1 | Curriculum level | Sek I: Kompetenzbereich + Teilbereich + Kompetenzerwartung (Ende Jg. 9/10) + Inhaltsfeld with full name as in `sek1.md`. Oberstufe: standard code + Kurshalbjahr.Themenfeld + GK/LK as in `oberstufe.md`, wording as printed. Content belongs to the stated level (table "Level traps") | reference missing or invented; LK-only content in GK material (weak-acid pH, Nernst, extended MWG, S<sub>N</sub>1/S<sub>N</sub>2, entropy, orbital model); Oberstufe content in Sek I material that the plan does not teach |
| C2 | Equations | every equation balanced in elements and charges; electrons equal in both half equations; formulas right (ion charges, indices); states given from Jg. 9; right arrow (→, ⇌); smallest whole coefficients; names match formulas (Kupfer(II) = Cu<sup>2+</sup>) | any unbalanced equation or wrong formula in Lösung, Erwartungshorizont, Erklärung, Tafelbild or animation |
| C3 | Calculations | own result = material's result: value, unit, digits; mole ratio from the equation; mL → L; molar masses and constants are the ones printed on the sheet; no rounding chain; answer sentence answers the question | wrong value or unit; a needed value (molar mass, potential, pK<sub>S</sub>, molar volume) neither printed nor in the named aid |
| C4 | Solvable and unambiguous | all data given; one reading; conditions named (temperature for pH + pOH = 14, standard conditions for <i>E</i>°); data realistic (burette volumes, concentrations, masses) | missing datum; two valid readings with different results; pH task below about 10<sup>−6</sup> mol/L treated without autoprotolysis |
| C5 | Stoff, Teilchen, Symbol | observations on the Stoffebene only; interpretation on the Teilchenebene; no "Atome sind rotbraun", "Moleküle sieden", "NaCl-Molekül"; ionic compounds as ions in solution; spectator ions handled consistently | an interpretation inside the expected observation, or a particle statement that is chemically wrong |
| C6 | Concepts | oxidation/reduction, Oxidationsmittel/Reduktionsmittel, donor/acceptor, anode/cathode and poles, strong/concentrated, equilibrium ("constant, not equal"; catalyst), exothermic/activation energy used correctly; the redox or acid definition is the one of the level (Sauerstoff → Elektronen; Arrhenius → Brönsted) | a statement that is wrong or teaches a known misconception as fact (`fachpraxis.md`, typical errors) |
| C7 | Expected observations | each stated observation follows from the chemistry (own prediction from the redox series, solubility, indicator colours) and matches `fachpraxis.md`; "keine Veränderung" stated where nothing reacts; the student sheet does not give the observation away | an observation that would not occur, or a missing one that a task needs |
| C8 | Safety block | present on every experiment sheet with the student lines of `sicherheit.md`, all lines in lesson plan or Lösung; Versuchsart fits Tabelle 3b for the Jahrgang; concentration and amount named; each classification has a source or is marked `prüfen`; products (gases) considered; substitution line filled; disposal per residue; draft sentence printed; no pregnancy question, no student named | experiment without safety block; a student activity that Tabelle 3b forbids for the Jahrgang; a GHS classification stated as fact without source; draft sentence missing; open flame next to a flammable liquid in the procedure |
| C9 | Procedure | steps numbered, amounts and vessels given, one variable changed where a comparison is meant, control present, time fits the phase, material exists in a school collection | a procedure that cannot yield the stated observation or data |
| C10 | Animation chemistry | per step: atoms conserved, charges balanced, electrons shown = electrons in the equation; particles labelled with symbol and charge, not by colour alone; model named, one limit named (from Jg. 9); last step = equation of the worksheet; needed at all (process, not a still structure) | a step that shows wrong chemistry or counts; values or formulas that differ from worksheet or solution |
| C11 | Operators, AFB, marking | operator from the science list (du in Sek I, Sie in the Oberstufe); AFB fits (routine balancing or routine calculation = I-II, prediction for an unknown system = II-III); Klausur has all three AFB and material; points split so that equation, Ansatz, calculation, result with unit can be awarded; Folgefehler stated; grade key recomputed | AFB III missing in a Klausur; points that cannot be awarded from the description; key thresholds wrong |
| C12 | Notation and bilingual, chemistry side | real sub- and superscripts, charge as `2+`, minus sign, Roman numerals in names, italics for quantity symbols; KCGO names (Oxonium-Ion, Alkanol); English term from `begriffe.md` (reducing agent, amount of substance, precipitate, fume cupboard); same formulas and numbers in both lines; decimal comma in German, point in English | `H2O`/`Cu2+` in a formula a task depends on; wrong subject term or different number/formula in the English line |

## Table for the independent solutions (goes into the report as "Nachgerechnet")
```markdown
| Task | Own equation / result | Balance (elements · charges · e⁻) or second way | Material says | Match |
|---|---|---|---|---|
| 2 | Zn + Cu²⁺ → Zn²⁺ + Cu | Zn 1/1, Cu 1/1 · 2+/2+ · 2 e⁻ given, 2 taken | same | yes |
| 4 | c(HCl) = 0,125 mol/L | n = 0,1 mol/L · 0,0125 L = 1,25 mmol; ÷ 0,0100 L | 0,125 mol/L | yes |
```
- Keep full precision until the end; round once. A difference in the last digit: find the cause (molar mass table, intermediate rounding) before writing the finding.
- Observations and explanations: list the expected key points first, then compare; a missing key point in the Erwartungshorizont is a finding.
- Predictions: derive them from the data given on the sheet only (not from the full electrochemical series, unless the sheet prints it).

## Frequent defects (look for these first)
- Charges not balanced in an ionic equation (Cu + Ag<sup>+</sup> → Cu<sup>2+</sup> + Ag); electrons left in the overall equation.
- Sulfate written as SO<sub>4</sub><sup>−</sup>; Eisen(II) and Eisen(III) mixed up; Fe<sup>3+</sup> formed where Fe<sup>2+</sup> is meant.
- "Zink löst sich auf" as Beobachtung and as Deutung; colour of a solution ascribed to atoms.
- Redox series ordered by what is deposited instead of what goes into solution; "edel" and "starkes Reduktionsmittel" swapped.
- mL used as L in <i>c</i> = <i>n</i>/<i>V</i>; molar mass in the solution differs from the one on the sheet.
- Zellspannung with the wrong sign order; Anode called Pluspol in a galvanic cell.
- Safety block names the pure substance although a dilute solution is used; pictograms from memory; disposal "in den Ausguss" for heavy-metal solutions.
- Student experiment with Brom or Bromwasser, concentrated acids, or hydrogen from a cylinder in Jg. 5-9.
- The worksheet's info box already tells the result of the experiment.
- Points: sub-points add to more than the task's points; AFB table not updated after a change.
- English line: "educt", "lye", "connection" for Verbindung, "reduction means" for Reduktionsmittel, "solve" for lösen (dissolve), decimal comma kept.
- Animation: an ion disappears without an atom appearing; two electrons drawn, one counted in the caption.

## Verdict
Base rule. Chemistry addition: one Must in C2, C3 or C7 that changes a task, or any Must in C8 → at best "Einsatzbereit nach Must-Korrekturen", and the experiment is not used before the fix; a wrong grade key or more than three Must → "Überarbeiten". Every report ends "Sicherheit: offen" with the reminder that the Gefährdungsbeurteilung stays with the teacher.
