---
name: darshan-singh-meel-schule-deutsch
description: Deutsch as a school subject in Hessen - Grundschule Jg. 1-4 (Lesen, Schreiben, Rechtschreibung, Sprache untersuchen) and Gymnasium Sek I and Oberstufe (Literatur, Sachtexte, Erörterung, Interpretation, Sprachreflexion, Landesabitur). Creates lesson plans, worksheets with solutions, Klassenarbeiten and Klausuren with Erwartungshorizont, explanations and animations. Use for any Deutsch teaching material named by school year or course (Jg., E, Q1-Q4, GK/LK), DaZ support in a school class included; load together with darshan-singh-meel-schule. Not for German as a foreign or second language by CEFR level A1-C1 (darshan-singh-meel-daf). Triggers - "Deutschunterricht", "Arbeitsblatt Deutsch", "Diktat", "Rechtschreibung", "Wortarten", "Satzglieder", "Aufsatz", "Erörterung", "Gedichtinterpretation", "Sachtextanalyse", "Lektüre", "Klausur Deutsch", "Landesabitur Deutsch"; "German lesson" (school subject), "spelling worksheet", "grammar worksheet", "essay task with marking scheme", "poem analysis".
---

# Deutsch (Hessen): Grundschule and Gymnasium

Load `darshan-singh-meel-schule` first: it owns formats, templates, folders, grading rules, the review rubric and `check_material.py`. This skill adds the Deutsch content and the rules below. Where both speak, this file wins for Deutsch.

## Rules
- **German is content and target.** English is a help line, not a second version.

  | Element | English help line |
  |---|---|
  | Instruction, task wording, hint, info box, rule explanation, Merksatz | yes |
  | Lösungsweg, typical mistake, Erwartungshorizont criteria, lesson plan | yes |
  | Text under analysis, dictation, reading text, example sentence, word list, gap text, grammar table | no - `data-nur-de` |
  | Result of a language task, model answer, sentence starters, Wortspeicher | no - `data-nur-de` |
  | Glossary | `DE | EN | Bedeutung`; grammar and literary terms only, never the vocabulary of the text |

  - Default `data-sprache="de-en"` with the table above. `de` (German only plus the DE | EN glossary) when no reader needs the help line - one setup question.
  - Jg. 1-2: at most one short English line per instruction. Oberstufe: English on instructions and glossary; Erwartungshorizont criteria in short phrases.
  - DaZ support is German support first: Wortspeicher with article and plural, sentence starters, pictures (base `differenzierung.md`). The English line helps only learners who read English.
- **Texts.** Public domain (author dead more than 70 years - state the death year), the user's own, or written for the task. Source line under every text: author, title, year, `gemeinfrei` or `für diese Aufgabe verfasst`. Verse or line numbers on every text a task quotes. No excerpts from protected authors, textbooks, past Abitur papers or Vergleichsarbeiten: refer to chapter and page of the class edition instead. Details: `references/texte.md`.
- **Every answer proven.** Grammar and spelling: name the test that proves it (Umstellprobe, Ersatzprobe, Verlängern, Ableiten). Text work: every expected statement carries a line or verse reference. A sentence with two defensible analyses is replaced, not footnoted.
- **Writing tasks.** The Erwartungshorizont has two parts: Inhalt (what must be said, with points) and Darstellung (structure, text type, expression, handling of quotations - holistic levels). Oberstufe: Verstehensleistung : Darstellungsleistung = 70 : 30 plus the Fehlerindex deduction. Sek I and Grundschule: school decision; working default in `references/schreibaufgaben.md`.
- **One term set.** KC terms: Nomen, Verb, Adjektiv, Artikel, Pronomen, Satzglied, Subjekt, Prädikat, Objekt. Ask once whether the school says Nomen or Substantiv, Zeitform or Tempus; never mix inside one file.
- **Spelling norm.** Amtliches Regelwerk; where it allows variants, one variant throughout. Grundschule: Hessen rules in `references/grundschule.md` (Grundwortschatz, corrected spelling from the second half of Jg. 1, joined handwriting SAS or VA).
- **Operators.** Oberstufe and Jg. 7-10: Deutsch block of base `operatoren.md` (`interpretieren`, `erörtern`, `begründen` are AFB III there). Grundschule and Jg. 5-6 add Deutsch work verbs (own list, not official): `Lies` · `Schreibe ab / auf` · `Unterstreiche` · `Markiere` · `Kreise ein` · `Trenne` · `Setze ein` · `Ergänze` · `Stelle um` · `Verbinde` · `Erzähle` · `Überarbeite`.
- **Long texts go on the class's paper** (Heft, Klausurbogen): a task expecting more than about 15 lines says so and carries no `.zeile` block.
- **Animation** only for movement or build-up: Umstellprobe (sentence parts move), syllables and word building, letter formation, tension curve of a drama, an argument growing (These → Argument → Beleg → Beispiel). A figure covers everything else.

