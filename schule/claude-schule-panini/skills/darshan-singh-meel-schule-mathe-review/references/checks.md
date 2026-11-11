# Maths checks (added to the base rubric)

Base areas 1-12 stay in force (`darshan-singh-meel-schule/references/review.md`). M1-M13 sharpen areas 1, 2, 3, 5, 6, 7, 9 and 10 for Mathematik. References named below belong to `darshan-singh-meel-schule-mathe`.

## Checks
| # | Area | Check | Must when |
|---|---|---|---|
| M1 | Curriculum level | Grundschule/Sek I: Kompetenzbereich + Kompetenzerwartung with stage + Inhaltsfeld as in `grundschule.md` / `sek1.md`, wording as printed. Oberstufe: Kurshalbjahr.Themenfeld, GK/LK, K-code as in `oberstufe.md`. Content belongs to the stated stage or course; prior knowledge used was taught earlier | reference missing or invented; LK-only content in GK material (Hypothesentest, Normalverteilung, Rotationskörper, Vektorprodukt, partielle Integration ...); a task needs a method the level does not have; Sek I content of a later double year of `sek1.md` table 7.3 (quadratic equation in Jg. 8), unless the material states that the school's curriculum places it earlier; Oberstufe: Kompetenzbereich without the standard code (`K5` instead of `K5.4`) is a Should |
| M2 | Every result | own result = material's result for every task and sub-task: value, sign, unit, form asked for (gekürzt, gemischte Zahl, gerundet, exakt); solution set complete; every printed intermediate step true; at least one `data-check` per task tests the final answer against the given data (a slope-only check for a line equation is a Should even when the answer is right) | any wrong result or step; incomplete solution set; a solution that answers another question than the task asks |
| M3 | Solvable, unique, fair | all data given; no contradiction; exactly one reading; domain stated where it matters; "find all" bounded; no part that needs the result of a failed part without a fallback value (tests); surplus data only on purpose and named in the solution | missing or contradictory data; two valid readings with different results; a test part that cannot be started after an earlier error |
| M4 | Numbers for the level | Zahlenraum of the year incl. intermediate results (Grundschule); by-hand tasks come out clean; calculator tasks state the rounding; no result guessable from the page; no two tasks with the same result; contexts realistic (prices, speeds, sizes) | numbers outside the level's range in a graded task; a "by hand" task that needs a calculator; an impossible context value that the task depends on |
| M5 | Notation and form | German notation as in `konventionen.md` (decimal comma, `·`, `:`, `P(2|3)`, `[a; b]`, `−`); `=` only between equal things (no chain like `3 + 4 = 7 · 2 = 14`); `≈` after rounding; units in every line; variables defined; MathML/HTML formulas, no images; Oberstufe notation of the Landesabitur "Hinweise" | a formula that is mathematically wrong as written (equals-chain, missing brackets, wrong limits); notation that changes the meaning |
| M6 | Solution quality | result first; steps a student of the level can follow, in the method the class uses; Probe / plausibility; Antwortsatz for context tasks; one typical mistake per task that is real for the topic; open tasks with criteria and a model answer | solution uses a method not available at the level or not in the info box; reasoning task "solved" by a calculation only |
| M7 | Operators, AFB, tools | operator from the base list, du/Sie form; AFB fits the real demand (a routine repeated from an earlier part is not AFB III); aids stated on every test; Oberstufe: `berechnen` only where a by-hand way exists, `bestimmen/ermitteln` where the calculator is meant, the rule printed on the paper; no calculator-specific notation in solutions; hilfsmittelfreier Teil really solvable without aids | AFB III missing in an Oberstufe Klausur; `berechnen` on a task that has no by-hand way; aids missing on a graded test |
| M8 | Marking scheme | points per step awardable (Ansatz, Rechnung, Ergebnis, Antwort); sub-points = part points; parts = total; test = Erwartungshorizont (ids, points, AFB); AFB table recomputed; grade key recomputed from the percentages, falling, right scale, rounding as `konventionen.md` (Oberstufe exact; Sek I exact or up to the next half point, stated under the key); tolerance for rounded values; Folgefehler and other ways stated | any sum wrong; key thresholds wrong; points that cannot be awarded from the description |
| M9 | Figures | coordinates follow the stated scale (recompute three points); graph passes through the points the text names (zeros, vertex, intercepts); axes labelled, equal units unless stated; right angles, equal lengths and parallel lines marked and true; fraction pictures with exactly equal parts; `nicht maßstäblich` where it applies; figure agrees with the task data | a figure that contradicts the data or shows wrong maths; a task that depends on measuring a figure that is not to scale |
| M10 | Animation maths | each step true on its own (equal parts equal, a moved piece keeps its size, constructions in a valid order, graph states computed); captions say what changes and why; start = question, last step = solution, same numbers as worksheet; limit processes shown as stages and named as such; needed at all (change, construction or sequence) | a step that shows false maths; end state differs from the solution |
| M11 | Understanding and differentiation | a picture or action carries each new rule (Grundschule: E-I-S visible); at least one reasoning, error-analysis or reversed task; three levels differ in help or complexity, not in topic; ★★★ is not "more of the same" | - (Should), unless a requested level is missing |
| M12 | Bilingual, maths side | English term from `begriffe.md` (false-friends table); same numbers and units in both lines; decimal comma in German lines and formula-only lines, decimal point in English sentences incl. formulas inside them (`r(t) = −0.3t² + 2.4t`); formulas otherwise identical; formula-only lines not duplicated; singular after fractions below one (`3/4 litre`); operator pair from base `operatoren.md`; fixed phrases as in `begriffe.md` | wrong subject term that changes the maths (`Stelle`/`Punkt`, `kürzen`, `Körper`) or a different number in the English line |
| M13 | Print, maths side | formulas unbroken; fraction bars and exponents readable at print size; squared field ≥ model solution + 2 lines; written algorithms one digit per square; no sum row repeated on every page; grade key in one piece; page count sensible for the level | answer field clearly too small for the calculation; a formula cut or broken so that it reads wrong |

