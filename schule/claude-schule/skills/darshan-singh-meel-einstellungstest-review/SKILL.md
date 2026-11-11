---
name: darshan-singh-meel-einstellungstest-review
description: Strict review of Einstellungstest material for Ausbildung applicants - question and chapter JSON with English sidecars, practice sheets, mock tests with answer key, target profiles. Solves every item independently before opening the key; checks exactly one correct option (none for Persönlichkeit and Situational Judgement - there the explanation), answer index and explanation, distractors, difficulty and time, fidelity to the named target pages, simple German and matching English, originality against published sample questions, no personal data. Writes a report with verdict and Must / Should / Other to reviews/. Reviews only; fixes only when asked. Loads darshan-singh-meel-schule and darshan-singh-meel-einstellungstest. Triggers - "Einstellungstest-Fragen prüfen", "Testfragen gegenlesen", "Probetest prüfen", "Lösungen nachrechnen"; "review aptitude test questions", "check my mock test", "verify the answer key".
---

# Einstellungstest: review

Load `darshan-singh-meel-schule` (rubric, formats, language rule) and `darshan-singh-meel-einstellungstest` (areas, item building, formats, target research). This skill adds the test checks and fixes the order of work. It reviews; it changes files only when the user asks for fixes.

## Rules
- **Independent.** Solve every keyed item from stem, `material`, `figure` and options alone, before reading `answer`, `explanation`, `check`, `loesung.html` or `erwartungshorizont.html`. Write your own index list first, then compare. Hide the key with a script that prints the items without `answer`, `explanation` and `check`.
- **Own computation.** For every item with numbers, a series or finitely many cases write your own short Python check in the scratchpad - not a copy of the item's `check` - and test all four options, not only the keyed one.
- **Every option.** An item passes only when the key is right **and** each other option is wrong under every reasonable reading of the stem.
- **No key, other duty.** Persönlichkeit and SJT items (`answer` -1) have no option to verify. Check instead: no hidden key or ranking in the explanation, what each option shows is fair and plausible, the honesty rule holds (`persoenlichkeit-sjt.md` of the coach skill).
- **Evidence.** Every finding names file and item id, quotes the text, and gives the corrected text, value or index. No finding from memory of what such material usually contains.
- **Facts about tests** are compared with the pages named in `profil.json` `sources` and the verified table in `ziel.md`, not with memory. A fact no named page states is a finding unless marked `check:`; a `check:` line presented as fact is a finding.
- **Originality.** Never paste an item into a web search. A suspicion of copying is reported with the reason and the request to the author to confirm the source.
- **Privacy.** The report never repeats a person's data or an access detail found in a file; it says "personal or access detail in <file>, <key>".
- **Severity** as in base `review.md`; test-specific Must conditions in `references/checks.md`.
- **No rewrite.** Findings carry a concrete fix; files stay as they are until the user says "fix".

## Process (fixed)
1. **Scope** - files or folder (default: every `.json` and `.html` of the topic folder in `unterricht/einstellungstest/`). Kind from the content: practice set · mock test · target profile. Ask only when it cannot be read from the files.
2. **Read** base `review.md`, `bilingual.md`; coach skill `bereiche.md`, `aufgabenbau.md`, `formate.md`, and by content `ziel.md`, `persoenlichkeit-sjt.md`; `references/checks.md` of this skill.
3. **Solve blind** - per keyed item: own result, own index, seconds needed, one line on each wrong option (which mistake leads there, or "none found"). Then the own Python check over all options. Blind-solving table: `references/checks.md`.
4. **Scripts** - `python <coach skill dir>/scripts/check_items.py <folder>` and, when sheets exist, `python <base skill dir>/scripts/check_material.py <folder>`. Each FAIL is a Must; each `?` is checked by hand. Read every `check` expression: does it compute from the stem's numbers, or restate the answer? A green run proves neither stem nor level: steps 3, 5 and 6 are never skipped.
5. **Compare** own indices and values with `answer`, the explanation, the key line and sections of the sheets, the answer sheet cells, the scoring block. Recompute section times, totals and percent.
6. **Test checks** - walk `references/checks.md` (E1-E14) item by item and file by file.
7. **Language** - German: simple, correct, "du", sentence length; each German text against its English sidecar text and each sheet pair with the 3-step test of base `bilingual.md`; deciding words (`nicht`, `mindestens`, `höchstens`, `vor`, `nach`, `je`) carry the same meaning; numbers in the notation of each language; test-object texts left untranslated.
8. **Sheets** - open every HTML; print preview: no question split, material and figure with their questions, Merkfähigkeit material on its own page, answer sheet on one page, footer present, toggle hides all English.
9. **Base checklist** - areas 1-12 of base `review.md` with these readings: 1 (curriculum) = fit to the area tables in `bereiche.md` and the profile; 3 (operators, AFB) = difficulty labels; 5 (marking scheme) = scoring block without grade key; 8 (differentiation) = difficulty mix.
10. **Report** - write `reviews/einstellungstest-review-<YYYY-MM-DD-HHMM>.md` in the base report format (name taken → add `-2`, `-3`; never overwrite a report), with the extra section "Nachgerechnet" (table: id · difficulty · own result · own index · key · match · other options wrong · seconds). Add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, report path, the three most important fixes.
11. **Fixes** only on request: Must first; re-run the scripts; re-solve the changed items; append "Nach Korrektur" with the new verdict to the same report.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | checks E1-E14 with "Must when", the blind-solving table, frequent defects, report additions |
