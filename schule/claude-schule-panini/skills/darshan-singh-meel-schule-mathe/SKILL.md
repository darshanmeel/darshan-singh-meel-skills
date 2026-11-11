---
name: darshan-singh-meel-schule-mathe
description: Mathematics teaching material for Hessen - Grundschule (Jg. 1-4) and Gymnasium (Sek I Jg. 5-10, Oberstufe E-Phase and Q1-Q4, GK and LK, KCGO, Landesabitur rules incl. WTR/CAS) - lesson plans, worksheets with solutions, Klassenarbeiten and Klausuren with Erwartungshorizont, explanations, step animations, in German with an English line under every line. Every task is solved twice; answers and points are recomputed by a check script. Use with darshan-singh-meel-schule whenever maths material is created or changed. Not for Känguru preparation (darshan-singh-meel-kaenguru). Triggers - "Mathematik", "Mathe Arbeitsblatt", "Mathearbeit", "Klassenarbeit Mathe", "Mathe Klausur", "Rechenaufgaben", "Sachaufgaben", "Bruchrechnung", "Gleichungen", "Geometrie", "Funktionen", "Analysis", "Integralrechnung", "Stochastik", "Landesabitur Mathe", "Mathe zweisprachig"; "maths lesson", "math worksheet", "maths test with marking scheme", "word problems", "fractions animation", "bilingual maths".
---

# Mathematik (Hessen: Grundschule + Gymnasium)
Load `darshan-singh-meel-schule` first: owns formats, templates, folder, language rule, grading, operators, process, review rubric. This skill adds maths only.

## Scope
- Grundschule Jg. 1-4 (KC Primarstufe: 6 Kompetenzbereiche, 5 Inhaltsfelder) → `references/grundschule.md`
- Sek I Gymnasium Jg. 5-10 (6 Kompetenzbereiche, 5 Leitideen, 11 Inhaltsfelder, stages 6/8/9-10) → `references/sek1.md`
- Oberstufe E, Q1-Q4, GK/LK (KCGO 2024: K1-K6, L1-L5, Themenfelder E.1-Q4.3; Landesabitur, WTR/CAS) → `references/oberstufe.md`
- Out: `unterricht/mathematik/<stufe>/<thema>/`, `<stufe>` = `jg03` · `jg06` · `e` · `q1-gk` · `q3-lk`.

## Rules
- Curriculum: cite per level reference (Kompetenzbereich + Kompetenzerwartung + stage + Inhaltsfeld; Oberstufe: Kurshalbjahr.Themenfeld + GK/LK + code). KC fixes stages, not years → year from school curriculum or reference placement, say so. LK content never in GK material.
- Every task solved twice, every answer checked: second way confirms; each solution element with `data-aufgabe` has `data-check` recomputing the answer, ≥1 expression puts the answer back into the given data; `scripts/check_rechnung.py` passes. Task not clean → rewrite the task, not the solution.
- Numbers fit level and goal: inside the year's Zahlenraum · by-hand results clean · calculator tasks state rounding · realistic sizes with units · build backwards from the result → `konventionen.md`.
- Notation: German in German lines and formulas (`,` · `·` · `:` · `P(2|3)` · `[a; b]`); English sentence → decimal point, also in formulas inside it, nothing else changes; formula-only line once, German notation. Formulas MathML/plain HTML, never images or script libs.
- Solutions teach: result first → every written step → Probe/plausibility → Antwortsatz (context tasks) → one typical mistake. Erwartungshorizont: `Schritt: n P` + `data-teilpunkte`, Folgefehler, rounding tolerance.
- Aids named on every test: `ohne Hilfsmittel` · `Taschenrechner (WTR)` · `CAS` · `Formelsammlung`. Oberstufe: `berechnen` = by hand, documented · `bestimmen/ermitteln` = calculator functions allowed, documented; print the rule on the Klausur. GTR → `check:` in `oberstufe.md`.
- Understanding before rule: picture/action first (Grundschule: handelnd → bildlich → symbolisch); ≥1 task per worksheet asks a reason, error analysis or reversed question.
- Figures: SVG coordinates computed, scale stated, sketches `nicht maßstäblich`.
- Animation when dividing · moving · constructing · changing parameter · limit process is the idea (fractions, written algorithms, constructions, graphs, Ober-/Untersummen); exact geometry, worksheet numbers → `animationen.md`.
- Terms `DE | EN` from `begriffe.md`; false-friends table binding (`kürzen` = simplify · `Stelle` = x-value · `Körper` = solid).
- School decisions asked, not guessed: subtraction method, division notation (Grundschule) · calculator introduction year · hilfsmittelfreier Teil · WTR/CAS · grade key.