## Setup (base question table, Deutsch options)
| # | Deutsch options |
|---|---|
| 1 Jahrgang/Kurs | Grundschule Jg. 1-4 · Gymnasium Jg. 5-10 · E · Q1-Q4 with GK or LK and the exam year |
| 2 Thema | 3 proposals from the Inhaltsfeld / Themenfeld of that level, or the user's Lektüre with edition |
| 4 Sprache | Deutsch mit englischer Hilfszeile an Anweisungen und Erklärungen (Recommended) · nur Deutsch + Glossar DE \| EN |
| Test | Klassenarbeit: Diktat/Rechtschreibung · Grammatik · Aufsatz (which form) · Lesen/Textarbeit. Oberstufe: Aufgabenart and exam year |

Ask also, only when it changes the material: Nomen or Substantiv · Lineatur and script in Jg. 1-2 · edition of the Lektüre.

## Process (fixed)
1. **Setup** - base step 1 with the options above.
2. **Read** the level file, then only what the outputs need (table below).
3. **Plan in 5 lines** - KC reference (Kompetenzbereich, standard, Inhaltsfeld or Themenfeld) · Stundenziel · text or language material and its source · tasks with operator, AFB, points · animation or not, and why.
4. **Create** from the base templates. Write the German material first and mark it `data-nur-de`; then the task lines with their English help line, pair by pair.
5. **Self-check every task and every answer** - before the layout:
   - solve each task without the solution, then compare; redo grammar with the named test;
   - count: words of a dictation, syllables, verses, stressed syllables, rhyme letters, Satzglieder;
   - check every quotation against the printed text, with line numbers; a printed public-domain text against the wording the user pasted or confirmed (`texte.md`) - without it the file is "not ready";
   - writing task: outline a full-marks answer in 5 lines; every Inhalt criterion reachable from text and lessons; points add up;
   - spelling pass over every German line; English pass with the 3-step test of base `bilingual.md`;
   - `data-nur-de` on every German-only block; no English line gives away an answer.
6. **Layout check** - `python <base skill dir>/scripts/check_material.py <folder>`; fix every `FAIL`, read every `?`; print preview A4: count the pages, no task split from its material or answer lines.
7. **Hand over** - reply with files (relative paths), KC reference, printed pages per file, `check:` items (always: Anlage 9a rows, school grade key), "not ready: Wortlaut" for every text typed from memory. Offer the review by `darshan-singh-meel-schule-deutsch-review` (optional; recommended before graded work).

## References
| File | Read when |
|---|---|
| `references/grundschule.md` | Jg. 1-4: KC Primarstufe, Hessen spelling and handwriting rules, formats per area |
| `references/sek1.md` | Jg. 5-10: KC Sek I Gymnasium, emphases per double year, Klassenarbeit forms |
| `references/oberstufe.md` | E, Q1-Q4: KCGO codes, Themenfelder, Landesabitur 2027 and 2028 (Pflichtlektüren, task types, times) |
| `references/schreibaufgaben.md` | any writing task: forms, criteria, Erwartungshorizont Inhalt/Darstellung, 70 : 30, Fehlerindex |
| `references/texte.md` | choosing, marking up and analysing texts; Stilmittel; quoting |
| `references/sprache.md` | Grammatik, Rechtschreibung, Proben, typical mistakes, DE \| EN terms |
| `references/sources.md` | where each fact comes from; what is not verified |
| `references/examples/` | finished output to copy the pattern from: `jg03-umstellprobe/` (Stundenentwurf, Arbeitsblatt, Lösung, Animation) · `q1-gk-mondnacht/` (Klausur with public-domain poem, Erwartungshorizont with Verstehensleistung in BE, Darstellungsleistung grid, key 15-0, 70 : 30) |
