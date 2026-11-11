# Building a problem

Own working rules for this skill, derived from the competition's form (`wettbewerb.md`). The organiser publishes no syllabus and no difficulty definition on the pages read.

## Anatomy
| Part | Rule |
|---|---|
| Stem | 1-4 short sentences; one question, last sentence; every number needed, none unused (unless spotting the unused number is the point - at most one such problem per set) |
| Figure | only when the problem needs it; then it carries facts the text does not repeat in full, and the text says "Das Bild zeigt …" |
| Options | five, (A)-(E), same form (all numbers, all names, all pictures); numbers ascending; unit in every option; lengths of options similar |
| Key | exactly one option correct under every reasonable reading |
| Solution | letter + value, steps, strategy name, mistake behind each distractor |

- Question forms that fit: "Wie viele …?", "Welche Zahl …?", "Wie groß/lang ist …?", "Welche der folgenden … ist …?", "Was ist sicher richtig?", "Welches Ergebnis ist nicht möglich?".
- Negations (`nicht`, `kein`) and quantifiers that carry the problem (`genau`, `mindestens`, `höchstens`, `sicher`) are printed bold.
- Avoid: "alle obigen", "keine der genannten" as a hiding place (allowed as (E) at most once per set, and then sometimes correct across sets), trick wording, cultural knowledge, real brand or person names, the current year as a hidden hint to an old paper.
- Stories: everyday, neutral, short. Invented first names, mixed; one name per initial inside a problem.

## Difficulty
| Points | What the problem asks | Steps | Target time (student of the level) |
|---|---|---|---|
| 3 | one idea that is known from class; careful reading or one clever look | 1-2 | about 1-2 min |
| 4 | two ideas combined, or one strategy that must be chosen (work backwards, list systematically) | 2-4 | about 3 min |
| 5 | an insight not practised in class (invariant, extreme case, clever counting), or several conditions held at once | 3-6 | about 4-5 min |

- Difficulty comes from the idea, never from long arithmetic or large numbers.
- Inside one point class: easier first. A set ends with its hardest problem.
- The same story at three difficulties is a good training device (strategy sets): change the number of conditions, not the size of the numbers.
- Adult check (step 6 of the process): at most 1, 2, 3 min for 3, 4, 5 points.

## Fields (mix of a mixed set or mock test)
| Field | Share (guide) | Examples of families |
|---|---|---|
| Zahlen und Rechnen | about 1/3 | clever calculation, digits and place value, divisibility, number puzzles, sequences |
| Geometrie und Raum | about 1/3 | counting figures, perimeter and area by decomposition, symmetry, folding and cutting, cube buildings, nets, angles |
| Logik, Kombinatorik, Sachsituationen | about 1/3 | orders and rankings, true/false statements, counting possibilities, calendar and clock, weighing, ages, paths |

Each third of a mock test contains all three fields. The families per level are in the level files.

## Distractors
One mistake → one wrong option. Sources, in order of preference:

| Mistake family | Example (result 20: "double, subtract 7, divide by 3 gives 11") |
|---|---|
| stopped one step early | 40 (did not halve) |
| inverse step wrong | 13 (subtracted 7 instead of adding) |
| wrong order of steps | 27 |
| answered another quantity of the problem | the intermediate value, the other animal, the shorter side |
| off by one (fence posts, first and last counted or not) | counting days, posts, pages |
| counted double or forgot one case | 9 instead of 10; 15 with leading zeros |
| mixed up perimeter/area, digit/number, sum/product | 20 cm for 5 squares of area 4 cm² |
| took the unit or scale wrong | minutes for hours |

- The correct value is not the only one with a special property (only even number, only multiple of 5, the middle value every time).
- No option is absurd at first sight in 4- and 5-point problems; in 3-point problems one obvious outlier is acceptable.
- When fewer than four real mistakes exist, fill with neighbours of the correct value (± 1, ± step) and say "Nachbarwert" in the solution.
- Estimation problems: options far enough apart that a correct estimate decides.

## Key letters
- Decide the result first, then choose distractors so that ascending order puts the result on the planned letter.
- Set of 10 or more problems: every letter correct at least once; no letter correct in more than 40 % of the problems; never the same letter three times in a row. Smaller sets: no letter correct more than twice (from 8 problems: 40 %), at most 2 equal letters in a row. The script warns.
- Results are spread: not always the largest or the smallest option.

## Figures
- Inline SVG, black lines on white, grey fill plus hatching or label where two areas must be told apart (nothing by colour alone).
- Exact: counts, equal lengths and right angles drawn as stated. A figure that cannot be to scale carries "Skizze nicht maßstabsgetreu / sketch not to scale".
- Labels inside the picture; `role="img"` and an `aria-label` (German / English) that states every fact a solver needs.
- Option pictures: five small SVGs of equal size, each inside its `data-option` item.
- Width at most 40 mm for a simple figure, 70 mm for grids and nets; figure directly under its stem.

## Originality
- Allowed: the general problem types of school mathematics and recreational mathematics (heads and legs, working backwards, magic squares, counting triangles).
- Not allowed: a competition problem's wording, numbers, figure, story or option set, also not translated or with changed numbers only.
- Write from the plan (idea + result), not from a remembered problem. If a draft feels like a known competition problem, change story, structure and numbers.
- Past papers are named to the user as further practice with the link in `sources.md`; they are not embedded.

## Uniqueness and correctness
- State what is needed for one answer: `genau eines`, `verschiedene Ziffern`, `ganze Zahl`, `gleich große Quadrate`, direction of counting.
- Logic problems: all cases checked in `pruefung.py`; exactly one case survives.
- Optimisation ("kleinstes", "größtes", "mindestens"): the script searches all cases; the solution text shows both that the value is reached and that nothing better exists.
- Geometry with a figure: the script models the figure (cells, coordinates), it does not restate the formula of the solution.
