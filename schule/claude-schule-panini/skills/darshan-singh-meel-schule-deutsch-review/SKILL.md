---
name: darshan-singh-meel-schule-deutsch-review
description: Reviews Deutsch teaching material for Hessen (Grundschule Jg. 1-4, Gymnasium Sek I and Oberstufe) - lesson plans, worksheets and solutions, Klassenarbeiten and Klausuren with Erwartungshorizont, explanations, animations - against the shared school rubric plus Deutsch checks (every task solved independently, German of the material, text source and wording, curriculum level, Erwartungshorizont and points, English help line). Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Use after darshan-singh-meel-schule-deutsch or on any existing Deutsch material named by school year or course; CEFR-level material (A1-C1) goes to darshan-singh-meel-daf-review. Triggers - "Deutsch-Material prüfen", "Arbeitsblatt Deutsch prüfen", "Diktat prüfen", "Klausur Deutsch gegenlesen", "Erwartungshorizont Deutsch prüfen", "Aufsatzaufgabe prüfen"; "review German worksheet" (school subject), "check my German test", "check the essay marking scheme".
---

# Deutsch review (Hessen)
Load `darshan-singh-meel-schule` (rubric, formats, grading, language) + `darshan-singh-meel-schule-deutsch` (curriculum, text, writing). Reviews only · edits files only on "fix".

## Rules
- Independent: answer every task from task text + material before opening Lösung/EH · grammar via named Probe · text work via own count of verses, lines, rhyme letters, stressed syllables.
- Evidence: file + task/line · quote wrong text · give corrected text · verse/line number on text findings · nothing from memory of "what such material contains".
- Material = spelling model: proofread every German line (Rechtschreibung · Zeichensetzung · Grammatik) · one error in a student-facing file = Must.
- Severity: base `review.md` · Deutsch Must conditions → `references/checks.md` · `check:` line = Should ("verify with <page>"), never fact.
- Curriculum facts from Deutsch skill references, not memory · Landesabitur texts/Themenfelder vs Erlass of the exam year · year not covered → "Not checked" + page to read.
- Open tasks: differing reading = no finding if text supports it · criterion text does not support = finding.
- Privacy: no names in report · no filled-in student work with names.
- No rewrite: every finding carries a concrete fix.

## Process
1. Scope: folder/files (default every `.html` in `unterricht/deutsch/<stufe>/<thema>/`) · level, GK/LK, exam year, test type from files · ask only if unreadable.
2. Read: base `review.md` · `bilingual.md` · `formate.md` · `bewertung.md` (if test) · Deutsch `grundschule.md` | `sek1.md` | `oberstufe.md` · `sprache.md` (language tasks) · `texte.md` (text work) · `schreibaufgaben.md` (writing) · `references/checks.md`.
3. Script: `python <base skill dir>/scripts/check_material.py <folder>` → `FAIL` = Must · `?` = by hand: add help line, or `data-nur-de` if it must stay German.
4. Solve every task → fill table "Nachgeprüft" (`checks.md`) → compare with Lösung, EH, Erklärung, animation captions · recompute every point/BE sum, percentage, key threshold, 70 : 30 and Fehlerindex examples.
5. Proofread every German line · every text vs source (author, years, title, year, status; wording word by word vs edition or user-pasted text · neither → ask once for class edition · still none → Must "Wortlaut ungeprüft", file not ready, no word corrected from memory).
6. Walk `checks.md` D1-D12 file by file.
7. Help line: allowed place (Deutsch skill table) · closest natural sentence (base `bilingual.md` 3-step test) · no answer given away · no German text translated.
8. Animation: steps forward/back · each speed · English toggle · print preview · every moved unit, capital, end state vs Lösung (D12).
9. Base checklist areas 1-12 of `review.md` · print preview: count pages.
10. Report `reviews/darshan-singh-meel-schule-deutsch-review-<YYYY-MM-DD-HHMM>.md`: base format + section "Nachgeprüft" · add `/reviews/` to `.gitignore` on first creation · reply: verdict · counts · path · 3 top fixes.
11. Fixes only on request: Must first → re-run script → re-solve changed tasks → append "Nach Korrektur" + new verdict to same report.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | D1-D12 + "Must when" · independent-answer table · frequent defects · verdict rule |
