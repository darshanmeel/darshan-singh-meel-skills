---
name: darshan-singh-meel-kaenguru
description: Preparation material for the Känguru der Mathematik competition (Math Kangaroo) for Klassenstufen 3/4, 5/6, 7/8, 9/10 and 11-13 - original multiple-choice problems (A-E) in the competition's style with 3, 4 and 5 points, plausible distractors, full worked solutions, strategy training (elimination, estimation, symmetry, working backwards and more), practice sets and timed mock tests with answer sheet and scoring, in German with the closest natural English sentence under every line. Every answer is recomputed by a Python check and compared with the key in the solution files. Use with darshan-singh-meel-schule whenever Känguru training material is created or changed. Triggers - "Känguru", "Känguru der Mathematik", "Mathe-Känguru", "Känguru-Wettbewerb", "Känguru-Training", "Känguru-Aufgaben", "Knobelaufgaben im Känguru-Stil", "Übungswettbewerb", "Probewettbewerb", "Antwortzettel", "Multiple-Choice-Aufgaben im Känguru-Stil", "3-Punkte-Aufgaben", "Wettbewerbsvorbereitung Mathematik"; "Math Kangaroo", "Kangaroo practice", "Kangaroo mock test", "kangaroo-style problems", "Kangaroo strategies", "math competition practice".
---

# Känguru: training material
Scope: practice sets, mock tests, strategy texts, lessons. Load `darshan-singh-meel-schule` first (templates, language rule, rubric, privacy, check script); not repeated here. `→` then · `·` list · rec recommended.

## Levels
| Stufe | `<stufe>` | tasks = start pts / max | read |
|---|---|---|---|
| 3/4 | `jg03-04` | 24 / 120 | `references/klassen-03-04.md` |
| 5/6 | `jg05-06` | 24 / 120 | `references/klassen-05-06.md` |
| 7/8 | `jg07-08` | 30 / 150 | `references/klassen-07-08.md` |
| 9/10 | `jg09-10` | 30 / 150 | `references/klassen-09-10.md` |
| 11-13 | `jg11-13` | 30 / 150 | `references/klassen-11-13.md` |

## Output
`unterricht/kaenguru/<stufe>/<thema>/` · `<thema>` = `uebungswettbewerb-01` · `rueckwaertsarbeiten` · `gemischte-uebung-01`.
- Übungsblatt → `arbeitsblatt.html` + `loesung.html`
- Übungswettbewerb → `test.html` + `erwartungshorizont.html`
- Strategie-Erklärung → `erklaerung.html` · Trainingsstunde → `stundenentwurf.html` · Schritte/Bewegung → `animation.html`
- Key proof → `pruefung.py` (same folder)

## Rules
- Competition facts (tasks, time, points, deduction, aids, date) only from `references/wettbewerb.md` · line `check:` → tell user "unverified" · mock test prints rules in head.
- Original only: never copy, translate, renumber a competition problem, figure or story · never open a past paper · footer "Übungsmaterial im Stil des Wettbewerbs … keine Wettbewerbsaufgaben" · no logo, mascot, official claim.
- Form: one question · five options (A)-(E) · exactly one correct · no calculator · one option form · numbers ascending · units in every option.
- Points 3/4/5 rising in file · calibration `aufgabenbau.md` · mock test = equal thirds.
- Distractor = one nameable mistake or misreading, named in solution · no filler numbers.
- Level: only knowledge in level file · younger class of pair sits same paper → 3-pt needs nothing only the older class learned.
- Verified: every key computed in `pruefung.py` independently of solution text (brute force · enumeration · exact fractions) · proves exactly one option equals result.
- Solutions teach: letter + value · steps a student can follow · strategy by name · mistake per distractor · second way if any.
- No grades: score in competition points only (`wettbewerb.md` row Grades) · AFB labels (3 P = I, 4 P = II, 5 P = III) = aid for base check script, not competition rule → Erwartungshorizont says so.
- Curriculum: Kompetenzbereich Problemlösen, wording from level file · Klassen 11-13 `check: KCGO Mathematik` · competition has no syllabus.
- Privacy: invented first names · never store or quote score lists, filled answer sheets.

