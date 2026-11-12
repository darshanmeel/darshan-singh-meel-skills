---
name: darshan-singh-meel-schule-mathe
description: Mathematics teaching material for Hessen - Grundschule (Jg. 1-4) and Gymnasium (Sek I Jg. 5-10, Oberstufe E-Phase and Q1-Q4, GK and LK, KCGO, Landesabitur rules incl. WTR/CAS) - lesson plans, worksheets with solutions, Klassenarbeiten and Klausuren with Erwartungshorizont, explanations, step animations, in German with an English line under every line. Every task is solved twice; answers and points are recomputed by a check script. Use with darshan-singh-meel-schule whenever maths material is created or changed. Not for Känguru preparation (darshan-singh-meel-kaenguru). Triggers - "Mathematik", "Mathe Arbeitsblatt", "Mathearbeit", "Klassenarbeit Mathe", "Mathe Klausur", "Rechenaufgaben", "Sachaufgaben", "Bruchrechnung", "Gleichungen", "Geometrie", "Funktionen", "Analysis", "Integralrechnung", "Stochastik", "Landesabitur Mathe", "Mathe zweisprachig"; "maths lesson", "math worksheet", "maths test with marking scheme", "word problems", "fractions animation", "bilingual maths".
---

# Mathematik (Hessen: Grundschule + Gymnasium)

Load `darshan-singh-meel-schule` first: it owns formats, templates, folder, language rule, grading, operators, process and review rubric. This skill adds the maths: curriculum content per level, notation, number choice, solution layout, the answer check, animations, terms. Nothing from the base is repeated here.

## Scope
| Level | Curriculum | Read |
|---|---|---|
| Grundschule, Jg. 1-4 | KC Hessen, Primarstufe, Mathematik: 6 Kompetenzbereiche, 5 Inhaltsfelder (= Leitideen), standards for the end of Jg. 4 | `references/grundschule.md` |
| Sek I Gymnasium, Jg. 5-10 | KC Hessen, Sek I Gymnasium, Mathematik: 6 Kompetenzbereiche, 5 Leitideen with 11 Inhaltsfelder, stages Jg. 6, 8, 9/10 | `references/sek1.md` |
| Oberstufe, E, Q1-Q4, GK and LK | KCGO Mathematik (Ausgabe 2024): K1-K6, L1-L5, Themenfelder E.1-Q4.3; Landesabitur structure, WTR/CAS | `references/oberstufe.md` |

Output folder: `unterricht/mathematik/<stufe>/<thema>/` (base convention; `<stufe>` = `jg03`, `jg06`, `e`, `q1-gk`, `q3-lk`).

## Rules
- **Curriculum.** Cite as the level reference says: Kompetenzbereich + Kompetenzerwartung with stage + Inhaltsfeld (Grundschule, Sek I) or Kurshalbjahr.Themenfeld + GK/LK + standard code (Oberstufe). The KC fixes stages, not years: take the year from the school's curriculum or place it by the reference and state the placement in the Stundenentwurf as a fact. LK-only content never appears in GK material.
- **Every task solved, every answer checked.** Solve each task yourself, then confirm it by a second way. Every solution element with `data-aufgabe` carries `data-check` with expressions that recompute the answer; at least one expression puts the final answer back into the task's given data (the line passes through A and B; the solution satisfies the equation). `scripts/check_rechnung.py` must pass. A task that does not come out cleanly is rewritten, not patched in the solution.
- **Numbers fit the level and the goal.** Inside the Zahlenraum of the year; by-hand tasks have clean results; calculator tasks state the rounding; contexts use realistic sizes with units. Build tasks backwards from the result. `references/konventionen.md`.
- **Notation.** German school notation in German lines and in all formulas (decimal comma, `·`, `:`, `P(2|3)`, `[a; b]`); an English sentence uses the decimal point, also in a formula inside it (`g(x) = 1.5x + 2.5`), and changes nothing else in the formula; a formula-only line stands once, in German notation. Formulas as MathML or plain HTML, never images or script libraries. `references/konventionen.md`.
- **Solutions teach.** Result first, then every step a student writes, a Probe or plausibility remark, an Antwortsatz for context tasks, one typical mistake per task. Erwartungshorizont: points per step as `Schritt: n P` and as `data-teilpunkte`, Folgefehler, tolerance for rounded values.
- **Tools named.** Every test states the aids: `ohne Hilfsmittel`, `Taschenrechner (WTR)`, `CAS`, `Formelsammlung`. Oberstufe: `berechnen` = by hand, documented; `bestimmen/ermitteln` = calculator functions allowed and documented; write this rule on the Klausur. GTR: `check:` in `oberstufe.md`.
- **Understanding before rule.** A rule follows a picture or an action that carries it (Grundschule: handelnd → bildlich → symbolisch). Each worksheet has at least one task that asks for a reason, an error analysis or a reversed question.
- **Figures to scale.** SVG coordinates are computed, the scale is stated, sketches are labelled `nicht maßstäblich`.
- **Animation** when dividing, moving, constructing, a changing parameter or a limit process is the idea (fractions, written algorithms, constructions, graphs, Ober-/Untersummen). Exact geometry, same numbers as the worksheet. `references/animationen.md`.
- **Terms.** `DE | EN` from `references/begriffe.md`; the false-friends table there is binding (`kürzen` = simplify, `Stelle` = x-value, `Körper` = solid).
- **School decisions are asked, not guessed**: written subtraction method and division notation (Grundschule), year of calculator introduction, hilfsmittelfreier Teil, WTR or CAS, grade key.

