---
name: darshan-singh-meel-schule-nwt-review
description: Reviews teaching material for Naturwissenschaft und Technik (NWT, NaWi-Technik, MINT-Wahlunterricht) in the Mittelstufe of the Gymnasium in Hessen - lesson plans, worksheets and solutions, competence checks with marking scheme, explanations, animations of technical systems - against the shared school rubric plus NWT checks - correct curriculum anchor (Wahlunterricht, no invented NWT-Kerncurriculum), every task solved independently, units and plausibility, measurable requirements, buildable instructions, technical drawings and diagrams, tool and experiment safety, assessment with Vermerke, and the German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Triggers - "NWT-Material prüfen", "NaWi Arbeitsblatt prüfen", "Technik-Projekt gegenlesen", "Bauanleitung prüfen", "Konstruktionsaufgabe prüfen", "Sicherheit Werkzeug prüfen"; "review STEM worksheet", "check my engineering task", "check build instructions", "review science and technology lesson".
---


# NWT review (Hessen)
Load `darshan-singh-meel-schule` (rubric, formats, language) + `darshan-singh-meel-schule-nwt` (offer, modules, methods, safety, assessment) · calculations/experiments → also physics `konventionen.md`, `experimente.md`. Reviews only · edits files only on "fix".

## Rules
- Independent: solve every task and follow every build/measuring instruction from the material alone before opening Lösung · never copy a number from the solution.
- Evidence: file + task/line · quote text · give corrected text/value.
- Curriculum truth: no NWT-Kerncurriculum at Hessen Gymnasium → citing one = Must · anchor = real Inhaltsfeld + standard of Physik/Chemie/Biologie (`module.md`, physics `sek1.md`) + Wahlunterricht line.
- Severity: base `review.md` · NWT Must conditions → `references/checks.md` · `check:` line = Should ("verify with <page>").
- No rewrite: every finding carries a concrete fix.

## Process
1. Scope: folder/files (default every `.html` in `unterricht/nawi-technik/<stufe>/<thema>/`) · course frame (Wahlunterricht ohne Noten | graded by school decision) from files, else ask once.
2. Read: base `review.md` · `bilingual.md` · `formate.md` · NWT `hessen-nwt.md` · `technik.md` · module row in `module.md` · physics `konventionen.md` · `experimente.md` (if built/measured) · `references/checks.md`.
3. Scripts: `python <base skill dir>/scripts/check_material.py <folder>` + `python <physics skill dir>/scripts/check_einheiten.py <folder>` → FAIL = Must · `?` = by hand.
4. Solve and build in head: every calculation with second way/estimate · every requirement tested vs model solution · every build step with listed parts and tools only (missing part, impossible order, unclear dimension = finding).
5. Walk `checks.md` N1-N10.
6. Language pairs: base 3-step test · terms vs NWT `begriffe.md` + physics list · comma/point · same numbers.
7. Animation: `node --check` on last `<script>` block (unescaped apostrophe in caption stops player) · every step forward/back with buttons and ← → after click on Weiter · screenshot every step (labels covered/cut) · each speed · English toggle · print preview · ratios, rotation directions, cause → effect order vs `technik.md` (system animations).
8. Base checklist areas 1-12 of `review.md`.
9. Report `reviews/darshan-singh-meel-schule-nwt-review-<YYYY-MM-DD-HHMM>.md`: base format + section "Nachgerechnet" (task · own result · material's result · match) · add `/reviews/` to `.gitignore` on first creation · reply: verdict · counts · path · 3 top fixes.
10. Fixes only on request: Must first → re-run both scripts → re-solve changed tasks → append "Nach Korrektur" + new verdict.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | N1-N10 + "Must when" · frequent defects |
| `references/examples/review-beispiel.md` | real report (Jg. 9 Kettentrieb) as model |
