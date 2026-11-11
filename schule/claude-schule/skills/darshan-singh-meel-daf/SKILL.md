---
name: darshan-singh-meel-daf
description: Teaching German as a foreign or second language (DaF/DaZ) A1-C1 for adults and teens, in two tracks - allgemein and Beruf (workplace German - phone calls, e-mails, meetings, applications). Lesson plans, worksheets with solutions, tests scored like the exams (Goethe-Zertifikat A1-C1, telc Deutsch incl. Beruf, Deutsch-Test für den Beruf A2-C1), student explanations of grammar with English support, vocabulary lists by level, grammar progression, speaking and writing rubrics, grammar animations. German target texts stay German; instructions and rule explanations get the closest natural English line. Use with darshan-singh-meel-schule (formats, templates, bilingual rule). Not for Deutsch as a school subject or DaZ support inside a regular Deutsch lesson (darshan-singh-meel-schule-deutsch). Triggers - "DaF", "DaZ", "Deutsch als Fremdsprache", "Deutsch als Zweitsprache", "Deutschkurs", "Integrationskurs", "Berufssprachkurs", "Deutsch für den Beruf", "Deutschkurs A1" ... "Deutschkurs C1", "A2-Kurs", "B1 Prüfungstraining", "Goethe-Zertifikat", "telc", "DTB", "Prüfungsvorbereitung", "Wortschatzliste", "Grammatik erklären", "Redemittel", "Bewertungsraster Schreiben/Sprechen"; "German as a foreign language", "German course lesson plan", "German worksheet A2", "job German", "business German", "exam practice Goethe/telc", "vocabulary list by level", "German grammar explanation in English", "speaking rubric", "writing rubric".
---

# DaF/DaZ A1-C1: allgemein and Beruf

Load `darshan-singh-meel-schule` first: it owns the folder convention, HTML templates, the German-plus-English-line rule, the check script and the review rubric. This skill supplies the language-teaching content. Global rules in CLAUDE.md apply.

## What replaces the Hessen parts of the base
| Base | DaF/DaZ |
|---|---|
| Kerncurriculum reference | GER (CEFR) level + activity + Kann-Beschreibung + Handlungsfeld: `references/niveaus.md`. Adult DaF has no Hessen KC; DaZ in Hessen schools: `check:` in `references/sources.md` |
| Operators | instruction verbs by level: `references/aufgaben.md` (Sie-form for adults, du-form for teens) |
| AFB I-III | I = recognise, reproduce · II = guided use · III = free production, interaction, mediation (own mapping; the check script needs it) |
| Grade key | points and Prädikate as in the exams, pass mark 60 %: `references/bewertung.md` |
| `<fach>` / `<stufe>` | `daf` / `a1` ... `c1`; Beruf track `a2-beruf` ... `c1-beruf` |

## Rules
- **Level first.** Every text, task and model answer stays inside the target level: grammar from `references/grammatik.md` up to that level, text length and topics from `references/niveaus.md`. One new structure per lesson; 8-12 new words per 45 min.
- **Target language stays German.** Reading and listening texts, example sentences, gap texts, grammar tables, Redemittel, model answers: German only, block marked `data-nur-de`. Never give the English of what the learner must understand or produce.
- **English is the help line.** Instructions, task wording, rule explanations, Merksätze, typical-mistake notes and teacher pages get the closest natural English sentence under the German line (base `references/bilingual.md`). Amount by level: `references/niveaus.md`. Words go into the glossary `DE | EN`: nouns with article and plural, verbs with 3rd person and Perfekt from A2.
- **Communicative goal before grammar.** The Stundenziel is a Kann-Beschreibung ("kann sich telefonisch krankmelden"); grammar and vocabulary serve it. Every lesson ends with the learners using the language in the situation.
- **Skill named on every task**: Lesen, Hören, Schreiben, Sprechen, Wortschatz, Grammatik, Mediation. Hören: the script stands in the teacher file (Lösung or Erwartungshorizont) as "Hörtext zum Vorlesen"; no audio files are produced.
- **Register stated in the task**, both tracks: every e-mail, letter, message and role-play task says du or Sie and formell, halbformell or informell; the rubric asks only for what the task states.
- **Beruf track:** situations from the Handlungsfelder in `references/beruf.md`; no single profession unless the user names one.
- **Exam practice mirrors the format, never the content.** Same parts, item types, timing and scoring as the named exam (`references/pruefungen.md`); every text and item is new. Lines marked `check:` are told to the user, not presented as fact.
- **Learners:** adults by default (Sie, adult topics); teens (du, school and leisure topics) when the user says so. Invented first names and firms only.
- **German facts are checked**: article, plural, verb forms, case after each preposition, word order, spelling, commas. Unsure about a form → rewrite the sentence.

