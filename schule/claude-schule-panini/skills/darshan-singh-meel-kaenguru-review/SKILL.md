---
name: darshan-singh-meel-kaenguru-review
description: Reviews Känguru der Mathematik (Math Kangaroo) training material - practice sets with solutions, timed mock tests with answer sheet and marking scheme, strategy explanations, training lessons, animations - against the shared school rubric plus competition checks - every problem solved independently, exactly one correct option, distractors that come from real mistakes, 3/4/5-point difficulty, level knowledge, competition rules and scoring, key balance, originality (no copied competition problems), and the German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-kaenguru or on any existing Känguru-style material. Triggers - "Känguru-Material prüfen", "Känguru-Aufgaben prüfen", "Übungswettbewerb gegenlesen", "Lösungsbuchstaben prüfen", "Känguru-Ablenker prüfen", "Knobelaufgaben im Känguru-Stil nachrechnen"; "review Kangaroo practice", "check my Kangaroo mock test", "verify the Kangaroo answer key", "check the Kangaroo distractors".
---

# Känguru: review
Scope: review only; edit files only on "fix". Load `darshan-singh-meel-schule` (rubric, formats, language rule) + `darshan-singh-meel-kaenguru` (rules, levels, building, formats). `→` then · `·` list.

## Rules
- Independent: solve every problem from printed stem, figure, options before opening `loesung.html`, `erwartungshorizont.html`, `pruefung.py` · own letter list first → then compare.
- Own computation: numbers or finitely many cases → own short Python check in scratchpad (not the folder's `pruefung.py`) · tests all five options.
- Every option: pass = key right and each other option wrong under every reasonable reading.
- Evidence: finding = file + problem number + quoted text + corrected text, value or letter · nothing from memory of what such material usually holds.
- Severity per base `review.md` · Must conditions `references/checks.md` · `check:` line → Should ("verify with <page>"), never fact.
- Competition rules compared with teacher skill `wettbewerb.md`, not memory · rule stated in material but absent there → finding.
- Originality: never paste a problem into a web search · suspected copy → report reason (wording, figure, option set typical of a known paper) + ask author for source.
- Privacy: no names from answer sheets or score lists in report.
- No rewrite: each finding carries concrete fix; files unchanged until "fix".

## Process
1. Scope: folder + files (default every `.html` and `pruefung.py` in `unterricht/kaenguru/<stufe>/<thema>/`) · level from `data-stufe` · kind (practice set / mock test) from file names · ask only if unreadable.
2. Read base `review.md` · `bilingual.md` · `formate.md` · teacher `wettbewerb.md` · level file · `aufgabenbau.md` · `formate.md` · `begriffe.md` · `strategien.md` if a strategy is named · `references/checks.md`.
3. Solve blind, task file only; per problem: own result · letter · time · strategy · one line per wrong option (mistake that leads there, or "no mistake found") → then own Python check over all options.
4. Scripts: `python <base skill dir>/scripts/check_material.py <folder>` · `python <kaenguru skill dir>/scripts/kaenguru_check.py <folder>` → FAIL = Must · `?` = check by hand → finding or false alarm · read `pruefung.py`: computes from stem data or only restates answer? · green run proves neither stem nor level → steps 3, 5, 6 never skipped.
5. Compare own letters and values with key line, each solution, Erwartungshorizont rows, `pruefung.py`, explanation, animation · recompute point sum, start points, maximum (and addends beside it), worked scoring example, AFB shares.
6. Competition checks: `references/checks.md` K1-K14, problem by problem, file by file.
7. Language pairs: each DE/EN pair through the 3-step test of base `bilingual.md` · terms vs `begriffe.md` · deciding words (genau, mindestens, höchstens, je, verschieden) same meaning in both lines · options translated identically in stem and solution.
8. Animation + print: every step forwards and backwards · print preview: no split problem · figure with stem · answer sheet one page · key files within page limit (teacher `formate.md`) · test ← → keys before clicking a button (engine ignores keys while a button has focus → Other for base skill, not a material defect).
9. Base checklist: areas 1-12 of base `review.md` · area 5 reads "scoring" not "grade key" · area 8 reads "rising difficulty" not three differentiation levels.
10. Report: `reviews/darshan-singh-meel-kaenguru-review-<YYYY-MM-DD-HHMM>.md`, base report format + section "Nachgerechnet" (table: problem · points · own result · own letter · key · match · other options wrong · time) · `/reviews/` → `.gitignore` on first creation · reply: verdict · counts · report path · three most important fixes.
11. Fixes on request only: Must first → extend `pruefung.py` → re-run both scripts → re-solve changed problems → append "Nach Korrektur" + new verdict to same report.

## Reference
- `references/checks.md`: competition checks K1-K14 with "Must when" · blind-solving table · frequent multiple-choice defects
