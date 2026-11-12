---
name: darshan-singh-meel-kaenguru
description: Preparation material for the Känguru der Mathematik competition (Math Kangaroo) for Klassenstufen 3/4, 5/6, 7/8, 9/10 and 11-13 - original multiple-choice problems (A-E) in the competition's style with 3, 4 and 5 points, plausible distractors, full worked solutions, strategy training (elimination, estimation, symmetry, working backwards and more), practice sets and timed mock tests with answer sheet and scoring, in German with the closest natural English sentence under every line. Every answer is recomputed by a Python check and compared with the key in the solution files. Use with darshan-singh-meel-schule whenever Känguru training material is created or changed. Triggers - "Känguru", "Känguru der Mathematik", "Mathe-Känguru", "Känguru-Wettbewerb", "Känguru-Training", "Känguru-Aufgaben", "Knobelaufgaben im Känguru-Stil", "Übungswettbewerb", "Probewettbewerb", "Antwortzettel", "Multiple-Choice-Aufgaben im Känguru-Stil", "3-Punkte-Aufgaben", "Wettbewerbsvorbereitung Mathematik"; "Math Kangaroo", "Kangaroo practice", "Kangaroo mock test", "kangaroo-style problems", "Kangaroo strategies", "math competition practice".
---

# Känguru der Mathematik: training material

Load `darshan-singh-meel-schule` first: it owns templates, the language rule, the review rubric, privacy and the check script. This skill adds the competition: rules, levels, how a problem is built, strategies, the formats for practice set and mock test. Nothing from the base is repeated here.

## Scope
| Klassenstufe | Folder `<stufe>` | Tasks / start points / maximum | Read |
|---|---|---|---|
| 3/4 | `jg03-04` | 24 / 24 / 120 | `references/klassen-03-04.md` |
| 5/6 | `jg05-06` | 24 / 24 / 120 | `references/klassen-05-06.md` |
| 7/8 | `jg07-08` | 30 / 30 / 150 | `references/klassen-07-08.md` |
| 9/10 | `jg09-10` | 30 / 30 / 150 | `references/klassen-09-10.md` |
| 11-13 | `jg11-13` | 30 / 30 / 150 | `references/klassen-11-13.md` |

Output folder: `unterricht/kaenguru/<stufe>/<thema>/` (`<thema>`: `uebungswettbewerb-01`, `rueckwaertsarbeiten`, `gemischte-uebung-01`).

| Output | Files |
|---|---|
| Übungsblatt (practice set, by strategy, topic or mixed) | `arbeitsblatt.html` + `loesung.html` |
| Übungswettbewerb (timed mock test with answer sheet) | `test.html` + `erwartungshorizont.html` |
| Strategy explanation for students | `erklaerung.html` |
| Training lesson (AG, Förderstunde, Vertretung) | `stundenentwurf.html` |
| Steps or motion (net folds to a cube, working backwards, counting by layers) | `animation.html` |
| Proof that every key is right | `pruefung.py` in the same folder |

