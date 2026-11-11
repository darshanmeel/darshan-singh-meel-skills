# Formats (additions to the base `formate.md`)

Base templates, CSS, toolbar, DE/EN markup and print rules stay as they are. This file adds what a multiple-choice competition needs. Blocks to copy: `templates/bloecke.html`.

## Attributes the scripts read
| Where | Attribute | Value |
|---|---|---|
| `<body>` of every `.html` in the folder | `data-stufe` | `jg03-04` · `jg05-06` · `jg07-08` · `jg09-10` · `jg11-13`, the same value in all files |
| `<body>` of `test.html` | `data-start` | start points = number of problems |
| `<body>` of `test.html` | `data-zeit` | working time in minutes |
| problem in task file | `data-aufgabe`, `data-punkte` (3, 4, 5), `data-afb` (I for 3, II for 4, III for 5) | base check script sums the points |
| each option | `data-option` | `A` … `E`, in this order |
| problem in key file | same `data-aufgabe`, `data-punkte`, `data-afb`, plus `data-loesung` | one letter |
| answer sheet cell | `data-antwort` | problem number, same order as the problems |
| total | `data-gesamt` | sum of problem points **without** start points |
| every printed maximum score of a mock test (meta line and answer sheet of `test.html`, Auswertung of `erwartungshorizont.html`) | `data-max` | start points + `data-gesamt`, on an element that holds only the number: `<b data-max="30">30</b>` |

- Klassen 3/4: `<body class="gs">` (14 pt) on student files only (`arbeitsblatt`, `test`, `erklaerung`, `animation`). Key files and `stundenentwurf` are read by the teacher: no `gs`.
- One problem set per `<thema>` folder (a practice set and a mock test go to two folders): `pruefung.py` proves exactly the problems of the folder's key file.
- No answer space per problem: the answer is a letter (circled on a practice set, entered in the answer sheet of a mock test). This replaces the base rule "one answer space per task".
- Head line of every file: `Mathematik · Känguru-Training · Klassen <x/y>`; name, class and date as blank fields on student files.
- Footer of every file (`.fuss`, block 9), also `erklaerung`, `stundenentwurf` and `animation`: "Übungsmaterial im Stil des Wettbewerbs. Alle Aufgaben sind neu geschrieben; es sind keine Wettbewerbsaufgaben." with its English line. The script fails a file without it.
- Print length of key files: `loesung.html` at most 1 A4 page per 2 problems (6 problems: 3 pages), `erwartungshorizont.html` one page more. Longer → shorten steps, keep mistakes inline.

## arbeitsblatt.html + loesung.html (practice set)
- 6-9 problems; points rising; stars as in the base: ★ = 3 P, ★★ = 4 P, ★★★ = 5 P (`data-niveau` basis, standard, herausforderung).
- Meta line: time (problems × 3 min in Klassen 3-6, × 2,5 min from Klasse 7, rounded up to 5), sum of points.
- Info box "Das brauchst du": how to answer (circle the letter), aids (scratch paper, no calculator), the strategy or tip of the set in at most 2 lines.
- Each problem: heading with number, stars, points → stem pair → figure → options.
- Lösung: line with all key letters; per problem `Lösung: (X) value`, steps as pairs, `Strategie`, one pair `Typische Fehler: (A) what was done wrong; (B) …` (inline, no box: a box per problem doubles the print length). A distractor without a real mistake behind it is listed as `Nachbarwert`.
- Glossary at the end of both files.

## test.html + erwartungshorizont.html (Übungswettbewerb)
| Block | Content |
|---|---|
| Meta line | "Übungswettbewerb", working time, aids ("Stift, Schmierpapier, Zeichengeräte; kein Taschenrechner"), start points + points (`data-gesamt`) = maximum (`data-max`) |
| Regeln | exactly one of five answers is correct; letter into the answer sheet; correct = points of the problem; wrong = minus a quarter; empty = 0 |
| Three sections | "3-Punkte-Aufgaben", "4-Punkte-Aufgaben", "5-Punkte-Aufgaben", equal numbers |
| Problem | number, stem pair, points at the right, figure, options |
| Antwortzettel | last page: one cell per problem, fields for Richtig, Falsch, Leer, Punkte / maximum (`data-max`) |

