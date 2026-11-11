# Maths conventions: notation, numbers, solutions, checks

Formats, templates and the DE/EN markup: base `formate.md`, `bilingual.md`. This file adds what maths needs.

## Notation (German school notation in the German line and in every formula)
| Item | German line and formula-only lines | English sentence |
|---|---|---|
| Decimal sign | `3,75` | `3.75` |
| Thousands | `12 500` or `12.500` only in Grundschule Zahlenraum work as the class writes it; never `12,500` | `12,500` |
| Multiplication, division | `3 · 4`, `12 : 4`; fraction bar for quotients of terms; `×` only for dimensions (`2×2`) | same symbols |
| Minus | `−` (U+2212), not the hyphen | same |
| Point, coordinates | `P(2|3)`, `A(1|−2|4)` | same; glossary notes `(2, 3)` as the English form |
| Intervals | `[a; b]`, `]a; b[` | same |
| Sets | `ℕ, ℤ, ℚ, ℝ`, `L = {2; 5}` | same |
| Function | `f(x) = 2x + 1`, graph `G_f`, derivative `f′(x)` | same |
| Vectors | column vectors with arrow; `|v⃗|` for the length; line `g: x⃗ = p⃗ + t · u⃗` | same |
| Angles | `α = 35°`; radians without unit | same |
| Percent, units | `25 %`, `3,5 cm`, `12 m²` with a no-break space | `25%` is allowed in English prose; units unchanged |
| Probability | `P(A)`, `P(A∣B)` or `P_B(A)` as the class writes it, `P(X ≤ k)` | same |
| Mixed numbers | only for final results in Sek I: `1 7/12`; never inside a product | "1 7/12" |
| Rounding sign | `≈` whenever a value was rounded | same |

- A line that is only a formula stands once, in German notation, without an English copy.
- A sentence gets its English line with the English decimal sign, also inside a formula in that sentence: `Der Flächeninhalt beträgt 4,5 cm².` / `The area is 4.5 cm².` · `... mit r(t) = −0,3t² + 2,4t beschrieben.` / `... described by r(t) = −0.3t² + 2.4t.` Nothing else in the formula changes (`·`, `:`, `P(2|3)`, `[a; b]`, `−` stay).
- Variables italic (`<var>x</var>`), numbers, units, operators and function names (sin, ln, lim) upright.

## Formulas in HTML (self-contained, printable)
- Fractions, roots, integrals with limits, sums, column vectors, matrices: inline MathML (`<math>` with `<mfrac>`, `<msqrt>`, `<msubsup>`, `<munderover>`, `<mtable>`). Current browsers render and print it without any script.
- Simple terms: text with `<sup>`, `<sub>`, `<var>`; wrap short formulas in `white-space:nowrap` so that no line breaks between sign and number or number and unit.
- Never a picture of a formula, never LaTeX source in the page, never a script library.
- Written algorithms (schriftliches Rechnen, Stellenwerttafel, Gauß scheme): a `<table>` with one digit per cell, carries in their own row.

## Choosing numbers
| Goal of the task | Numbers |
|---|---|
| Learn a method by hand | small, clean; results that end (fractions with small kgV, integer zeros, Pythagorean triples 3-4-5, 5-12-13, 8-15-17, discriminants that are squares) |
| Recognise a typical mistake | values where the mistake gives a visibly different, plausible-looking result |
| Model reality | realistic sizes with units (check against everyday knowledge); rounding instruction in the task |
| Calculator or CAS use | values that cannot be done by hand in the time; operator `bestimmen` |
| Test | no result that can be guessed from the task before it; parts independent where possible, or the later part states a fallback value (`Rechnen Sie mit b = 6 weiter, falls ...`) |

- Build tasks backwards: fix the result first, then derive the data, then solve forwards to confirm.
- No two tasks of one worksheet with the same result; no result equal to a number printed in the task.
- Reversed tasks ("find all ...") need the solution set proved complete in the solution.

## Solution layout (loesung.html, Erwartungshorizont)
| Task type | Solution contains |
|---|---|
| Calculation | result first; every step a student writes; for written algorithms the full scheme |
| Equation | each transformation with its operation (`| − 3x`), solution set, Probe by substitution |
| Sachaufgabe / modelling | Gegeben - Gesucht - Ansatz - Rechnung with units - Antwortsatz - plausibility remark |
| Construction / drawing | finished figure as SVG drawn to scale, plus the construction steps in order |
| Reasoning / proof | the chain of arguments in numbered steps; which property or theorem each step uses |
| Function analysis | conditions named (`notwendig`, `hinreichend`), points with both coordinates, sketch with the points found |
| Stochastics | model named (Laplace, Bernoulli with n and p), event in words and symbols, value rounded to 4 decimals or as percent with one decimal |

- Every solution task ends with one "Typischer Fehler" (from the level reference or the lesson).
- Rounding: carry full precision, round once at the end, write `≈`; German line with comma. State the rule in the task when a rounded value is expected.
- Erwartungshorizont: points per step (Ansatz, Rechnung, Ergebnis with unit, Antwort/Deutung), Folgefehler rule, accepted tolerance for rounded values, other correct ways.
- Sub-points: one pattern in every row, `Schritt: n P` / `step: n points` (Oberstufe `BE` / `marks`), steps separated by `;` - `Ansatz mit den Grenzen 0 und 4: 1 BE; Stammfunktion: 2 BE`. The same split stands on the row as `data-teilpunkte="1+2"`; it adds up to `data-punkte`.
- Grade key: Oberstufe thresholds exact (percentage × total, not rounded; base `bewertung.md`). Sek I and Grundschule: exact, or rounded **up** to the next half point (9,6 → 10; 13,2 → 13,5), never down; print which under the key (`Schwellen auf halbe Punkte aufgerundet`). The school's own key wins.