## Rules
- **Competition facts** (tasks, time, points, deduction, aids, date) only from `references/wettbewerb.md`; they change - lines marked `check:` are named in the reply as unverified; files state only the rule the material applies (`Mehrfachmarkierungen zählen hier als falsch`). Mock tests print the rules in the head.
- **Original problems only.** Never copy, translate or lightly renumber a competition problem, its figure or its story. Do not open a past paper while writing. Every file carries the footer "Übungsmaterial im Stil des Wettbewerbs … keine Wettbewerbsaufgaben". No logo, no mascot drawing, no claim to be official.
- **Form.** Every problem: one question, five options (A)-(E), exactly one correct, solvable without calculator. Options in one form, numbers ascending, units in every option.
- **Points.** 3, 4 or 5 per problem, in rising order in the file. Calibration: `references/aufgabenbau.md`. A mock test has equal thirds of 3-, 4- and 5-point problems.
- **Distractors.** Each wrong option is the result of one nameable mistake or misreading; the solution names it. No filler numbers.
- **Level.** Only knowledge the level file lists. The younger class of the pair (3, 5, 7, 9, 11) sits the same paper: what only the older class has learned is not needed for 3-point problems.
- **Verified.** Every key is computed in `pruefung.py` by a way that does not copy the solution text (brute force, enumeration, exact fractions); the script also proves that exactly one option equals the result.
- **Solutions teach.** Per problem: letter and value, steps a student of the level can follow, the strategy by name, the mistake behind each distractor. Where it exists: a second way.
- **No grades.** A mock test is scored in competition points, never with a grade key (organiser's FAQ: `wettbewerb.md`, row Grades). AFB labels (3 P = I, 4 P = II, 5 P = III) are a working aid for the base check script, not a rule of the competition - the Erwartungshorizont says so.
- **Curriculum.** Cite the Kompetenzbereich Problemlösen with the wording in the level file; Klassen 11-13: as `klassen-11-13.md` says. The competition has no published syllabus.
- **Privacy.** Invented first names only; score lists and filled answer sheets are never stored or quoted.

## Process (fixed)
1. **Setup** - one AskUserQuestion prompt (replaces base questions 1, 2, 5, 6; base question 4 "Sprache" is added as the fourth):

   | Question | Options |
   |---|---|
   | Klassenstufe | 3/4 · 5/6 · 7/8 · 9/10 · 11-13 (from the request; no default) |
   | Format (multi) | Übungsblatt + Lösung, 6-9 Aufgaben (Recommended) · kurzer Übungswettbewerb, 9-15 Aufgaben · voller Übungswettbewerb, 24 bzw. 30 Aufgaben in 75 min · Strategie-Erklärung · Trainingsstunde |
   | Schwerpunkt | gemischt wie im Wettbewerb (Recommended) · eine Strategie · ein Themenfeld (Zahlen, Geometrie, Logik, Kombinatorik) |

   Differenzierung (base question 6) is not asked: the 3-, 4- and 5-point problems are the levels. DaZ, LRS or Förderbedarf named in the request → base `differenzierung.md` for layout and support; the problems stay the same, stems may be read aloud neutrally (`wettbewerb.md`, row Support needs).
2. **Read** `wettbewerb.md`, the level file, `aufgabenbau.md`, `formate.md`; `strategien.md` for strategy sets, explanations and lessons; `begriffe.md` for the glossary and the English lines.
3. **Plan** - one row per problem: nr · points · field · strategy · idea in one line · result · the four mistakes behind the distractors · key letter. Fix the key letters here (balance rule in `aufgabenbau.md`); files only copy the plan.
4. **Write `pruefung.py` first** (contract in `formate.md`), run it, repair the plan until every row is `OK`.
5. **Create** the files from the base templates plus the blocks in `references/templates/bloecke.html`, pair by pair (German line, then its English line).
6. **Self-check every problem and answer** - from the printed text, not from the plan:
   - solve it again cold, by a second way where one exists; the result is the keyed option;
   - try to make each wrong option right by another reading of the text; if one works, rewrite the text;
   - the figure shows exactly what the text says (counts, lengths, positions); the `aria-label` describes it fully;
   - time: a prepared adult needs at most 1 min (3 P), 2 min (4 P), 3 min (5 P), no calculator, no long written arithmetic;
   - only knowledge from the level file; sentence length fits the age;
   - letter, value and steps agree in task file, key file, `pruefung.py`, explanation and animation.
   A problem that fails is rewritten and `pruefung.py` extended. Keep the table (nr · result · second way · key · time) for the reply.
7. **Scripts** - `python <base skill dir>/scripts/check_material.py <folder>`, `python <this skill dir>/scripts/kaenguru_check.py <folder>` (also runs `<folder>/pruefung.py`). Fix every FAIL; read every `?`. Then print preview: no problem split across pages, figure next to its text, answer sheet on one page, key files within the page limit of `formate.md`.
8. **Hand over** - files (relative paths), level, number of problems, time, maximum score, key string, the self-check table, every `check:` that applies. Offer: "Soll `darshan-singh-meel-kaenguru-review` das Material prüfen?" - run it only on a yes.

## References (load only what the task needs)
| File | Read when |
|---|---|
| `references/wettbewerb.md` | always: rules, scoring, time, aids, dates, what is not verified |
| `references/klassen-03-04.md` … `klassen-11-13.md` | the level asked for: knowledge allowed, problem families per 3/4/5 points, language, KC citation |
| `references/aufgabenbau.md` | always: anatomy of a problem, difficulty, distractors, key balance, figures, originality |
| `references/strategien.md` | strategy sets, explanations, lessons, solution texts; test tactics (time, guessing) |
| `references/formate.md` | writing any file: markup, head, answer sheet, scoring block, mock-test sizes and times, `pruefung.py` contract |
| `references/begriffe.md` | glossary and English lines: `DE | EN` |
| `references/templates/bloecke.html` | CSS and HTML blocks added to the base templates |
| `references/examples/` | one worked example (Klassen 3/4, mixed practice set: worksheet, solution, `pruefung.py`) |
| `references/sources.md` | where each fact comes from; what is not verified |

Script: `scripts/kaenguru_check.py <folder>` - options A-E complete and distinct, points 3/4/5 rising, equal thirds, start points, maximum (`data-max`), time against competition pace, answer sheet cells, key letters and their balance, `data-stufe` and footer in every file; runs `pruefung.py` and fails when its problem numbers or letters differ from the key file. `scripts/kaenguru_check.py score <key file> <answers>` scores one answer string (`A`-`E`, `-` = empty).
