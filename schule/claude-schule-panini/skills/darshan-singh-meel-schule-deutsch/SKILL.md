---
name: darshan-singh-meel-schule-deutsch
description: Deutsch as a school subject in Hessen - Grundschule Jg. 1-4 (Lesen, Schreiben, Rechtschreibung, Sprache untersuchen) and Gymnasium Sek I and Oberstufe (Literatur, Sachtexte, Erörterung, Interpretation, Sprachreflexion, Landesabitur). Creates lesson plans, worksheets with solutions, Klassenarbeiten and Klausuren with Erwartungshorizont, explanations and animations. Use for any Deutsch teaching material named by school year or course (Jg., E, Q1-Q4, GK/LK), DaZ support in a school class included; load together with darshan-singh-meel-schule. Not for German as a foreign or second language by CEFR level A1-C1 (darshan-singh-meel-daf). Triggers - "Deutschunterricht", "Arbeitsblatt Deutsch", "Diktat", "Rechtschreibung", "Wortarten", "Satzglieder", "Aufsatz", "Erörterung", "Gedichtinterpretation", "Sachtextanalyse", "Lektüre", "Klausur Deutsch", "Landesabitur Deutsch"; "German lesson" (school subject), "spelling worksheet", "grammar worksheet", "essay task with marking scheme", "poem analysis".
---

# Deutsch (Hessen) · Grundschule · Gymnasium
Load `darshan-singh-meel-schule` first (formats, templates, folders, grading, rubric, `check_material.py`) → this file wins for Deutsch.

## Language
- German = content + target · English = help line only, never a second version.
- Help line yes: instruction · task wording · hint · info box · rule · Merksatz · Lösungsweg · typical mistake · Erwartungshorizont criteria · lesson plan.
- `data-nur-de`: analysed text · dictation · reading text · example sentence · word list · gap text · grammar table · language-task result · model answer · sentence starters · Wortspeicher.
- Glossary `DE | EN | Bedeutung` · grammar + literary terms only, never text vocabulary.
- Default `data-sprache="de-en"`; `de` (+ glossary) when no reader needs English → one setup question.
- Jg. 1-2 ≤ 1 short English line per instruction · Oberstufe: English on instructions + glossary, EH criteria short.
- DaZ = German support first: Wortspeicher (article + plural) · starters · pictures (base `differenzierung.md`).

## Rules
- Texts: public domain (death year > 70 stated) · own · written for task. Source line: author, title, year, `gemeinfrei` | `für diese Aufgabe verfasst`. Verse/line numbers on every quoted text. No protected authors, textbooks, past Abitur/VERA → cite chapter + page of class edition. → `texte.md`
- Every answer proven: grammar/spelling → named Probe (Umstell · Ersatz · Verlängern · Ableiten) · text work → line/verse reference · two defensible analyses → replace sentence.
- Writing task EH = Inhalt (points) + Darstellung (holistic levels). Oberstufe: Verstehen : Darstellung = 70 : 30 + Fehlerindex. Sek I/GS: school decision, default in `schreibaufgaben.md`.
- One term set (Nomen · Verb · Adjektiv · Artikel · Pronomen · Satzglied · Subjekt · Prädikat · Objekt) · ask Nomen/Substantiv, Zeitform/Tempus once · never mix in a file.
- Spelling: Amtliches Regelwerk, one variant throughout · GS rules → `grundschule.md` (Grundwortschatz · corrected spelling from Jg. 1 second half · SAS | VA).
- Operators: Oberstufe + Jg. 7-10 → base `operatoren.md` Deutsch block (`interpretieren` · `erörtern` · `begründen` = AFB III) · GS + Jg. 5-6 add own (not official) verbs: Lies · Schreibe ab/auf · Unterstreiche · Markiere · Kreise ein · Trenne · Setze ein · Ergänze · Stelle um · Verbinde · Erzähle · Überarbeite.
- Task > ~15 lines → "on the class's paper", no `.zeile` block.
- Animation only for movement/build-up: Umstellprobe · syllables/word building · letter formation · drama tension curve · argument (These → Argument → Beleg → Beispiel). Else figure.

## Setup (base table, Deutsch options)
- 1 Jahrgang/Kurs: GS Jg. 1-4 · Gym Jg. 5-10 · E · Q1-Q4 + GK|LK + exam year.
- 2 Thema: 3 proposals from Inhalts-/Themenfeld, or user's Lektüre + edition.
- 4 Sprache: de-en (rec) · nur Deutsch + Glossar.
- Test: Diktat/Rechtschreibung · Grammatik · Aufsatz (form) · Lesen/Textarbeit · Oberstufe: Aufgabenart + exam year.
- Only if it changes the material: Nomen|Substantiv · Lineatur + script (Jg. 1-2) · Lektüre edition.

## Process
1. Setup → base step 1.
2. Read level file → then only what outputs need.
3. Plan in 5 lines: KC ref · Stundenziel · text/language material + source · tasks (operator, AFB, points) · animation y/n + why.
4. Create from base templates · German first (`data-nur-de`) → task lines + help line, pair by pair.
5. Self-check before layout:
   - solve each task without solution → compare · grammar via named Probe
   - count: dictation words · syllables · verses · stressed syllables · rhyme letters · Satzglieder
   - quotes vs printed text with line numbers · public-domain text vs user-pasted/confirmed wording (`texte.md`) → none = "not ready: Wortlaut"
   - writing task: 5-line full-marks outline · every Inhalt criterion reachable from text + lessons · points add up
   - spelling pass on all German · English pass via base `bilingual.md` 3-step test
   - `data-nur-de` on German-only blocks · no help line gives an answer away
6. Layout: `python <base skill dir>/scripts/check_material.py <folder>` → fix every `FAIL`, read every `?` · A4 print preview: count pages, no task split from material/answer lines.
7. Hand over: files (relative) · KC ref · pages per file · `check:` items (always Anlage 9a rows, school grade key) · "not ready: Wortlaut" per typed-from-memory text · offer `darshan-singh-meel-schule-deutsch-review` (rec before graded work).

## References (`references/`)
| File | Read when |
|---|---|
| `grundschule.md` | Jg. 1-4: KC Primarstufe · spelling/handwriting · formats |
| `sek1.md` | Jg. 5-10: KC · emphases per double year · Klassenarbeit forms |
| `oberstufe.md` | E, Q1-Q4: KCGO codes · Themenfelder · Landesabitur 2027/2028 |
| `schreibaufgaben.md` | writing task: forms · criteria · EH · 70 : 30 · Fehlerindex |
| `texte.md` | choose, mark up, analyse texts · Stilmittel · quoting |
| `sprache.md` | Grammatik · Rechtschreibung · Proben · typical mistakes · DE \| EN terms |
| `sources.md` | origin of each fact · unverified |
| `examples/` | finished pattern: `jg03-umstellprobe/` · `q1-gk-mondnacht/` |