## Table for the independent solutions (goes into the report as "Nachgerechnet")
```markdown
| Task | Own way | Own result | Second way / estimate | Material says | Match |
|---|---|---|---|---|---|
| 2b | 9/12 + 10/12 | 19/12 = 1 7/12 | 0,75 + 0,83 ≈ 1,58 | 1 7/12 | yes |
```
- Exact arithmetic (fractions, integers) wherever the task allows; round once at the end.
- "Match" = value, sign, unit, form and rounding. On a difference, find the cause (rounding chain, sign, reading of the task) before writing the finding - it may be the task that is ambiguous (M3), not the solution that is wrong.
- Proofs and reasons: list the necessary steps of the argument first, then compare; a gap in the Erwartungshorizont is a finding.
- "Find all" tasks: state how completeness was shown (enumeration, bound, algebra).
- Points and key: one line for the sub-points of every part (`2a: 2 + 1 + 1 = 4`, counted from the text, compared with `data-teilpunkte` and the part's points), one line each for total, AFB sums and every threshold.

## Frequent defects (look for these first)
- Result right, intermediate step wrong (copied from an earlier version of the task).
- Wrong final answer with a green script: the `data-check` tests only one part (slope without intercept) or repeats the wrong value.
- Task changed, solution not: other numbers in Arbeitsblatt and Lösung; `data-check` still passes because it checks the old numbers.
- "Find all" with a missed case (0, negative solution, improper fraction, symmetric pair).
- Equals-chains; unit missing in the last line; `≈` missing; comma kept in the English prose line.
- Grundschule: intermediate result leaves the Zahlenraum; subtraction method differs from the class's method; too little squared space.
- Fractions: result not simplified although the task says so; picture with unequal parts.
- Functions: sketch does not pass through the computed points; `Stelle` asked, point given.
- Integral: area across a zero computed as one integral; unit of rate × time wrong in the Antwortsatz.
- Stochastics: `P(X ≥ k)` as `1 − F(k)`; rounded probabilities that do not add up to 1 without a note.
- Oberstufe: `berechnen` for a cumulated binomial value; LK-only content in a GK Klausur; AFB III part that only repeats an earlier routine.
- Points: sub-points in the text add to more than the part or differ from `data-teilpunkte`; sub-point written without colon after a number (`... 0 und 4 1 BE`); AFB table not updated after a change; Oberstufe key with 6 rows or thresholds rounded.
- English line: "shorten" for kürzen, "break" for Bruch, "Given is ...", "3/4 litres".
- Animation: pieces change size while moving; last caption gives another form of the result than the solution.

## Verdict
Base rule. Maths addition: one Must in M2, M3 or M8 that changes a task, a solution or the grading → at best "Einsatzbereit nach Must-Korrekturen"; a wrong grade key, a test part that is unsolvable, or more than three Must → "Überarbeiten".