## Process (fixed)
1. **Setup** - the base questions (subject = Mathematik is answered). Add, in the same prompt while at most 4 are open, otherwise in a second prompt:

   | Question | Options |
   |---|---|
   | Hilfsmittel - only when a test is an output (Sek I from Jg. 7, Oberstufe) | ohne Hilfsmittel (Recommended up to Jg. 6) · Taschenrechner (WTR) · CAS · hilfsmittelfreier Teil + Teil mit Hilfsmitteln |
   | Oberstufe only: Kurs | GK (Recommended) · LK · E-Phase |
   | Grundschule, only for written subtraction or division: Rechenverfahren der Klasse | wie im eingeführten Lehrwerk - Verfahren nennen (Recommended) · Abziehverfahren mit Entbündeln · Ergänzungsverfahren |
   | Schwerpunkt der Aufgaben | Üben mit steigender Schwierigkeit (Recommended) · Sachaufgaben/Modellieren · Begründen/Problemlösen · Wiederholung vor der Arbeit |

   Ask for the Jahrgang of the topic in the school's curriculum only when the user gave no year.
2. **Read** the level reference (`grundschule.md`, `sek1.md` or `oberstufe.md`); `konventionen.md` always; `animationen.md` when an animation is planned; `begriffe.md` for glossary and English lines.
3. **Plan** - the base 5 lines plus 4 maths lines: tasks with data **and results** (built backwards) · the second way for each result · representation or material that carries the idea · aids and rounding. Fix all numbers here; the files only copy them.
4. **Create** each output from the base template, pair by pair (German line, then its English line). Formulas once, without an English copy. Put `data-check` on each solution element while writing it.
5. **Self-check every task and answer** - before the layout check, for each task:
   - solve it again from the task text alone, by the second way (`konventionen.md`); both results agree;
   - `python <this skill dir>/scripts/check_rechnung.py <folder>` → every line `OK`, no `?` left (`data-check="-"` only for answers without a number); it also adds up `data-teilpunkte` and recomputes AFB shares and grade key;
   - the task is solvable with the info box, the stated aids and what the plan says was taught; exactly one reading; solution set complete for "find all" tasks;
   - numbers inside the level's range; units in every line; rounding as stated; German comma, English point;
   - same values in Arbeitsblatt, Lösung, Test, Erwartungshorizont, Erklärung, figure labels and animation captions;
   - operator and AFB fit what the task demands; points can be awarded step by step.
   A task that fails is rewritten and checked again. Keep the result as a table (task · result · second way · check) for the reply.
6. **Layout check** - `python <base skill dir>/scripts/check_material.py <folder>` (fix every FAIL, read every `?`). Then look at each file once in print preview: formulas readable (fractions, exponents, no break inside a formula), figures to scale and labelled, squared answer fields large enough for the model solution, no task split across pages, sum row and grade key not broken (`konventionen.md`, print notes).
7. **Hand over** - reply with: files (relative paths), KC reference, the self-check table, school decisions assumed, every `check:` that applies. Offer the review: "Soll `darshan-singh-meel-schule-mathe-review` das Material prüfen?" - run it only on a yes.

## References (load only what the task needs)
| File | Read when |
|---|---|
| `references/grundschule.md` | Jg. 1-4: Kompetenzbereiche, Bildungsstandards, Inhaltsfelder, usual placement, Grundschule rules, typical mistakes |
| `references/sek1.md` | Jg. 5-10: Kompetenzerwartungen per stage, Leitideen and Inhaltsfelder per double year, rules, typical mistakes |
| `references/oberstufe.md` | E-Phase and Q1-Q4: K and L codes, Themenfelder with GK/LK split, WTR/CAS, operator documentation, exam notation, Landesabitur structure |
| `references/konventionen.md` | always: notation, formulas in HTML, number choice, solution layout, `data-check`, second ways, figures, print notes |
| `references/animationen.md` | an animation is planned: what to animate, maths rules, recipes for the base engine |
| `references/begriffe.md` | glossary and English lines: `DE | EN` per level, false friends, fixed phrases |
| `references/examples/brueche-addieren/` | worked example (Jg. 6): how plan, worksheet, solution with `data-check` and animation fit together |
| `references/examples/lineare-funktionen-jg08/` | worked example (Jg. 8): `erklaerung.html` with checked example and practice tasks; Klassenarbeit and Erwartungshorizont with `data-teilpunkte` and a 1-6 grade key |
| `references/sources.md` | where each fact comes from; what is not verified |

Script: `scripts/check_rechnung.py <file-or-folder>` (searches subfolders) - evaluates every `data-check` in `loesung*`, `erwartungshorizont*` and `erklaerung*` (exact fractions, school rounding, term values, derivative, integral, zeros, binomial and normal distribution, vectors); adds up `data-teilpunkte`; recomputes AFB shares and grade-key thresholds; compares points and AFB of test and Erwartungshorizont; exit code 1 on a false or broken check; `?` for a missing check. A green run shows that the material agrees with itself, not that an answer is right.
