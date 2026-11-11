---
name: darshan-singh-meel-schule-deutsch-review
description: Reviews Deutsch teaching material for Hessen (Grundschule Jg. 1-4, Gymnasium Sek I and Oberstufe) - lesson plans, worksheets and solutions, Klassenarbeiten and Klausuren with Erwartungshorizont, explanations, animations - against the shared school rubric plus Deutsch checks (every task solved independently, German of the material, text source and wording, curriculum level, Erwartungshorizont and points, English help line). Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-schule-deutsch or on any existing Deutsch material named by school year or course; CEFR-level material (A1-C1) goes to darshan-singh-meel-daf-review. Triggers - "Deutsch-Material prüfen", "Arbeitsblatt Deutsch prüfen", "Diktat prüfen", "Klausur Deutsch gegenlesen", "Erwartungshorizont Deutsch prüfen", "Aufsatzaufgabe prüfen"; "review German worksheet" (school subject), "check my German test", "check the essay marking scheme".
---

# Deutsch: review (Hessen)

Load `darshan-singh-meel-schule` (rubric, formats, grading, language rule) and `darshan-singh-meel-schule-deutsch` (curriculum, text and writing rules). This skill adds the Deutsch checks and fixes the order of work. It reviews; it changes files only when the user asks for fixes.

## Rules
- **Independent.** Answer every task from the task text and the material alone before opening Lösung or Erwartungshorizont: grammar with the named Probe, text work with your own count of verses, lines, rhyme letters and stressed syllables.
- **Evidence.** Every finding names file and task or line, quotes the wrong text and gives the corrected text. Text findings carry the verse or line number. No finding from memory of "what such material usually contains".
- **The material is a spelling model.** Every German line is proofread (Rechtschreibung, Zeichensetzung, Grammatik); one error in a student-facing file is a Must.
- **Severity** as in base `review.md`; Deutsch Must conditions in `references/checks.md`. A `check:` line of a reference is a Should ("verify with <page>"), never a fact.
- **Curriculum facts** come from the Deutsch skill's references, not from memory. Landesabitur texts and Themenfelder are compared with the Erlass of the course's exam year; a year not covered there → "Not checked" plus the page to read.
- **Open tasks.** A reading that differs from yours is no finding when the text supports it; a criterion the text does not support is one.
- **Privacy.** The report quotes no names; filled-in student work is not reviewed with names.
- **No rewrite.** Findings carry a concrete fix; files stay as they are until the user says "fix".

## Process (fixed)
1. **Scope** - folder and files (default: every `.html` in `unterricht/deutsch/<stufe>/<thema>/`). Level, GK/LK, exam year and type of test from the files; ask only when they cannot be read from them.
2. **Read** base `review.md`, `bilingual.md`, `formate.md`, and `bewertung.md` when a test is included; Deutsch `grundschule.md`, `sek1.md` or `oberstufe.md` for the level; `sprache.md` for language tasks, `texte.md` for text work, `schreibaufgaben.md` for writing tasks; `references/checks.md` of this skill.
3. **Script** - `python <base skill dir>/scripts/check_material.py <folder>`. Each `FAIL` is a Must; each `?` is checked by hand: add the help line, or `data-nur-de` when the line must stay German.
4. **Solve every task yourself** and fill the table "Nachgeprüft" (`checks.md`). Then compare with Lösung, Erwartungshorizont, Erklärung, animation captions. Recompute every sum of points or BE, every percentage, every threshold of the key, the 70 : 30 example and the Fehlerindex example.
5. **Proofread** every German line, then every text against its source line (author, years, title, year, status; wording word by word against an edition or the text the user pastes. Neither at hand → ask once for the class edition's text; still none → Must "Wortlaut ungeprüft": the file is not ready, and no word is corrected from memory).
6. **Deutsch checks** - walk `references/checks.md` (D1-D12) file by file.
7. **Help line** - where English stands: allowed place (Deutsch skill, table in "Rules"), closest natural sentence (3-step test of base `bilingual.md`), no answer given away, no German text translated.
8. **Animation** - step forwards and backwards, each speed, English toggle, print preview; every moved unit, capital letter and end state compared with the Lösung (`checks.md`, D12).
9. **Base checklist** - areas 1-12 of base `review.md`. Print preview: count the pages.
10. **Report** - `reviews/darshan-singh-meel-schule-deutsch-review-<YYYY-MM-DD-HHMM>.md` in the base report format plus the section "Nachgeprüft". Add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, report path, the three most important fixes.
11. **Fixes** only on request: Must first, re-run the script, re-solve the changed tasks, append "Nach Korrektur" with the new verdict to the same report.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | Deutsch checks D1-D12 with "Must when", the table for the independent answers, frequent defects, verdict rule |
