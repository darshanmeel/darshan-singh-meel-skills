---
name: darshan-singh-meel-schule
description: Shared base for all school skills (Hessen, Grundschule, Gymnasium) - KC framework, grading, operators and AFB, bilingual rule (German line + closest English line), output folder, HTML templates (Stundenentwurf, Arbeitsblatt + Lösung, Test + Erwartungshorizont, Erklärung, Animation), setup questions, review rubric. Load with every school subject skill and school *-review skill; alone when no subject skill fits. Triggers - "Stundenentwurf", "Arbeitsblatt", "Lösung", "Klassenarbeit", "Klausur", "Lernkontrolle", "Erwartungshorizont", "Notenschlüssel", "Erklärung für Schüler", "Animation für den Unterricht", "zweisprachig"; "lesson plan", "worksheet", "answer key", "test with marking scheme", "teaching animation", "German with English translation", "review my worksheet".
---

# Schule base
Subject skills give content, KC and subject facts. This skill gives framework, formats, language rule, process, review rubric. CLAUDE.md applies.

## Rules
- KC source on every output: Kompetenzbereich + competence + Inhaltsfeld (Sek I, GS) or Kurshalbjahr + Themenfeld (Oberstufe); format `references/hessen.md`. Never invent KC wording; quote the subject reference or write `check: <KC PDF>`.
- Solve every task yourself before writing the solution; check each number, unit, date, name, formula. Unsolvable task → rewrite.
- Each task: one operator from the subject list + one AFB (I/II/III); `references/operatoren.md`.
- German line, then the closest natural English line under it: same meaning, same order, not paraphrase, not word-for-word. Terms in `DE | EN` glossary. Deutsch texts under analysis and DaF target texts stay German; `references/bilingual.md`.
- One answer space per task, after the DE+EN pair.
- Original tasks only; never copy textbooks, Abitur, Vergleichsarbeiten, competitions. Source texts: public domain, teacher's own, or written for the task; plain source line (`Quelle: eigener Text`).
- Privacy: no real student names, grades, photos, class lists. Name fields blank; example persons invented first names; reviews never quote student data.
- One self-contained HTML per output: inline CSS/SVG/JS, no CDN/external images/fonts, A4 print CSS. Use the template; never restyle.
- Rule facts (number of Klassenarbeiten, durations, grade keys) only from `references/bewertung.md`. `check:` lines are unverified → tell the user in the reply. Schulkonferenz/Fachkonferenz decisions override defaults; ask if relevant.
- Author voice (global rule): material = written by the teacher · student text addresses students · Lehrkraft notes in the teacher's voice · never the chat, the request, how it was made · open point = fact (`Notenschlüssel nach Fachkonferenzbeschluss`), not a note to the requester.
- Animation only when steps or motion explain better than a still (process, movement, construction, change over time); else labelled figure in `erklaerung.html`.

## Output
```
unterricht/<fach>/<stufe>/<thema>/
  stundenentwurf.html
  arbeitsblatt.html  loesung.html
  test.html  erwartungshorizont.html
  erklaerung.html
  animation.html  (only when needed)
```
- `<fach>`: mathematik, deutsch, nawi-technik, erdkunde, biologie, physik, geschichte, chemie, wirtschaft, psychologie, daf. Lower case, ASCII (ae oe ue ss), hyphens.
- `<stufe>`: jg01-jg10, e, q1-q4 + `-gk`/`-lk` (q2-lk); languages a1-c1, `-beruf` for job courses.
- `<thema>`: short slug (brueche-addieren). Several lessons: `stunde-01/`, `stunde-02/` below.
- Pairs together: arbeitsblatt+loesung; test+erwartungshorizont.
- Full-English copy (only on request): `.en.html`, `<html lang="en">`.
- Reply paths relative to project root. Reviews: `reviews/<skill>-<YYYY-MM-DD-HHMM>.md`; add `/reviews/` to `.gitignore` on first creation.

## Process
1. Setup: one AskUserQuestion, recommended first, skip what is already said, >4 → second prompt. No answer → recommended, say which in the reply.
   | # | Question | Options |
   |---|---|---|
   | 1 | Fach, Jahrgang/Kurs | from request; Oberstufe E, Q1-Q4, GK/LK |
   | 2 | Thema | 3 topics from the KC Inhaltsfeld/Themenfeld, or free text |
   | 3 | Outputs (multi) | Stundenentwurf+Arbeitsblatt+Lösung (rec) · Test+Erwartungshorizont · Erklärung · Animation |
   | 4 | Sprache | DE + English line under each line (rec) · DE + Fachbegriffe DE\|EN · plus full English copy |
   | 5 | Zeit | 45 min (rec) · 90 min; test: Bearbeitungszeit |
   | 6 | Differenzierung (multi) | 3 Niveaus (rec) · DaZ · LRS · Förderbedarf |
   Graded test also: Klassenarbeit, Lernkontrolle or Klausur; school grade key (default `references/bewertung.md`).
2. Read the subject skill's level reference, then only the base references the outputs need.
3. Plan in 5 lines: KC competence, Stundenziel, phases with minutes, tasks (operator, AFB, points), animation content if any.
4. Write each output from `references/templates/` per `references/formate.md`; DE line then EN line, pair by pair, never translate a finished page.
5. Check: `python <skill dir>/scripts/check_material.py unterricht/<fach>/<stufe>/<thema>/`. Fix all errors, read all warnings (`?` = German without English line). Covers: well-formed HTML, no external loads, alt/labels, leftover placeholders, DE/EN pairs, English toggle, points = total, test = Erwartungshorizont, grade key order, phase minutes = lesson length, animation controls/captions.
6. Self-review against `references/review.md` (Must items). Reply: files (relative), KC used, `check:` items.

## References (load only when needed)
| File | Read when |
|---|---|
| `references/hessen.md` | new material: levels, KC structure, citing |
| `references/bewertung.md` | tests, Klausuren, grade keys, number/length of written work |
| `references/operatoren.md` | writing/reviewing tasks; EN operator per DE one |
| `references/bilingual.md` | always: closeness of EN line, good/too-free/too-literal examples, Deutsch/DaF exceptions |
| `references/differenzierung.md` | levels, DaZ, LRS, Förderbedarf, Nachteilsausgleich |
| `references/formate.md` | any output: template contents, DE/EN markup, animation rules |
| `references/review.md` | school *-review skills; step 6 |
| `references/sources.md` | origin of each fact; unverified items |

## Subject skills and reviewers
- Subject skill adds: KC competences + Inhalts-/Themenfelder per level, subject operators, typical mistakes, conventions (units, notation, source work), `DE | EN` terms, fitting animations. It never redefines formats, folders, language rule, grading.
- Reviewer loads this + subject skill, runs `scripts/check_material.py`, applies `references/review.md`, writes `reviews/`. Reviews only; fixes only on request.