## Process
1. Setup → base questions (subject answered) + in the same prompt (≤4, else second prompt):
   - Hilfsmittel (test output, Sek I from Jg. 7 / Oberstufe): ohne Hilfsmittel (rec to Jg. 6) · WTR · CAS · hilfsmittelfreier Teil + Teil mit Hilfsmitteln
   - Oberstufe: Kurs: GK (rec) · LK · E-Phase
   - Grundschule, written subtraction/division: Verfahren: wie im Lehrwerk, nennen (rec) · Abziehverfahren mit Entbündeln · Ergänzungsverfahren
   - Schwerpunkt: Üben mit steigender Schwierigkeit (rec) · Sachaufgaben/Modellieren · Begründen/Problemlösen · Wiederholung vor der Arbeit
   - Jahrgang of topic: ask only if no year given.
2. Read level reference · `konventionen.md` always · `animationen.md` if animation · `begriffe.md` for glossary/English.
3. Plan → base 5 lines + 4 maths lines: tasks with data and results (backwards) · second way per result · representation carrying the idea · aids and rounding. All numbers fixed here; files only copy.
4. Create from base template, pair by pair (DE line, EN line); formulas once; `data-check` while writing.
5. Self-check each task:
   - re-solve from task text alone by the second way → results agree
   - `python <this skill dir>/scripts/check_rechnung.py <folder>` → all `OK`, no `?` (`data-check="-"` only for non-numeric answers); also sums `data-teilpunkte`, recomputes AFB shares, grade key
   - solvable with info box, stated aids, planned taught content · one reading · full solution set for "find all"
   - numbers in level range · units on every line · rounding as stated · German comma, English point
   - same values in Arbeitsblatt, Lösung, Test, Erwartungshorizont, Erklärung, figure labels, animation captions
   - operator and AFB fit the demand · points awardable per step
   - Fail → rewrite, recheck. Keep table (task · result · second way · check) for the reply.
6. Layout → `python <base skill dir>/scripts/check_material.py <folder>` (every FAIL fixed, every `?` read) → print preview once per file: formulas readable and unbroken · figures to scale/labelled · answer squares fit the model solution · no task split · sum row + grade key intact (`konventionen.md`).
7. Hand over → files (relative) · KC reference · self-check table · assumed school decisions · applicable `check:` lines · offer "Soll `darshan-singh-meel-schule-mathe-review` das Material prüfen?" → run only on yes.

## References (load only what the task needs)
- `references/grundschule.md` · Jg. 1-4: Kompetenzbereiche, Bildungsstandards, Inhaltsfelder, placement, rules, typical mistakes
- `references/sek1.md` · Jg. 5-10: Kompetenzerwartungen per stage, Leitideen, Inhaltsfelder, rules, mistakes
- `references/oberstufe.md` · E-Q4: K/L codes, Themenfelder GK/LK, WTR/CAS, operator documentation, exam notation, Landesabitur structure
- `references/konventionen.md` · always: notation, HTML formulas, number choice, solution layout, `data-check`, second ways, figures, print
- `references/animationen.md` · animation planned: what to animate, rules, recipes
- `references/begriffe.md` · glossary, false friends, fixed phrases
- `references/examples/brueche-addieren/` · Jg. 6 worked example: plan, worksheet, checked solution, animation
- `references/examples/lineare-funktionen-jg08/` · Jg. 8: Erklärung, Klassenarbeit, Erwartungshorizont with `data-teilpunkte`, 1-6 key
- `references/sources.md` · fact sources, unverified items

## Script
- `scripts/check_rechnung.py <file-or-folder>` → evaluates `data-check` in `loesung*` · `erwartungshorizont*` · `erklaerung*` (fractions, school rounding, terms, derivative, integral, zeros, binomial/normal, vectors); sums `data-teilpunkte`; recomputes AFB, grade key; compares test vs Erwartungshorizont; exit 1 on false/broken; `?` = check missing.
- Green = material agrees with itself, not that an answer is right.
