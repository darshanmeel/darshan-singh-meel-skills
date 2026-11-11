---
name: darshan-singh-meel-einstellungstest
description: Practice for the online Einstellungstests employers in Germany use before an Ausbildung - original chapters and 4-option questions with worked solutions as JSON with an English sidecar, practice sheets with solutions and timed mock tests with answer sheet and scoring (Mathe, Logik, Deutsch, Englisch, Allgemeinwissen, IT, Konzentration, Merkfähigkeit, Postkorb, Branchenwissen; unscored Persönlichkeit and SJT). For a named target (an employer such as Deutsche Bahn, an Ausbildung or a sector) it searches public pages for the test's structure, areas, timing and provider, names every page, reuses fitting items and writes only the missing ones. Use with darshan-singh-meel-schule. Triggers - "Einstellungstest", "Eignungstest", "Auswahltest", "Online-Assessment", "Testfragen schreiben", "Probetest", "Zahlenreihen üben", "Einstellungstest Deutsche Bahn", "Einstellungstest Bankkaufmann",; "aptitude test practice for an apprenticeship", "online assessment practice questions", "mock aptitude test".
---

# Einstellungstest: practice material

Writes original practice material for the online tests employers use before an Ausbildung (not duales Studium, not university admission). Load `darshan-singh-meel-schule` first: it owns the language rule, the HTML templates, privacy and `check_material.py`. This skill adds the test: areas, item building, the JSON format, mock tests, target research. Base parts that do not apply: KC citation, operators, grade keys, the three-level differentiation, base setup questions 1, 2, 5 and 6.

## Jobs
| Request | Job | Read |
|---|---|---|
| "write chapters / questions / a practice set for …" | A Practice set | `bereiche.md`, `aufgabenbau.md`, `formate.md`; Persönlichkeit/SJT: `persoenlichkeit-sjt.md` |
| "a mock test / Probetest" | B Mock test | as A, plus `formate.md` (mock test) |
| "Einstellungstest for <Ausbildung / sector / employer>" | C Target | `ziel.md`, then A and B |

## Rules
- **Original items only.** Never copy, translate or renumber an item from a provider, employer, book or training site. Pages are read for areas and formats, never for items. Every sheet carries the footer "Übungsmaterial … keine Originalaufgaben".
- **Generic material.** No invitation, TAN, PIN, login, link with a token, applicant or recruiter name, test date or result of a person in any file or reply. If the user pastes such details, use only the target (occupation, sector, employer) and say that the rest was left out.
- **Facts about tests** only from the pages read in job C (named in the output) or the verified table in `ziel.md`; anything unsure is `check: <page>`. Never state a pass mark, a provider's scoring or an item count as fact.
- **Item form.** One question, exactly 4 options, exactly one correct (`answer` 0-3), solvable in `time_seconds` without calculator unless the item says one is allowed. Difficulty 1-3 mixed in every file; the correct index spread evenly over 0-3.
- **Distractors.** Each wrong option is the result of one nameable mistake (`bereiche.md`, `aufgabenbau.md`). No filler.
- **Explanation.** Three parts in this order: the way to the answer · `Typischer Fehler:` why the most tempting wrong option is wrong · `Trick:` the fastest way under time pressure.
- **Recomputed.** Every item with a number or a series carries a `check` expression; `check_items.py` proves that exactly the keyed option equals it. Items without `check` (language, knowledge) are solved a second time cold and facts checked against a named source.
- **Persönlichkeit and SJT have no key** (`answer` -1). The explanation says what each reaction shows and what employers look for, never which to tick (`persoenlichkeit-sjt.md`).
- **Language.** Simple, correct German with "du", sentences up to about 15 words, terms explained on first use. English: sidecar in JSON, line pairs on sheets (base `bilingual.md`). German texts under test and English items stay in their language; only instruction and explanation are translated.
- **Chapters teach why.** Concept (why it is asked, the idea), example, step-by-step `example_explained`, 4-6 tips, 2-4 traps as "X ist Y, nicht Z.".