Erwartungshorizont ("nur für Lehrkräfte"):

| Block | Content |
|---|---|
| Meta line | KC reference as in the level file (Problemlösen, Kompetenzerwartung with stage, Inhaltsfelder with Leitidee) |
| Lösungsbuchstaben | one line `1D 2C 3A …` for fast marking |
| Erwartete Leistungen | per problem: letter and value, steps, strategy, distractors with their mistake, AFB, points; sum row = `data-gesamt` |
| Auswertung | start points, + 3/4/5, 0, − 0,75/− 1/− 1,25; maximum (`data-max`); no part points; several letters "hier" scored as wrong; one worked example of a score; longest run of correct answers |
| AFB table | points and share per AFB, with the sentence that 3/4/5 → I/II/III is a working aid of the material, not a rule of the competition |
| Hinweise zur Besprechung | discuss the most-missed problems and the most-chosen distractor first; other correct ways count; guessing rule |

- No grade key (`data-ab`): the mock test is not graded. If a user wants a grade from it, refuse the mapping here and point to a Klassenarbeit made with `darshan-singh-meel-schule-mathe`.
- The test shows no AFB labels, no strategy names, no key.

## Sizes and times of a mock test
Time = problems × 75 / full paper, rounded up to the next 5 min. Start points = problems.

| Problems (thirds) | Klassen 3-6 (full: 24) | Klassen 7-13 (full: 30) | Maximum score |
|---|---|---|---|
| 6 (2 + 2 + 2) | 20 min | 15 min | 30 |
| 9 (3 + 3 + 3) | 30 min | 25 min | 45 |
| 12 (4 + 4 + 4) | 40 min | 30 min | 60 |
| 15 (5 + 5 + 5) | 50 min | 40 min | 75 |
| 24 (8 + 8 + 8) | 75 min | - | 120 |
| 30 (10 + 10 + 10) | - | 75 min | 150 |

Maximum = start points + 12 points per triple of problems (3 + 4 + 5).

## pruefung.py (in the topic folder)
Contract - the reviewer and `kaenguru_check.py` rely on it:
- Python standard library only; one function per problem (`a1`, `a2`, …) that **computes** the result from the data of the stem: brute force over all cases, enumeration, exact arithmetic (`fractions`), a model of the figure. It does not print a constant and does not repeat the solution's shortcut.
- Where the stem promises uniqueness, the function asserts it (`assert len(hits) == 1`).
- A table `KEY = {nr: (function, [five options as values], "letter")}`. The main block checks for every problem: the computed result equals the option at the key letter, and no other option equals it.
- Output: one line per problem `OK   Aufgabe 4: berechnet 20 = (B)` - number after `Aufgabe`, key letter in brackets at the line end; ASCII only (Windows consoles); exit code 1 on any `FAIL`.
- `kaenguru_check.py` reads these lines: the problem numbers must be exactly those of the key file and every letter must equal its `data-loesung`. A key changed in one place only fails the run.
- Problems that cannot be computed (pure reading of a picture): the function returns the value from a coded model of the picture (grid, list of pieces); if even that is impossible, the line reads `HAND Aufgabe n` (the script lists it with `?`) and the hand check is written into the reply.
- Example: `examples/jg03-04-gemischte-uebung/pruefung.py`.

## erklaerung.html, stundenentwurf.html, animation.html
- Base templates plus `data-stufe` on `<body>` and the footer (block 9) as the last element of the page content. Content rules: `strategien.md`.
- Stundenentwurf: KC rows from the level file; Stundenziel names the strategy ("Die Lernenden lösen Aufgaben, bei denen das Ende bekannt ist, durch Rückwärtsarbeiten").
- Erklärung "Probier es selbst": 2-3 multiple-choice problems with options A-E and the letters as short solution.

## Checks
1. `python <base skill dir>/scripts/check_material.py <folder>`
2. `python <this skill dir>/scripts/kaenguru_check.py <folder>` - task and key file, `data-max`, `data-stufe` and footer of every `.html`; runs `<folder>/pruefung.py` and compares its letters with the key file
3. Not checked by a script: the numbers printed next to a tagged maximum ("6 + 24 ="), the worked scoring example, level knowledge, print length - self-check and review
