# Strategies

Names are used word for word in solutions (`Strategie: … / Strategy: …`), explanations and lesson goals. The KC Hessen names systematisches Probieren, Hilfslinien, Hilfsgrößen, Vorwärts- und Rückwärtsarbeiten (`klassen-09-10.md`); the rest is standard heuristics.

## Solving strategies
| Strategie \| Strategy | From | Use when | Core move | Typical slip |
|---|---|---|---|---|
| Schrittweise rechnen \| calculating step by step | 3/4 | 3-point problems that need no special strategy | one operation per step, each intermediate result written down | a step left out; all numbers of the text added |
| Rückwärtsarbeiten \| working backwards | 3/4 | the end is known, the start is asked | undo each step with the inverse operation, last step first | inverse steps in the original order |
| Systematisch probieren \| systematic trial | 3/4 | few candidates, conditions easy to test | try in order, note each result, use it to choose the next try | random tries, a candidate skipped |
| Systematisch aufschreiben und zählen \| listing and counting systematically | 3/4 | "wie viele" with a small number of cases | fix an order (by first digit, by size), list, count | first or last case missing, a case twice |
| Skizze oder Tabelle \| sketch or table | 3/4 | several persons, properties, time steps | one row per person, one column per property; cross out | reading the clue in the wrong direction |
| Annehmen und ausgleichen \| assuming and adjusting | 3/4 | two kinds, two totals (heads and legs) | assume all are of one kind, compare, exchange one by one | difference not divided by the difference per exchange |
| Antworten einsetzen \| testing the options | 3/4 | the options are candidates for the unknown | start with the middle option when they are ordered | stopping at the first option that fits one condition only |
| Ausschließen \| elimination | 3/4 | options can be tested faster than the answer can be found | rule out by parity, last digit, size, units | ruling out without a reason |
| Abschätzen und überschlagen \| estimating | 5/6 | options far apart, exact value costly | round so that the direction of the error is known | rounding both factors the same way and trusting the last digit |
| Symmetrie nutzen \| using symmetry | 3/4 | figure or situation has equal parts | solve one part, multiply; pair opposite terms (first + last) | counting the axis part twice |
| Zerlegen und ergänzen \| decomposing and completing | 5/6 | area or perimeter of a composite figure | cut into known parts, or complete to a rectangle and subtract | inner edges counted in the perimeter |
| Hilfslinie einzeichnen \| drawing an auxiliary line | 7/8 | angles or lengths not directly linked | parallel through a vertex, radius to a tangent point, diagonal | assuming a property the line does not have |
| Fallunterscheidung \| case distinction | 5/6 | truth and lie, "genau eines", sign of a number | assume each case in turn, follow it to a contradiction | not testing all cases after the first that works |
| Extremfall betrachten \| looking at the extreme case | 5/6 | smallest, largest, at least, at most | push each quantity to its limit; then show the limit is reached | optimum claimed without showing it is possible |
| Kleinere Fälle, Muster suchen \| smaller cases, finding a pattern | 5/6 | large n, repeating process | solve n = 1, 2, 3, 4; find the rule; check it once more | pattern guessed from two cases |
| Reste und letzte Ziffer \| remainders and last digit | 5/6 | weekdays, cycles, divisibility, big products | reduce to the period; only the last digit matters | quotient used instead of remainder |
| Gerade und ungerade (Parität) \| parity | 7/8 | "ist es möglich", sums and moves | follow what stays even or odd | parity of the count confused with parity of the sum |
| Invariante suchen \| finding an invariant | 7/8 | repeated operation, game | find what a move never changes (sum, parity, colour) | invariant checked for one kind of move only |
| Schubfachprinzip \| pigeonhole principle | 7/8 | "mindestens … sicher" | worst case first: fill every box without success, add one | computing the best case |
| Doppeltes Abzählen \| counting in two ways | 9/10 | handshakes, edges, incidences | count the same pairs from both sides, divide | forgetting the division by 2 |
| Variable einführen \| introducing a variable | 7/8 | relations between unknowns | name one unknown, express the rest, one equation | two variables where one suffices |

Levels are the earliest paper in which a problem may need the strategy; older levels use all earlier ones.

## Test tactics (taught with every mock test)
| Tactic | Rule for students |
|---|---|
| Order | first all 3-point problems, then 4, then 5; inside a block skip what does not open within a minute |
| Time | average 3 min (Klassen 3-6) or 2,5 min (Klassen 7-13) per problem; the last 5 min are for the answer sheet and for marked problems |
| Two rounds | round 1: sure problems; round 2: marked ones, hardest last |
| Guessing | never blind (expected gain 0); after ruling out at least one option a guess gains on average (`wettbewerb.md`) |
| Options first | read the five options before calculating: they show the form and size of the answer |
| Reading | underline the question and the words genau, mindestens, höchstens, nicht |
| Answer sheet | enter each letter right away or in one pass at the end with a number check; one letter per problem |
| Check | 5-point problem solved in 30 seconds → read the stem again |
| Scratch paper | sketch, table, list; number the notes with the problem number |

## Strategy set (Übungsblatt with one strategy)
- Info box: name of the strategy, when it fits, the core move in 2-3 lines, one worked mini example.
- 6-9 problems, all solvable with the strategy, rising 3 → 5 points; the last problem needs the strategy plus a second idea.
- One problem where the strategy does **not** fit best is allowed from Klassen 7/8 on and is marked in the solution ("hier ist … schneller").
- Solution: the strategy steps are shown explicitly (each undo step, each case, each row of the list).

## Explanation and animation
- `erklaerung.html`: one strategy per page; figure = the strategy as a picture (arrow chain forward and back, table with crossed cells, number line).
- `animation.html` only where steps explain: working backwards (arrows reverse one by one), a net folding to a cube, counting squares by size (one size lights up per step), elimination (options are crossed out one by one with the reason in the caption). Final frame = the answer of the worksheet.

## Training lesson (45 min, guide)
| Phase | Minutes | Content |
|---|---|---|
| Einstieg | 5 | one 3-point problem on the board, solved silently, answers by show of letter cards |
| Erarbeitung 1 | 12 | the strategy on a 4-point problem: students try, two ways compared |
| Sicherung | 6 | name, when it fits, core move - as Merksatz |
| Erarbeitung 2 | 15 | worksheet, problems in rising order, partner check with the reason for each ruled-out option |
| Abschluss | 7 | one 5-point problem in plenum; which distractor was tempting and why |