## Process A: practice set (fixed)
1. **Setup** - one AskUserQuestion prompt, recommended first, skip what the request already says:

   | Question | Options |
   |---|---|
   | Bereich und Thema | from the request, or 3 topics of the area from `bereiche.md` |
   | Umfang | 1 Kapitel + 8 Fragen + Übungsblatt (Recommended) · nur Fragen (10 / 20) · Probetest mit Lösungsbogen |
   | Ziel | allgemein (Recommended) · eine Ausbildung, Branche oder Firma (job C) |
   | Sprache | base question 4 (German with English line recommended) |
2. **Inventory** - list topics, ids and stems already in `unterricht/einstellungstest/` by script, not by reading files: reuse what fits, never duplicate.
3. **Plan** - one row per item: id · topic · difficulty · idea in one line · result · the mistake behind each of the 3 distractors · answer index · seconds · `check`. Fix the answer indices here (balance rule in `aufgabenbau.md`).
4. **Write JSON** from `references/templates/`: chapter, then questions; each German text, then its English sidecar text, item by item.
5. **Check** - `python <this skill dir>/scripts/check_items.py <folder>`; fix every FAIL, read every `?`.
6. **Sheets** - `arbeitsblatt.html` + `loesung.html` from the base templates plus `references/templates/bloecke.html`; options in JSON order, `data-frage` = id (`formate.md`).
7. **Check again** - `check_items.py <folder>` and `python <base skill dir>/scripts/check_material.py <folder>`.
8. **Self-check every item cold** from the printed text: solve it by a second way; try to make each wrong option right by another reading; level and wording fit a 16-year-old; German and English say the same. A failing item is rewritten and re-checked.
9. **Hand over** - files (relative paths), counts per topic and difficulty, key balance, check output, every `check:` that applies. Offer: "Soll `darshan-singh-meel-einstellungstest-review` das Material prüfen?" - run it only on a yes.

## Process B: mock test
Sections and weights from the target's `profil.json` (job C) or the general mix in `bereiche.md` → items reused or written by process A → `test.html` + `erwartungshorizont.html` with answer sheet, key and scoring per area (`formate.md`) → steps 5, 7, 8, 9 of process A.

## Process C: target (details in `references/ziel.md`)
Only when the user names a target: web search for its test (employer's and provider's own pages first, other public prep pages for structure only) → `profil.json` with areas, formats, weights, every page used and every `check:` → reuse fitting items → write only the missing ones (process A) → practice sets per missing area and one mock test (process B).

Large orders (several areas): one writer per area in parallel on Sonnet, each with this skill; the review skill afterwards on Opus.

## References (load only what the job needs)
| File | Read when |
|---|---|
| `references/bereiche.md` | always: areas, topics, item families, seconds per item, typical mistakes, what can carry a `check`, general mix |
| `references/aufgabenbau.md` | writing or judging chapters and items: anatomy, difficulty, distractors, key balance, explanation, `check` |
| `references/formate.md` | writing files: folder, JSON schema, sidecar, sheets, mock test, `profil.json` |
| `references/ziel.md` | job C: search, trust order, what to take, sample questions, verified provider facts, reuse |
| `references/persoenlichkeit-sjt.md` | Persönlichkeit and SJT items: form, explanation, honesty |
| `references/templates/` | `kapitel.json`, `fragen.json`, `profil.json`, `bloecke.html` (blocks added to the base templates) |
| `references/examples/mathe-prozent/` | one worked set: 1 chapter, 8 questions with `check`, English sidecars, practice sheet, solution |
| `references/sources.md` | where each fact comes from; what is not verified |

Script: `scripts/check_items.py <folder>` - schema, 4 distinct options, key in range, ids unique across files with one prefix per file, topic = a chapter topic of the same folder, English sidecar complete, key balance, duplicates, e-mail/link/machine path, `check` recomputed against all four options, sheets against JSON (ids, option texts and order, key letters; no key on task files).
