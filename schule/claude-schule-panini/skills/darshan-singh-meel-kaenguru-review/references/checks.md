# Känguru checks (K1-K14)

Added to the 12 areas of the base `review.md`. Rule sources: `wettbewerb.md`, `aufgabenbau.md`, `formate.md` and the level file of `darshan-singh-meel-kaenguru`.

## Blind-solving table (step 3, before any key is opened)
| Nr. | P | Own result | Own letter | Way (strategy) | Second way or Python | Time | (A) | (B) | (C) | (D) | (E) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3 | … | … | … | … | … min | mistake or "none" | … | … | … | … |

- Columns (A)-(E): for the correct option "richtig"; for each wrong option the mistake that produces it, or "none found".
- Time: your own time with paper only. Limit for a prepared adult: 1 min (3 P), 2 min (4 P), 3 min (5 P).
- Own Python check: computes the result from the stem's data over all cases and prints which options equal it. Exactly one must.

## Checks
| # | Check | How | Must when |
|---|---|---|---|
| K1 | Key correct | own result = keyed option, in task file, key line, solution, Erwartungshorizont row and `pruefung.py` | any key wrong; files disagree |
| K2 | Exactly one correct option | each wrong option tested against the stem under every reasonable reading (inclusive/exclusive counting, "zwischen", leading zeros, order matters or not, figure to scale or not) | two options defensible; none correct |
| K3 | Stem complete and unambiguous | all data needed are given; unused data only when intended; words that decide (genau, mindestens, höchstens, verschieden, je) present where needed; one question | data missing; the question allows two readings with different answers |
| K4 | Figure | counts, lengths, positions equal the stem; drawn exactly or marked "nicht maßstabsgetreu"; `aria-label` states every needed fact; readable in black-and-white print | figure contradicts the stem; a needed fact exists only as colour |
| K5 | Options form | five, A-E in order, same form, numbers ascending, units in each, no duplicates, no absurd outlier in 4-5 P | fewer or more than five; duplicate values; unit missing so that the answer is unclear |
| K6 | Distractors | each wrong option follows from a nameable mistake; the solution's stated mistake really gives that value (recompute it); correct value not marked by a special property | a stated distractor calculation is wrong (Should when only the explanation is wrong, Must when it makes the option correct) |
| K7 | Points and difficulty | 3 P: one known idea; 4 P: two ideas or a chosen strategy; 5 P: insight or several conditions; rising inside the file; difficulty from the idea, not from long arithmetic; own times within the limits | a 3-point problem needs a 5-point idea or the reverse so clearly that the set misleads; arithmetic not feasible without calculator |
| K8 | Level | only knowledge the level file allows; 3-point problems solvable by the younger class of the pair; sentence length and terms fit the age | content of a later level is required |
| K9 | Mock-test structure | equal thirds 3/4/5; start points = number of problems; time at competition pace (table in `formate.md`); rules box equals `wettbewerb.md`; answer sheet cells = problems; no key, AFB or strategy on the test; one `data-stufe` on every file | thirds unequal; start points or deduction stated wrongly; answer sheet does not match |
| K10 | Scoring block | start, + 3/4/5, 0, − 0,75/− 1/− 1,25, maximum; every printed maximum (meta line, answer sheet, Auswertung) and the sum written beside it ("6 + 24 = 30") recomputed - the script checks only the number tagged `data-max`; worked example recomputed; "several letters" marked as this material's rule; no grade key | any number in the scoring block wrong; a grade key derived from competition points |
| K11 | Key balance | letter counts, runs, position of the correct value among the ordered options (not always the middle, largest or smallest) | - (Should) |
| K12 | Verification script | `pruefung.py` exists, runs, covers every problem, computes from the stem's data, checks all five options, asserts uniqueness where promised; its letters equal `data-loesung` of the key file (script) and the letters printed in the key line and solution text (by hand); `HAND` problems solved by hand | script missing or failing; a function returns a constant for a computable problem; a letter differs anywhere |
| K13 | Originality and claims | footer "keine Wettbewerbsaufgaben" present; no logo or mascot; no claim to be official; no problem that reproduces a known competition problem's wording, numbers, figure or option set; competition rules attributed to the organiser's page, not invented | copied or translated competition problem; material presents itself as official |
| K14 | Solutions teach | per problem: letter + value, steps a student of the level can follow, strategy name from `strategien.md`, mistakes behind the distractors; a check ("Probe") where working backwards is used; optimisation: shown that the value is reached and cannot be beaten | solution steps contain a wrong statement; the argument for "smallest/largest" is missing in a 5-point problem (Should) |

## Frequent defects of multiple-choice problems
| Defect | Example | Finding |
|---|---|---|
| Counting convention open | "Wie viele Zahlen liegen zwischen 10 und 20?" (9 or 11) | K2/K3: state "größer als 10 und kleiner als 20" |
| Start day counted or not | "in 60 Tagen" vs. "am 60. Tag" | K3 |
| Hidden assumption in a figure | squares "look" equal, angle "looks" right | K4: say it in the stem |
| Digit vs. number | "Wie oft schreibt er die 3?" (33 once or twice) | K3: "die Ziffer 3" |
| Uniqueness not forced | truth/lie puzzle with two consistent cases | K2: add a statement; prove with all cases |
| Optimum claimed, not proven | "kleinstes Ergebnis" found by one good try | K14 |
| Answer leaks | only one option has the right last digit, unit or parity in every problem | K6/K11 |
| Distractor equals a correct second reading | perimeter option right if inner edges count | K2 |
| Translation changes the problem | "mindestens" → "at most"; "je" dropped | base area 7, Must |
| Options not ordered | 12, 8, 20, 6, 18 | K5 (Should) |
| Same letter pattern | key A B C D E A B C D E | K11 |
| Process note in the material | `check: KCGO PDF` in the meta line; "Mehrfachmarkierung beim Veranstalter nachfragen"; "wie gewünscht 12 Aufgaben" | base area 6 (Should): state the rule or scope as a fact ("Mehrfachmarkierungen zählen hier als falsch") |
| Stem longer than the idea | five sentences of story for one subtraction | K7/K8 (Should) |

## Report additions
- Section "Nachgerechnet": the blind-solving table, shortened to: problem · points · own result · own letter · key · match · other options wrong · time.
- Section "Not checked": always list what could not be verified - originality against all past papers (no systematic comparison), print on paper, rules after the date in `sources.md`.
- Verdict words as in base `review.md`. A wrong key or a second defensible option (K1, K2) is a Must in base area 2 and leads to "Überarbeiten" when more than one problem is affected.
