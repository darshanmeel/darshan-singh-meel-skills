---
name: darshan-singh-meel-einstellungstest-review
description: Strict review of Einstellungstest material for Ausbildung applicants - question and chapter JSON with English sidecars, practice sheets, mock tests with answer key, target profiles. Solves every item independently before opening the key; checks exactly one correct option (none for Persönlichkeit and Situational Judgement - there the explanation), answer index and explanation, distractors, difficulty and time, fidelity to the named target pages, simple German and matching English, originality against published sample questions, no personal data. Writes a report with verdict and Must / Should / Other to reviews/. Reviews only; fixes only when asked. Loads darshan-singh-meel-schule and darshan-singh-meel-einstellungstest. Triggers - "Einstellungstest-Fragen prüfen", "Testfragen gegenlesen", "Probetest prüfen", "Lösungen nachrechnen"; "review aptitude test questions", "check my mock test", "verify the answer key".
---

# Einstellungstest: review
Scope: review only · files change only when user asks for fixes. Load `darshan-singh-meel-schule` (rubric, formats, language rule) + `darshan-singh-meel-einstellungstest` (areas, item building, formats, target research). This skill adds test checks and fixes the order of work. `→` then · `·` list.

## Rules
- Independent: solve every keyed item from stem · `material` · `figure` · options alone, before reading `answer` · `explanation` · `check` · `loesung.html` · `erwartungshorizont.html` → write own index list first, then compare · hide key with a script printing items without `answer`, `explanation`, `check`.
- Own computation: item with numbers · series · finitely many cases → own short Python check in scratchpad, not a copy of item's `check` · test all four options, not only keyed.
- Every option: item passes only when key right and each other option wrong under every reasonable reading of stem.
- No key, other duty: Persönlichkeit, SJT (`answer` -1) have no option to verify → check instead: no hidden key or ranking in explanation · what each option shows is fair and plausible · honesty rule holds (`persoenlichkeit-sjt.md` of coach skill).
- Evidence: every finding names file + item id · quotes text · gives corrected text, value or index · no finding from memory of what such material usually contains.
- Test facts compared with pages named in `profil.json` `sources` and verified table in `ziel.md`, not memory · fact no named page states = finding unless marked `check:` · `check:` line presented as fact = finding.
- Originality: never paste an item into a web search · suspected copying → report with reason + ask author to confirm source.
- Privacy: report never repeats a person's data or access detail found in a file → says "personal or access detail in <file>, <key>".
- Severity as base `review.md` · test-specific Must conditions in `references/checks.md`.
- No rewrite: findings carry a concrete fix · files stay until user says "fix".

## Process (fixed)
1. Scope: files or folder (default: every `.json` + `.html` of topic folder in `unterricht/einstellungstest/`) · kind from content: practice set · mock test · target profile · ask only when unreadable from files.
2. Read base `review.md`, `bilingual.md` · coach skill `bereiche.md`, `aufgabenbau.md`, `formate.md`, by content `ziel.md`, `persoenlichkeit-sjt.md` · this skill's `references/checks.md`.
3. Solve blind, per keyed item: own result · own index · seconds needed · one line per wrong option (which mistake leads there, or "none found") → then own Python check over all options · blind-solving table `references/checks.md`.
4. Scripts: `python <coach skill dir>/scripts/check_items.py <folder>` · sheets exist → `python <base skill dir>/scripts/check_material.py <folder>` · each FAIL = Must · each `?` checked by hand · read every `check` expression: computes from stem's numbers, or restates the answer? · green run proves neither stem nor level → steps 3, 5, 6 never skipped.
5. Compare own indices and values with `answer` · explanation · key line and sections of sheets · answer sheet cells · scoring block → recompute section times, totals, percent.
6. Test checks: walk `references/checks.md` (E1-E14) item by item, file by file.
7. Language: German simple, correct, "du", sentence length · each German text vs its English sidecar text · each sheet pair with 3-step test of base `bilingual.md` · deciding words (`nicht`, `mindestens`, `höchstens`, `vor`, `nach`, `je`) same meaning · numbers in notation of each language · test-object texts left untranslated.
8. Sheets: open every HTML · print preview: no question split · material and figure with their questions · Merkfähigkeit material on own page · answer sheet on one page · footer present · toggle hides all English.
9. Base checklist: areas 1-12 of base `review.md`, readings: 1 (curriculum) = fit to area tables in `bereiche.md` + profile · 3 (operators, AFB) = difficulty labels · 5 (marking scheme) = scoring block without grade key · 8 (differentiation) = difficulty mix.
10. Report: `reviews/einstellungstest-review-<YYYY-MM-DD-HHMM>.md` in base report format (name taken → `-2`, `-3`; never overwrite) + extra section "Nachgerechnet" (table: id · difficulty · own result · own index · key · match · other options wrong · seconds) · `/reviews/` added to `.gitignore` when folder first created → reply: verdict · counts · report path · three most important fixes.
11. Fixes only on request: Must first → re-run scripts → re-solve changed items → append "Nach Korrektur" with new verdict to same report.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | checks E1-E14 with "Must when" · blind-solving table · frequent defects · report additions |
