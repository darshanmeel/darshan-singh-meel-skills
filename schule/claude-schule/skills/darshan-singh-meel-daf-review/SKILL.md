---
name: darshan-singh-meel-daf-review
description: Reviews DaF/DaZ teaching material A1-C1 (allgemein and Beruf) - lesson plans, worksheets and solutions, tests and marking schemes, explanations, vocabulary lists, rubrics, animations - for correct German, level fit (GER/CEFR), answerable and unambiguous tasks, exam-format fidelity (Goethe, telc, DTB), scoring, and the German-plus-closest-English-line rule. Solves every task independently and writes a report with verdict and Must / Should / Other findings to reviews/. Use after darshan-singh-meel-daf, or on any German-course material. Loads darshan-singh-meel-schule and darshan-singh-meel-daf. Triggers - "DaF-Material prüfen", "Arbeitsblatt Deutschkurs prüfen", "Test A2 prüfen", "Niveau prüfen", "ist das B1?", "Prüfungstraining prüfen", "Lösung kontrollieren"; "review my German worksheet", "check the level", "check this German test", "review DaF material", "is this exam practice correct".
---

# DaF/DaZ review

Reviews, does not rewrite. Fixes only when the user asks, then re-runs the checks. Global rules in CLAUDE.md apply (report in `reviews/`, git-ignored; relative paths; no learner data).

## Loads
- `darshan-singh-meel-schule`: `references/review.md` (process, 12-area checklist, severity, report format, verdict), `references/bilingual.md`, `references/formate.md`, `scripts/check_material.py`.
- `darshan-singh-meel-daf`: `references/niveaus.md`, `references/grammatik.md`, `references/aufgaben.md`; `references/pruefungen.md` and `references/bewertung.md` for tests; `references/beruf.md` for the Beruf track; `references/wortschatz.md` for lists.
- `references/checks.md` of this skill: the DaF checks D1-D12 and how they map to the base areas.

## Rules
- **Independent reviewer.** Run in a fresh agent or session that did not write the material; otherwise say so under "Not checked".
- **Independent solving.** Solve every task from the learner's side, with only the material of the sheet, before opening the key. For listening tasks read the Hörtext once, then answer.
- **Every German form is checked**, in tasks, texts, keys, glossary and Tafelbild: article, plural, verb forms, case, word order, commas, spelling. A wrong form in learner-facing German is always Must.
- **Level is measured, not felt**: list each structure above the level (`grammatik.md`, "not yet") and each text outside its length range (`niveaus.md`) with the line that shows it.
- **Exam practice** is compared with `pruefungen.md` line by line; a difference from a `read` fact is Must, from a `check:` fact Should ("verify with <page>").
- **Evidence for every finding**: file, task id, quoted line. No praise section, no restating.
- A base "Must when" that names the Hessen KC is read as the GER reference (level, activity, Kann-Beschreibung, Handlungsfeld).

## Process (fixed)
1. **Scope** - folder (default: every `.html` in `unterricht/daf/<stufe>/<thema>/`), level, track, learners (adults/teens), exam if any. Ask only what the files do not show (one AskUserQuestion).
2. **Script** - `python <base skill dir>/scripts/check_material.py <folder>`: every `FAIL` is Must (it compares printed points with the `data-*` values; points named in running text are still checked by hand in step 7); every `?` line is read: target language → must carry `data-nur-de`; otherwise the English line is missing.
3. **Solve** - answer every task without the key; note the time needed; then compare with `loesung.html` / `erwartungshorizont.html`. Note every item with two possible answers, none, or a key that does not match.
4. **Language** - read every German sentence aloud in your head as a native teacher; apply the table of forms in `grammatik.md`.
5. **Level** - structures, vocabulary, text and sentence length, instruction language against the level; English amount against `niveaus.md`.
6. **Pairs** - every DE/EN pair with the 3-step test of the base `bilingual.md`; no English for target-language text.
7. **Scoring** - points per item, sums, conversion, Prädikat table, pass mark, rubric scaling; exam format when it is exam practice.
8. **Checklist** - base areas 1-12 plus `references/checks.md` D1-D12, then the print view of every file (`references/checks.md`, "Print view").
9. **Report** - write `reviews/darshan-singh-meel-daf-review-<YYYY-MM-DD-HHMM>.md` in the base report format (verdict, counts, Must / Should / Other as `what · why · fix`, checked without findings, not checked). Add `/reviews/` to `.gitignore` on first use. Reply: verdict, counts, report path.

## Verdict
Base table (`review.md`). DaF additions: a wrong German form in learner-facing text, a task with no or two correct answers in a graded test, a structure above the level in a graded item, or a text more than one level off count as Must in area 2 or 6.