## Process
1. Setup: one AskUserQuestion (replaces base Q 1, 2, 5, 6; base Q4 Sprache = 4th):
   - Klassenstufe: 3/4 · 5/6 · 7/8 · 9/10 · 11-13 (from request; no default)
   - Format (multi): Übungsblatt + Lösung 6-9 Aufgaben (rec) · kurzer Übungswettbewerb 9-15 · voller Übungswettbewerb 24/30 in 75 min · Strategie-Erklärung · Trainingsstunde
   - Schwerpunkt: gemischt (rec) · eine Strategie · ein Themenfeld (Zahlen · Geometrie · Logik · Kombinatorik)
   - No Differenzierung question (3/4/5 pts are the levels) · DaZ, LRS, Förderbedarf named → base `differenzierung.md`, same problems, stems may be read aloud (`wettbewerb.md` row Support needs).
2. Read `wettbewerb.md` · level file · `aufgabenbau.md` · `formate.md` · `strategien.md` (strategy sets, explanations, lessons) · `begriffe.md` (glossary, English lines).
3. Plan, row per problem: nr · points · field · strategy · idea · result · four distractor mistakes · key letter → letters fixed here (balance rule `aufgabenbau.md`); files copy the plan.
4. Write `pruefung.py` first (contract `formate.md`) → run → fix plan until all `OK`.
5. Create files from base templates + `references/templates/bloecke.html` · pair by pair (German line → English line).
6. Self-check each problem from printed text, not plan:
   - solve cold, second way if any → keyed option
   - each wrong option made right by another reading? → rewrite stem
   - figure = text (counts, lengths, positions) · `aria-label` full
   - prepared adult ≤ 1 min (3 P) · 2 (4 P) · 3 (5 P) · no calculator, no long arithmetic
   - level knowledge only · sentence length fits age
   - letter, value, steps agree in task, key, `pruefung.py`, explanation, animation
   - fail → rewrite + extend `pruefung.py` · keep table (nr · result · second way · key · time) for reply.
7. Scripts: `python <base skill dir>/scripts/check_material.py <folder>` · `python <this skill dir>/scripts/kaenguru_check.py <folder>` (also runs `pruefung.py`) → fix every FAIL, read every `?` → print preview: no split problem · figure by text · answer sheet one page · key files within page limit (`formate.md`).
8. Hand over: files (relative) · level · problems · time · max score · key string · self-check table · applicable `check:` → offer "Soll `darshan-singh-meel-kaenguru-review` das Material prüfen?" → run only on yes.

## References
- `references/wettbewerb.md` always: rules, scoring, time, aids, dates, unverified
- `references/klassen-*.md` level asked: allowed knowledge, families per 3/4/5 pts, language, KC citation
- `references/aufgabenbau.md` always: anatomy, difficulty, distractors, key balance, figures, originality
- `references/strategien.md` strategy sets, explanations, lessons, tactics
- `references/formate.md` any file: markup, head, answer sheet, scoring block, sizes, times, `pruefung.py` contract
- `references/begriffe.md` glossary `DE | EN`
- `references/templates/bloecke.html` CSS/HTML blocks for base templates
- `references/examples/` Klassen 3/4 mixed practice set (worksheet, solution, `pruefung.py`)
- `references/sources.md` fact sources, unverified items

## Script
- `scripts/kaenguru_check.py <folder>`: options A-E complete + distinct · points 3/4/5 rising · equal thirds · start points · `data-max` · time vs pace · answer-sheet cells · key letters + balance · `data-stufe` + footer · runs `pruefung.py`, fails on differing numbers/letters.
- `scripts/kaenguru_check.py score <key file> <answers>` → scores one string (`A`-`E`, `-` empty).
