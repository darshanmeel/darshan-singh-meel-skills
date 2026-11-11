---
name: darshan-singh-meel-einstellungstest
description: Practice for the online Einstellungstests employers in Germany use before an Ausbildung - original chapters and 4-option questions with worked solutions as JSON with an English sidecar, practice sheets with solutions and timed mock tests with answer sheet and scoring (Mathe, Logik, Deutsch, Englisch, Allgemeinwissen, IT, Konzentration, Merkfähigkeit, Postkorb, Branchenwissen; unscored Persönlichkeit and SJT). For a named target (an employer such as Deutsche Bahn, an Ausbildung or a sector) it searches public pages for the test's structure, areas, timing and provider, names every page, reuses fitting items and writes only the missing ones. Use with darshan-singh-meel-schule. Triggers - "Einstellungstest", "Eignungstest", "Auswahltest", "Online-Assessment", "Testfragen schreiben", "Probetest", "Zahlenreihen üben", "Einstellungstest Deutsche Bahn", "Einstellungstest Bankkaufmann",; "aptitude test practice for an apprenticeship", "online assessment practice questions", "mock aptitude test".
---

# Einstellungstest: practice material
Scope: original practice material for online tests employers use before an Ausbildung (not duales Studium, not university admission). Load `darshan-singh-meel-schule` first (language rule, HTML templates, privacy, `check_material.py`); not repeated here. This skill adds areas · item building · JSON format · mock tests · target research. Base parts that do not apply: KC citation · operators · grade keys · three-level differentiation · setup Q 1, 2, 5, 6. `→` then · `·` list · rec recommended.

## Jobs
| Request | Job | Read |
|---|---|---|
| chapters · questions · practice set | A Practice set | `bereiche.md` · `aufgabenbau.md` · `formate.md`; Persönlichkeit/SJT: `persoenlichkeit-sjt.md` |
| mock test / Probetest | B Mock test | as A + `formate.md` (mock test) |
| test for <Ausbildung / sector / employer> | C Target | `ziel.md` → A and B |

## Rules
- Original items only: never copy, translate, renumber an item from provider · employer · book · training site · pages read for areas and formats, never items · every sheet footer "Übungsmaterial … keine Originalaufgaben".
- Generic material: no invitation · TAN · PIN · login · token link · applicant or recruiter name · test date · person's result in any file or reply · user pastes such → use only target (occupation · sector · employer), say rest left out.
- Test facts only from pages read in job C (named in output) or verified table in `ziel.md` · unsure → `check: <page>` · never state pass mark, provider scoring, item count as fact.
- Item: one question · exactly 4 options · exactly one correct (`answer` 0-3) · solvable in `time_seconds` · no calculator unless item allows · difficulty 1-3 mixed in every file · correct index spread evenly 0-3.
- Distractor = result of one nameable mistake (`bereiche.md`, `aufgabenbau.md`) · no filler.
- Explanation, three parts in order: way to the answer · `Typischer Fehler:` why most tempting wrong option is wrong · `Trick:` fastest way under time pressure.
- Recomputed: item with number or series carries `check` expression → `check_items.py` proves exactly the keyed option equals it · item without `check` (language, knowledge) → solved again cold, facts against a named source.
- Persönlichkeit, SJT: no key (`answer` -1) · explanation says what each reaction shows and what employers look for, never which to tick (`persoenlichkeit-sjt.md`).
- Language: simple correct German, "du", sentences ≤ ~15 words, terms explained on first use · English: sidecar in JSON, line pairs on sheets (base `bilingual.md`) · German texts under test and English items stay in their language; only instruction and explanation translated.
- Chapters teach why: concept (why asked, idea) · example · step-by-step `example_explained` · 4-6 tips · 2-4 traps as "X ist Y, nicht Z.".

## Process A: practice set (fixed)
1. Setup: one AskUserQuestion, rec first, skip what request says:
   - Bereich und Thema: from request, or 3 topics of the area from `bereiche.md`
   - Umfang: 1 Kapitel + 8 Fragen + Übungsblatt (rec) · nur Fragen (10 / 20) · Probetest mit Lösungsbogen
   - Ziel: allgemein (rec) · eine Ausbildung, Branche oder Firma (job C)
   - Sprache: base Q4 (German with English line rec)
2. Inventory: topics, ids, stems already in `unterricht/einstellungstest/` by script, not by reading → reuse what fits, never duplicate.
3. Plan, row per item: id · topic · difficulty · idea in one line · result · mistake behind each of 3 distractors · answer index · seconds · `check` → indices fixed here (balance rule `aufgabenbau.md`).
4. Write JSON from `references/templates/`: chapter, then questions · German text → its English sidecar text, item by item.
5. Check: `python <this skill dir>/scripts/check_items.py <folder>` → fix every FAIL, read every `?`.
6. Sheets: `arbeitsblatt.html` + `loesung.html` from base templates + `references/templates/bloecke.html` · options in JSON order · `data-frage` = id (`formate.md`).
7. Check again: `check_items.py <folder>` + `python <base skill dir>/scripts/check_material.py <folder>`.
8. Self-check every item cold from printed text: solve by a second way · make each wrong option right by another reading? · level and wording fit a 16-year-old · German and English say the same → failing item rewritten, re-checked.
9. Hand over: files (relative paths) · counts per topic and difficulty · key balance · check output · every `check:` that applies → offer "Soll `darshan-singh-meel-einstellungstest-review` das Material prüfen?" · run only on yes.

## Process B: mock test
Sections and weights from target's `profil.json` (job C) or general mix in `bereiche.md` → items reused or written by process A → `test.html` + `erwartungshorizont.html` with answer sheet, key, scoring per area (`formate.md`) → steps 5, 7, 8, 9 of A.

## Process C: target (details `references/ziel.md`)
Only when user names a target: web search for its test (employer's and provider's own pages first · other public prep pages for structure only) → `profil.json`: areas · formats · weights · every page used · every `check:` → reuse fitting items → write only the missing (A) → practice sets per missing area + one mock test (B).
- Large orders (several areas): one writer per area in parallel on Sonnet, each with this skill → review skill afterwards on Opus.

## References (load only what the job needs)
| File | Read when |
|---|---|
| `references/bereiche.md` | always: areas · topics · item families · seconds per item · typical mistakes · what can carry `check` · general mix |
| `references/aufgabenbau.md` | writing or judging chapters and items: anatomy · difficulty · distractors · key balance · explanation · `check` |
| `references/formate.md` | writing files: folder · JSON schema · sidecar · sheets · mock test · `profil.json` |
| `references/ziel.md` | job C: search · trust order · what to take · sample questions · verified provider facts · reuse |
| `references/persoenlichkeit-sjt.md` | Persönlichkeit, SJT items: form · explanation · honesty |
| `references/templates/` | `kapitel.json` · `fragen.json` · `profil.json` · `bloecke.html` (blocks added to base templates) |
| `references/examples/mathe-prozent/` | one worked set: 1 chapter · 8 questions with `check` · English sidecars · practice sheet · solution |
| `references/sources.md` | where each fact comes from · what is not verified |

Script `scripts/check_items.py <folder>`: schema · 4 distinct options · key in range · ids unique across files, one prefix per file · topic = chapter topic of same folder · English sidecar complete · key balance · duplicates · e-mail/link/machine path · `check` recomputed against all four options · sheets against JSON (ids, option texts and order, key letters; no key on task files).
