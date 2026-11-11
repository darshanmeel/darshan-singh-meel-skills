# Maths animations

Format, controls, captions, reduced motion and print: base `formate.md` (animation.html) and the base template. This file says what to animate in maths and how to build it with the base engine (`STEPS` list; numbers inside SVG attribute values are tweened; steps are cumulative).

## Animate or draw?
| Animate (a change, a construction or a sequence is the idea) | Draw a figure in `erklaerung.html` instead |
|---|---|
| a whole is divided, parts are refined and put together (fractions: teilen, erweitern, addieren) | one fraction shown as part of a whole |
| a written algorithm runs column by column with the carry | the finished calculation |
| jumps on the number line (addition, subtraction, negative numbers) | a number line with marked numbers |
| a construction in its order (Mittelsenkrechte, Winkelhalbierende, Spiegelung, Drehung, Thaleskreis, Dreieck from SSS/SWS/WSW) | the finished figure when the steps are already known |
| a figure is cut and rearranged (Parallelogramm → Rechteck, Trapez, Kreis → "Rechteck", Pythagoras by rearrangement) | a formula with a labelled figure |
| a net folds to a solid, shown as key frames | the net alone |
| a parameter changes a graph (`a`, `b`, `c` of a parabola; `a · sin(b(x − c)) + d`; a family of functions) | one graph with its special points |
| a secant turns into the tangent; h → 0 | the tangent alone |
| rectangles under a graph get narrower (Ober- und Untersumme, n = 2, 4, 8, 16) | one integral as shaded area |
| a point runs on the unit circle while the sine curve is drawn | the finished sine curve |
| a point moves along a line `p⃗ + t · u⃗`; two moving objects meet or miss | a line in a coordinate system |
| a tree diagram grows stage by stage; a histogram changes with n or p; the rejection region moves with α | one tree, one histogram |

No animation for: a rule text, a list of formulas, a table of values, decoration.

## Maths rules for every animation
- **Exact geometry.** Every coordinate is computed from the numbers of the task (script or formula), with one stated scale. Equal parts are equal to the pixel; a half is exactly half.
- **Same numbers** as worksheet, solution and explanation. The last step shows the result of the solution, written as the solution writes it.
- **One idea per step**, 4-8 steps; the caption states what changes and why, in at most two short sentences, German + English (`bilingual.md`).
- **Start = the question** (the task with `?`), end = the answer. A wrong idea may be shown only when the same step refutes it visibly.
- **Not by colour alone**: the two addends, graphs or objects differ by outline style (solid, dashed), pattern or label.
- **Limits are not reached by the engine**: for h → 0 or n → ∞ show three or four stages and say in the caption that the process continues.
- **Text does not tween.** A changing value is a set of `<text>` elements, one per state, switched by `opacity`. Fractions in the picture: numerator, bar (`<line>`), denominator as three elements in a `<g>`.
- **Paths tween only with the same command structure.** A graph that changes shape needs a `d` with the same commands and the same number of points in every step (compute all states with one function).
- Text in the stage at least 16 units high; with the two-per-row print layout prefer 22 or more for labels that students must read.

## Recipes for the base engine
| Effect | SVG | Step `set` |
|---|---|---|
| Part appears (division lines, label, result) | element or `<g>` with `opacity="0"` | `'#teil': { opacity: 1 }` |
| Piece moves (fraction part, tile, carry digit) | `<rect id="p" x="40" y="40" ...>` copy on top of its source, `opacity="0"` | `'#p': { x: 500, y: 100, opacity: 1 }` |
| Line is drawn (construction line, arc, graph) | `<path id="k" d="..." pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">` | `'#k': { 'stroke-dashoffset': 0 }` |
| Compass arc | `<path d="M x1 y1 A r r 0 0 1 x2 y2" pathLength="1" ...>` with computed end points | as above |
| Figure turns or flips | `<g id="f" transform="rotate(0 200 150)">`; reflection as `scale(1 1)` → `scale(-1 1)` around a translated axis | `'#f': { transform: 'rotate(90 200 150)' }` - same shape of the value |
| Jump on the number line | arc path per jump, drawn with the dash recipe; marker `<circle id="m" cx>` | `'#m': { cx: 380 }` |
| Graph changes with a parameter | `<path id="g" d="M ... L ... L ...">` with N computed points | new `d` with N points for the new parameter value |
| Secant → tangent | `<line id="s" x1 y1 x2 y2>` through P and Q; `<circle id="q">` | new `x2`, `y2` (and `cx`, `cy` of Q) per stage |
| Rectangles under a graph | one `<g id="n4">`, `<g id="n8">` ... per stage with computed `<rect>`s, `opacity="0"` | previous group `opacity: 0`, next `opacity: 1` |
| Point on the unit circle + sine curve | `<circle id="pt">`, radius `<line>`, curve path with the dash recipe split into quarters | `cx`, `cy`, line end, `stroke-dashoffset` 1 → 0,75 → 0,5 ... |
| Bar chart / histogram changes | `<rect id="b3" y height>` per bar | `y` and `height` together so that bars grow upwards |
| Tree diagram grows | branches as paths with the dash recipe; probabilities as hidden `<text>` | branch offsets to 0, then labels `opacity: 1` |
| Written algorithm | digits of the result and carries as `<text opacity="0">` in a grid | one column per step: carry and digit appear |

## Check before hand-over
- Recompute three coordinates of the stage by hand from the scale.
- Step forwards and backwards through all steps; play at each speed; toggle English; print preview (the engine prints one still per step).
- Count: parts, bars, points and labels in the last step equal the solution.
- `python <base skill dir>/scripts/check_material.py <folder>` passes for `animation.html`.

Worked example: `examples/brueche-addieren/animation.html` (½ + ⅓ with two rectangles refined to sixths; six steps).
