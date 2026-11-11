---
name: darshan-singh-meel-daf
description: Teaching German as a foreign or second language (DaF/DaZ) A1-C1 for adults and teens, tracks allgemein and Beruf (phone, e-mail, meetings, applications). Lesson plans, worksheets with solutions, tests scored like the exams (Goethe-Zertifikat A1-C1, telc Deutsch incl. Beruf, Deutsch-Test für den Beruf A2-C1), grammar explanations with English support, vocabulary lists, grammar progression, speaking and writing rubrics, grammar animations. German target texts stay German; instructions and rule explanations get the closest natural English line. Use with darshan-singh-meel-schule. Not for Deutsch as school subject or DaZ inside a regular Deutsch lesson (darshan-singh-meel-schule-deutsch). Triggers - "DaF", "DaZ", "Deutsch als Fremdsprache", "Deutsch als Zweitsprache", "Deutschkurs", "Integrationskurs", "Berufssprachkurs", "Deutsch für den Beruf", "Deutschkurs A1" ... "Deutschkurs C1", "A2-Kurs", "B1 Prüfungstraining", "Goethe-Zertifikat", "telc", "DTB", "Prüfungsvorbereitung", "Wortschatzliste", "Grammatik erklären", "Redemittel", "Bewertungsraster Schreiben/Sprechen"; "German as a foreign language", "German course lesson plan", "German worksheet A2", "job German", "business German", "exam practice Goethe/telc", "vocabulary list by level", "German grammar explanation in English", "speaking rubric", "writing rubric".
---

# DaF/DaZ A1-C1: allgemein · Beruf
Language-teaching content. Load `darshan-singh-meel-schule` first (folders, HTML templates, DE+EN rule, check script, review rubric). CLAUDE.md applies.

## Replaces Hessen parts of base
- Kerncurriculum → GER level · activity · Kann-Beschreibung · Handlungsfeld (`references/niveaus.md`). No Hessen KC for adult DaF; DaZ in Hessen schools → `check:` in `references/sources.md`.
- Operators → instruction verbs by level (`references/aufgaben.md`); Sie adults, du teens.
- AFB I-III → I recognise, reproduce · II guided use · III free production, interaction, mediation (own mapping; check script needs it).
- Grade key → exam points and Prädikate, pass 60 % (`references/bewertung.md`).
- `<fach>/<stufe>` → `daf/a1`…`c1`; Beruf `a2-beruf`…`c1-beruf`.

## Rules
- Level first: text, task, answer inside target level. Grammar ≤ level (`grammatik.md`), length and topics (`niveaus.md`). 1 new structure per lesson · 8-12 new words per 45 min.
- Target language German only (texts, examples, gap texts, tables, Redemittel, model answers) → block `data-nur-de`. Never English of what learners must understand or produce.
- English = help line: instructions, task wording, rule explanations, Merksätze, error notes, teacher pages → closest natural English under the German (base `bilingual.md`). Amount by level (`niveaus.md`). Glossary `DE | EN`: nouns with article + plural, verbs with 3rd person; Perfekt from A2.
- Communicative goal first: Stundenziel = Kann-Beschreibung ("kann sich telefonisch krankmelden"); grammar and words serve it; lesson ends with learners using the language in the situation.
- Every task names its skill: Lesen · Hören · Schreiben · Sprechen · Wortschatz · Grammatik · Mediation. Hören → script as "Hörtext zum Vorlesen" in teacher file; no audio files.
- Every e-mail, letter, message, role-play task states du/Sie + formell/halbformell/informell; rubric asks only for that.
- Beruf: situations from Handlungsfelder (`beruf.md`); no single profession unless named.
- Exam practice mirrors format, never content: same parts, item types, timing, scoring (`pruefungen.md`); all texts and items new. `check:` lines → tell user, not fact.
- Learners: adults default (Sie, adult topics); teens (du, school/leisure) if said. Invented first names and firms only.
- Check every German form: article, plural, verb forms, case after preposition, word order, spelling, commas. Unsure → rewrite sentence.

## Process
1. Setup → base prompt, one AskUserQuestion, rec first; skip what user said:
   - Niveau + Kurs: A1…C1 · allgemein (rec) · Beruf · Erwachsene (rec) · Jugendliche.
   - Thema/Sprachhandlung: 3 from `niveaus.md` / `beruf.md` for the level · free text.
   - Outputs (multi): Stundenentwurf + Arbeitsblatt + Lösung (rec) · Test + Erwartungshorizont · Erklärung · Animation · Wortschatzliste · Bewertungsraster.
   - Sprache, by level: A1-B1 English line on instructions + explanations (rec); B2-C1 English only on instructions + glossary (rec) · then: nur Glossar DE | EN.
   - Zeit: 45 min (rec) · 90 min; test → Bearbeitungszeit.
   - Test: Lernkontrolle zum Thema (rec) · Prüfungstraining Goethe · telc · DTB.
2. Read `niveaus.md` + level section of `grammatik.md` → only what outputs need (table) → base files named by base process.
3. Plan in 6 lines: Kann-Beschreibung · Stundenziel · new structure · new words · phases with minutes · tasks with skill + verb + AFB + points.
4. Create from base templates, DE line → EN line, pair by pair. DaF version per output: `aufgaben.md`. Extras: `wortschatz.html` (from `arbeitsblatt.html`), `bewertungsraster.html` (from `erwartungshorizont.html`).
5. Self-check: solve each task without key → compare. One correct answer or all accepted listed · German forms right · nothing from level's "not yet" · text length in range · key answers the task · points add up · Hörtext for every Hören task.
6. Layout: `python <base skill dir>/scripts/check_material.py unterricht/daf/<stufe>/<thema>/` → fix every `FAIL`; each `?` line → English line, or `data-nur-de` if target language. Print view: no cut figure label, no box alone on last page, Erklärung ≤ 2 pages (`aufgaben.md`).
7. Reply: files (relative) · level + Kann-Beschreibung · exam format + date if used · every `check:` line touched. Offer `darshan-singh-meel-daf-review` (optional).

## References (load only when needed)
- `references/niveaus.md` → always: level abilities, text/sentence length, topics, GER citation, English amount.
- `references/grammatik.md` → always: progression A1-C1, "not yet".
- `references/wortschatz.md` → vocabulary lists, glossaries, word fields, list format.
- `references/beruf.md` → Beruf: Handlungsfelder, scenarios, e-mail/phone/meeting conventions, Redemittel.
- `references/aufgaben.md` → writing tasks: verbs, task types per skill, DaF output versions, learner errors, teens, animations.
- `references/pruefungen.md` → exam practice, Goethe/telc/DTB formats.
- `references/bewertung.md` → tests, scoring, Prädikate, rubrics, error marking.
- `references/sources.md` → fact sources, unverified items.
- `references/examples/a2-beruf-krankmeldung/` → worked example (`arbeitsblatt.html` + `loesung.html`): skill in task heading, `data-nur-de` blocks, example item 0, glossary form, role cards in key words.
