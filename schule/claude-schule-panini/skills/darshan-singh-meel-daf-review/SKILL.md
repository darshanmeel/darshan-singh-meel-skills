---
name: darshan-singh-meel-daf-review
description: Reviews DaF/DaZ teaching material A1-C1 (allgemein and Beruf) - lesson plans, worksheets and solutions, tests and marking schemes, explanations, vocabulary lists, rubrics, animations - for correct German, level fit (GER/CEFR), answerable and unambiguous tasks, exam-format fidelity (Goethe, telc, DTB), scoring, and the German-plus-closest-English-line rule. Solves every task independently and writes a report with verdict and Must / Should / Other findings to reviews/. Use after darshan-singh-meel-daf, or on any German-course material. Loads darshan-singh-meel-schule and darshan-singh-meel-daf. Triggers - "DaF-Material prüfen", "Arbeitsblatt Deutschkurs prüfen", "Test A2 prüfen", "Niveau prüfen", "ist das B1?", "Prüfungstraining prüfen", "Lösung kontrollieren"; "review my German worksheet", "check the level", "check this German test", "review DaF material", "is this exam practice correct".
---

# DaF/DaZ review
Reviews, never rewrites; fixes only on request → re-run checks. CLAUDE.md applies (report in `reviews/` git-ignored · relative paths · no learner data).

## Loads
- `darshan-singh-meel-schule` → `references/review.md` (process, 12 areas, severity, report format, verdict) · `bilingual.md` · `formate.md` · `scripts/check_material.py`.
- `darshan-singh-meel-daf` → `niveaus.md` · `grammatik.md` · `aufgaben.md`; tests → `pruefungen.md` + `bewertung.md`; Beruf → `beruf.md`; lists → `wortschatz.md`.
- This skill → `references/checks.md`: DaF checks D1-D12, mapping to base areas, print view.

## Rules
- Independent reviewer: fresh agent/session that did not write the material; else say so under "Not checked".
- Solve every task from the learner's side, sheet only, before opening the key. Listening → read Hörtext once, then answer.
- Check every German form (tasks, texts, keys, glossary, Tafelbild): article · plural · verb · case · word order · commas · spelling. Wrong form in learner-facing German = Must.
- Level measured, not felt: list each structure above level (`grammatik.md` "not yet") and each text outside range (`niveaus.md`) with the proving line.
- Exam practice vs `pruefungen.md` line by line: diff from a `read` fact = Must; from a `check:` fact = Should ("verify with <page>").
- Evidence per finding: file · task id · quoted line. No praise, no restating.
- Base "Must when" naming Hessen KC → read as GER reference (level, activity, Kann-Beschreibung, Handlungsfeld).

## Process
1. Scope: folder (default every `.html` in `unterricht/daf/<stufe>/<thema>/`) · level · track · adults/teens · exam if any. Ask only what files do not show (one AskUserQuestion).
2. Script: `python <base skill dir>/scripts/check_material.py <folder>` → every `FAIL` = Must (compares printed points with `data-*`; points in running text → hand-check in step 7). Every `?` line: target language → needs `data-nur-de`; else English line missing.
3. Solve: answer all tasks without key, note time → compare with `loesung.html` / `erwartungshorizont.html`. Note items with 2 answers, none, or key mismatch.
4. Language: read each German sentence as native teacher; forms table in `grammatik.md`.
5. Level: structures · vocabulary · text/sentence length · instruction language; English amount vs `niveaus.md`.
6. Pairs: each DE/EN pair → 3-step test (base `bilingual.md`); no English for target-language text.
7. Scoring: points per item · sums · conversion · Prädikate · pass mark · rubric scaling; exam format if exam practice.
8. Checklist: base areas 1-12 + `checks.md` D1-D12 → print view of every file (`checks.md` "Print view").
9. Report: `reviews/darshan-singh-meel-daf-review-<YYYY-MM-DD-HHMM>.md` in base format (verdict · counts · Must/Should/Other as `what · why · fix` · checked without findings · not checked). First use → add `/reviews/` to `.gitignore`. Reply: verdict · counts · report path.

## Verdict
Base table (`review.md`). DaF adds Must (area 2 or 6): wrong German form in learner-facing text · graded-test task with no or two correct answers · structure above level in graded item · text > 1 level off.
