---
name: darshan-singh-meel-schule
description: Shared base for all school skills (Hessen, Grundschule and Gymnasium) - curriculum framework (Kerncurriculum, KCGO), grading and Klassenarbeit/Klausur rules, operators and Anforderungsbereiche, the bilingual rule (German text with the closest natural English sentence under every line), the fixed output folder and HTML templates (Stundenentwurf, Arbeitsblatt + Lösung, Test + Erwartungshorizont, Erklärung, Animation), the setup questions, and the shared review rubric. Load alongside every darshan-singh-meel school subject skill and every school *-review skill, and on its own when no subject skill fits. Triggers - "Stundenentwurf", "Unterrichtsstunde planen", "Arbeitsblatt", "Lösung", "Klassenarbeit", "Klausur", "Lernkontrolle", "Erwartungshorizont", "Notenschlüssel", "Erklärung für Schüler", "Animation für den Unterricht", "zweisprachig", "bilingual", "Deutsch und Englisch"; "lesson plan", "worksheet", "answer key", "test with marking scheme", "explain to students", "teaching animation", "German with English translation", "review my worksheet".
---

# Schule: shared base (Hessen)

Subject skills supply content (what to teach, subject facts, subject KC). This skill supplies everything they share: framework, formats, language rule, process, review rubric. Global rules in CLAUDE.md apply.

## Rules
- **Curriculum first.** Every piece of material names its KC source: Kompetenzbereich + competence + Inhaltsfeld (Sek I, Grundschule) or Kurshalbjahr + Themenfeld (Oberstufe). Citation format: `references/hessen.md`. Never invent KC wording or numbering - quote the subject skill's reference or write `check: <KC PDF>`.
- **Correct before pretty.** Solve every task yourself before writing the solution; every number, unit, date, name, formula checked. A task you cannot solve cleanly is rewritten.
- **Operators.** Every task starts with one operator from the subject's list; each task carries one AFB (I, II, III). `references/operatoren.md`.
- **German first, English directly under it.** Every German instruction, task, explanation and solution gets one English line: the closest English sentence to the German in that context - same meaning, same order of ideas, natural English; not a free paraphrase, not word-for-word nonsense. Subject terms in a `DE | EN` glossary. Texts under analysis in Deutsch and DaF target-language texts stay German; English only on the instructions. `references/bilingual.md`.
- **One answer space per task**, after the German + English pair. Never one per language.
- **Original tasks only.** Never copy tasks, texts or figures from textbooks, Abitur papers, Vergleichsarbeiten or competitions; write new ones in the same style. Source texts: public domain, the teacher's own, or written for the task - say which in a plain source line (`Quelle: eigener Text`).
- **Privacy.** No real student names, grades, photos or class lists. Name fields stay blank; example persons are invented first names; reviews never quote student data.
- **Self-contained files.** One HTML file per output, inline CSS/SVG/JS, no CDN, no external images or fonts, A4 print CSS. Start from the template; never restyle.
- **Facts about rules** (number of Klassenarbeiten, durations, grade keys) come from `references/bewertung.md`. Lines marked `check:` are not verified - tell the user in the reply, do not present them as fact. School decisions (Schulkonferenz, Fachkonferenz) override defaults; ask if they matter.
- **Author voice** (global rule "Author voice in produced files"). Material reads as written by the teacher. Student-facing text addresses the students; Lehrkraft notes (Stundenentwurf, Erwartungshorizont, Hinweise) are in the teacher's voice. No file mentions the chat, the request, or how it was made; open points are facts (`Notenschlüssel nach Fachkonferenzbeschluss`), not notes to the requester.
- **Animation only when motion or steps explain better than a still picture** (process, movement, construction, change over time). Otherwise a labelled figure in `erklaerung.html`.