## Process (fixed)
1. **Setup questions** - the base prompt (one AskUserQuestion, recommended first) with these replacements; skip what the user already said.

   | # | Question | Options |
   |---|---|---|
   | 1 | Niveau + Kurs | A1 · A2 · B1 · B2 · C1; allgemein (Recommended) · Beruf; Erwachsene (Recommended) · Jugendliche |
   | 2 | Thema / Sprachhandlung | 3 from `references/niveaus.md` or `references/beruf.md` for that level, or free text |
   | 3 | Outputs (multi) | Stundenentwurf + Arbeitsblatt + Lösung (Recommended) · Test + Erwartungshorizont · Erklärung · Animation · Wortschatzliste · Bewertungsraster |
   | 4 | Sprache | first and Recommended, by the level from question 1: A1-B1 englische Zeile bei Anweisungen und Erklärungen; B2-C1 Englisch nur bei Anweisungen und im Glossar · then: nur Glossar DE \| EN (the other level's option is not shown) |
   | 5 | Zeit | 45 min (Recommended) · 90 min; test: Bearbeitungszeit |
   | 6 | Test: Art | Lernkontrolle zum Thema (Recommended) · Prüfungstraining im Format Goethe · telc · DTB |
2. **Read** `references/niveaus.md` and the level's section of `references/grammatik.md`, then only what the outputs need (table below), then the base files the base process names.
3. **Plan in 6 lines**: Kann-Beschreibung, Stundenziel, new structure, new words, phases with minutes, tasks with skill + instruction verb + AFB + points.
4. **Create** from the base templates, German line then English line, pair by pair. DaF version of each output: `references/aufgaben.md`. Extra outputs: `wortschatz.html` (from the `arbeitsblatt.html` template), `bewertungsraster.html` (from `erwartungshorizont.html`).
5. **Self-check every task and answer** - solve each task without the key, then compare. Per task: exactly one correct answer, or every accepted answer listed; every German form in text, task and key correct; nothing from the "not yet" column of the level; text length inside the range; the key answers what the task asks; points add up; Hörtext present for every Hören task.
6. **Layout check** - `python <base skill dir>/scripts/check_material.py unterricht/daf/<stufe>/<thema>/`; fix every `FAIL`; each `?` line gets its English line, or `data-nur-de` when it is target language. Then the print view of each file: no figure label cut off, no box alone on a last page, Erklärung at most 2 pages (print rules: `references/aufgaben.md`).
7. **Reply**: files (relative paths), level and Kann-Beschreibung used, exam format and its date if used, every `check:` line touched. Offer a review by `darshan-singh-meel-daf-review` (optional).

## References (load only what the task needs)
| File | Read when |
|---|---|
| `references/niveaus.md` | always: what each level can do, text and sentence length, topics, how to cite the GER, how much English |
| `references/grammatik.md` | always: grammar progression A1-C1 and what is not yet available |
| `references/wortschatz.md` | vocabulary lists, glossaries, word fields per level, list format |
| `references/beruf.md` | Beruf track: Handlungsfelder, scenarios per level, e-mail, phone and meeting conventions, Redemittel |
| `references/aufgaben.md` | writing tasks: instruction verbs, task types per skill, DaF version of each output, typical learner errors, teens, animations |
| `references/pruefungen.md` | exam practice; any question about Goethe, telc or DTB formats |
| `references/bewertung.md` | tests, scoring, Prädikate, writing and speaking rubrics, error marking |
| `references/sources.md` | where each fact comes from; what is not verified |
| `references/examples/a2-beruf-krankmeldung/` | worked example, A2 Beruf, `arbeitsblatt.html` + `loesung.html`: copy its conventions (skill in each task heading, `data-nur-de` blocks, example item 0, glossary entry form, role cards in key words) |
