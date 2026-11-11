---
name: darshan-singh-meel-kaenguru-review
description: Reviews Känguru der Mathematik (Math Kangaroo) training material - practice sets with solutions, timed mock tests with answer sheet and marking scheme, strategy explanations, training lessons, animations - against the shared school rubric plus competition checks - every problem solved independently, exactly one correct option, distractors that come from real mistakes, 3/4/5-point difficulty, level knowledge, competition rules and scoring, key balance, originality (no copied competition problems), and the German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-kaenguru or on any existing Känguru-style material. Triggers - "Känguru-Material prüfen", "Känguru-Aufgaben prüfen", "Übungswettbewerb gegenlesen", "Lösungsbuchstaben prüfen", "Känguru-Ablenker prüfen", "Knobelaufgaben im Känguru-Stil nachrechnen"; "review Kangaroo practice", "check my Kangaroo mock test", "verify the Kangaroo answer key", "check the Kangaroo distractors".
---

# Känguru: review

Load `darshan-singh-meel-schule` (rubric, formats, language rule) and `darshan-singh-meel-kaenguru` (rules, levels, problem building, formats). This skill adds the competition checks and fixes the order of work. It reviews; it changes files only when the user asks for fixes.

## Rules
- **Independent.** Solve every problem from the printed stem, figure and options alone, before opening `loesung.html`, `erwartungshorizont.html` or `pruefung.py`. Write your own letter list first, then compare.
- **Own computation.** For every problem with numbers or finitely many cases write your own short Python check in the scratchpad (not a copy of the folder's `pruefung.py`); it tests all five options, not only the keyed one.
- **Every option.** A problem passes only when the key is right **and** each other option is wrong under every reasonable reading of the stem.
- **Evidence.** Every finding names file and problem number, quotes the text, and gives the corrected text, value or letter. No finding from memory of what such material usually contains.
- **Severity** as in base `review.md`; competition Must conditions in `references/checks.md`. A `check:` line of a reference is a Should ("verify with <page>"), never a fact.
- **Rules of the competition** are compared with `wettbewerb.md` of the teacher skill, not with memory; a rule the material states that is not in that file is a finding.
- **Originality.** Never paste a problem into a web search. A suspicion of copying is reported with the reason (wording, figure, option set typical of a known paper) and the request to the author to confirm the source.
- **Privacy.** No names from filled answer sheets or score lists in the report.
- **No rewrite.** Findings carry a concrete fix; files stay as they are until the user says "fix".

## Process (fixed)
1. **Scope** - folder and files (default: every `.html` and `pruefung.py` in `unterricht/kaenguru/<stufe>/<thema>/`). Level from `data-stufe`; kind (practice set or mock test) from the file names. Ask only when it cannot be read from the files.
2. **Read** base `review.md`, `bilingual.md`, `formate.md`; teacher skill `wettbewerb.md`, the level file, `aufgabenbau.md`, `formate.md`, `begriffe.md`, and `strategien.md` when a strategy is named; `references/checks.md` of this skill.
3. **Solve blind** - task file only. Per problem: own result, own letter, time needed, strategy used, one line on each wrong option (which mistake leads there, or "no mistake found"). Then the own Python check over all options.
4. **Scripts** - `python <base skill dir>/scripts/check_material.py <folder>` and `python <kaenguru skill dir>/scripts/kaenguru_check.py <folder>` (runs `pruefung.py` and compares its letters and problem numbers with the key file; checks `data-max`, `data-stufe`, footer). Each FAIL is a Must; each `?` is checked by hand and becomes a finding or is noted as a false alarm. Read `pruefung.py`: does each function compute from the stem's data, or does it only restate the answer? A green script run proves neither the stem nor the level: steps 3, 5 and 6 are never skipped.
5. **Compare** own letters and values with the key line, each solution, the Erwartungshorizont rows, `pruefung.py`, explanation and animation. Recompute the point sum, start points, maximum (also the addends printed beside it), the worked scoring example and the AFB shares.
6. **Competition checks** - walk `references/checks.md` (K1-K14) problem by problem and file by file.
7. **Language pairs** - every DE/EN pair with the 3-step test of base `bilingual.md`; terms against `begriffe.md`; the words that decide the answer (genau, mindestens, höchstens, je, verschieden) carry the same meaning in both lines; options translated the same way in stem and solution.
8. **Animation and print** - step through every animation step forwards and backwards; print preview of every file: no problem split, figure with its stem, answer sheet on one page, key files within the page limit of the teacher skill's `formate.md`. Test the ← → keys before clicking a control button: the base animation engine ignores them while a button has focus (report as Other for the base skill, not as a defect of the material).
9. **Base checklist** - areas 1-12 of base `review.md`; area 5 reads "scoring" instead of "grade key" (a mock test has none), area 8 reads "rising difficulty" instead of three differentiation levels.
10. **Report** - write `reviews/darshan-singh-meel-kaenguru-review-<YYYY-MM-DD-HHMM>.md` in the base report format, with the extra section "Nachgerechnet" (table: problem · points · own result · own letter · key · match · other options wrong · time). Add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, report path, the three most important fixes.
11. **Fixes** only on request: apply Must first, extend `pruefung.py`, re-run both scripts, re-solve the changed problems, append "Nach Korrektur" with the new verdict to the same report.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | competition checks K1-K14 with "Must when", the blind-solving table, frequent defects of multiple-choice problems |