## Checking every answer: `data-check`
Every solution element that carries `data-aufgabe` (section in `loesung.html`, row in `erwartungshorizont.html`) gets `data-check="expr; expr; ..."`. In `erklaerung.html` the Beispiel section and every "Probier es selbst" item carry `data-aufgabe` (`B`, `P1`, `P2`, ...) and `data-check`. `scripts/check_rechnung.py <folder>` (searches subfolders) evaluates each expression; all must be true.

| Kind of answer | Check to write |
|---|---|
| Arithmetic, fractions | `3/4 + 5/6 == 19/12` (integer division is exact) |
| Each printed intermediate step | one expression per step: `9/12 + 10/12 == 19/12` |
| Rounded value | `runde(32/3, 2) == 10.67` |
| Equation solution | substitute: `wert('2*x+3', 4) == 11`; zeros: `wert('-x**2+4*x', 4) == 0` |
| Derivative, antiderivative | `nah(ableitung('x**3-2*x**2+5*x', 1.7), wert('3*x**2-4*x+5', 1.7), 1e-4)` at two points |
| Definite integral, area | `nah(integral('-x**2+4*x', 0, 4), 32/3)` |
| Extremum, zero found numerically | `nah(nullstelle('x**3-2*x-5', 2, 3), 2.0946, 1e-4)` |
| Binomial, normal | `runde(binomsum(45, 0.1, 8) - binomsum(45, 0.1, 2), 3) == 0.809` · `runde(normal(55, 50, 2) - normal(48, 50, 2), 4) == 0.8351` |
| Vectors | `skalar([1,2,2],[2,-2,1]) == 0` · `betrag([1,2,2]) == 3` · `kreuz([1,0,0],[0,1,0]) == [0,0,1]` |
| Typical mistake value | the wrong result too: `438+247-10 == 675` |
| No numeric answer (text, drawing) | `data-check="-"` and a criteria list in the solution |

- **Final answer against the given data:** at least one expression per task puts the printed final answer back into the data of the task text - both given points into the line equation found (`wert('1.5*x+2.5', -1) == 1; wert('1.5*x+2.5', 3) == 7`), the solution into the original equation, the result into the context condition. A check of one part (the slope alone) lets a wrong answer pass.
- The expression is an independent second calculation: write what the task asks, not the steps of the printed solution copied one to one. Where both are useful, add both.
- Decimal point inside expressions; `<` as `&lt;`. A general statement ("for every a") is checked at two or three sample values.
- The script lists a solution task without `data-check` with `?`; it exits with code 1 on any false or broken check.
- The script also checks points in files with `data-gesamt`: `data-teilpunkte` adds up to `data-punkte` (`?` when a row of 2 or more points has none); printed AFB shares; grade-key `data-ab` against the printed percentage × total; test and Erwartungshorizont agree in ids, points and AFB.
- Limit: a green run means the files agree with themselves. A wrong answer with a matching wrong check, an off-level task or a bad sub-point text passes - process step 5 and the review find those.

## Second way for the self-check (process step 5)
| Task | Second way |
|---|---|
| Addition, multiplication | inverse operation; Überschlag |
| Equation | substitute the solution; graph |
| Fractions, percent | decimal value; picture |
| Geometry | measure in the scale drawing; decomposition; coordinates |
| Function analysis | value table and sketch; sign change of `f′` |
| Integral | estimate by a rectangle or triangle; symmetry |
| Vectors | Punktprobe; distance check with a second point |
| Probability | complementary event; sum of all paths = 1; small simulation in the plan notes |

## Figures
- Inline SVG, coordinates computed (Python or by formula), never placed by eye. State the scale (`1 Kästchen ≙ 1 cm`, `1 LE ≙ 20 px`); a sketch that is not to scale is labelled `Skizze, nicht maßstäblich` / `sketch, not to scale`.
- Coordinate systems: both axes labelled with variable (and unit), arrow heads, tick labels, origin; equal unit length on both axes unless stated. SVG y grows downwards: `y_px = y0 − k · y`.
- Function graphs: path through computed points (step ≤ 0,25 units) or exact Bézier for parabolas; mark the special points the solution names.
- Geometry: points with capital letters, sides lower case, right angles with the square-and-dot sign, equal lengths with tick marks; grey construction lines stay visible in the solution.
- Two graphs or two figures differ by line style or label, not by colour alone (base accessibility rule).
- A task that asks students to measure prints at 100 % only: note `Drucken ohne Skalierung` / `print without scaling` under the figure.

## Print notes for maths pages
- A calculation needs room: `.karo` height = 5 mm × (lines of the model solution + 2). Grundschule: 14 pt pages hold little - plan one info box plus one task per page.
- Long Erwartungshorizont tables: put `style="display:table-row-group"` on `<tfoot>`, otherwise browsers repeat the sum row at the bottom of every printed page.
- Keep a grade key in one piece: `style="break-inside:avoid"` on its section.