## Output convention
```
unterricht/<fach>/<stufe>/<thema>/
  stundenentwurf.html
  arbeitsblatt.html      loesung.html
  test.html              erwartungshorizont.html
  erklaerung.html
  animation.html         (only when needed)
```
- `<fach>`: `mathematik`, `deutsch`, `nawi-technik`, `erdkunde`, `biologie`, `physik`, `geschichte`, `chemie`, `wirtschaft`, `psychologie`, `daf` - lower case, ASCII (`ae oe ue ss`), hyphens.
- `<stufe>`: `jg01`-`jg10`, `e`, `q1`-`q4` plus `-gk` or `-lk` (`q2-lk`); language levels `a1`-`c1`, plus `-beruf` for job-related courses.
- `<thema>`: short slug (`brueche-addieren`). Several lessons on one topic: `stunde-01/`, `stunde-02/` below it.
- Pairs always together: `arbeitsblatt` + `loesung`; `test` + `erwartungshorizont`.
- Full-English copy (only when asked): same name with `.en.html`, `<html lang="en">`.
- Paths in replies are relative to the project root. Reviews: `reviews/<skill>-<YYYY-MM-DD-HHMM>.md`; add `/reviews/` to `.gitignore` when the folder is first created.

## Process (fixed)
1. **Setup questions** - one AskUserQuestion prompt, recommended option first, skip what the user already said; more than 4 open → second prompt right after. No answer → recommended options, and say which in the reply.

   | # | Question | Options |
   |---|---|---|
   | 1 | Fach, Jahrgang/Kurs | from the request; Oberstufe: E, Q1-Q4, GK or LK |
   | 2 | Thema | 3 topics from the KC Inhaltsfeld/Themenfeld of that level, or free text |
   | 3 | Outputs (multi) | Stundenentwurf + Arbeitsblatt + Lösung (Recommended) · Test + Erwartungshorizont · Erklärung · Animation |
   | 4 | Sprache | Deutsch mit englischer Zeile unter jeder Zeile (Recommended) · Deutsch + nur Fachbegriffe DE \| EN · zusätzlich ganz englische Fassung |
   | 5 | Zeit | 45 min (Recommended) · 90 min; for a test: Bearbeitungszeit |
   | 6 | Differenzierung (multi) | 3 Niveaus Basis/Standard/Herausforderung (Recommended) · DaZ · LRS · Förderbedarf |

   A test for grading also needs: Klassenarbeit, Lernkontrolle or Klausur, and the school's grade key (default: `references/bewertung.md`).
2. **Read** the subject skill's reference for that level, then only the files below that the outputs need.
3. **Plan in 5 lines** before writing: KC competence, Stundenziel, phases with minutes, tasks with operator + AFB + points, what the animation shows (if any).
4. **Write** each output from its template (`references/templates/`), following `references/formate.md`. Write the German line, then its English line, pair by pair - never translate a finished page in one pass.
5. **Check** - run `python <skill dir>/scripts/check_material.py unterricht/<fach>/<stufe>/<thema>/` and fix every error; read every warning (`?` = German text without an English line). It checks: well-formed HTML, nothing loaded from outside, alt texts and labels, placeholders left over, DE/EN pairs complete, the English toggle, points = total, test = Erwartungshorizont, grade key order, phase minutes = lesson length, animation controls and captions.
6. **Self-review** against `references/review.md` (Must items only), then reply: files written (relative paths), KC reference used, anything marked `check:`.

## References (load only what the task needs)
| File | Read when |
|---|---|
| `references/hessen.md` | always for new material: school levels, KC structure, how to cite |
| `references/bewertung.md` | tests, Klausuren, grade keys, number and length of written work |
| `references/operatoren.md` | writing or reviewing tasks; English operator for each German one |
| `references/bilingual.md` | always: how close the English line stays, good/too-free/too-literal examples, Deutsch and DaF exceptions |
| `references/differenzierung.md` | levelled tasks, DaZ, LRS, Förderbedarf, Nachteilsausgleich |
| `references/formate.md` | writing any output: what each template must contain, markup of the DE/EN pairs, animation rules |
| `references/review.md` | every school *-review skill; step 6 above |
| `references/sources.md` | where each fact comes from; what is not verified |

## For subject skills and reviewers
- A subject skill adds: KC competences and Inhaltsfelder/Themenfelder per level, subject operators, typical mistakes, subject conventions (units, notation, source work), its `DE | EN` term list, and what animations suit the subject. It does not redefine formats, folders, the language rule or grading.
- A reviewer loads this skill plus the subject skill, runs `scripts/check_material.py`, applies `references/review.md`, and writes the report to `reviews/`. It reviews, it does not rewrite; fixes only when the user asks.
