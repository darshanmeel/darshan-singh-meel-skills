---
name: darshan-singh-meel-schule-nwt-review
description: Reviews teaching material for Naturwissenschaft und Technik (NWT, NaWi-Technik, MINT-Wahlunterricht) in the Mittelstufe of the Gymnasium in Hessen - lesson plans, worksheets and solutions, competence checks with marking scheme, explanations, animations of technical systems - against the shared school rubric plus NWT checks - correct curriculum anchor (Wahlunterricht, no invented NWT-Kerncurriculum), every task solved independently, units and plausibility, measurable requirements, buildable instructions, technical drawings and diagrams, tool and experiment safety, assessment with Vermerke, and the German/English line pairs. Writes a report with verdict and Must/Should/Other findings to reviews/. Reviews only; fixes only when asked. Triggers - "NWT-Material prüfen", "NaWi Arbeitsblatt prüfen", "Technik-Projekt gegenlesen", "Bauanleitung prüfen", "Konstruktionsaufgabe prüfen", "Sicherheit Werkzeug prüfen"; "review STEM worksheet", "check my engineering task", "check build instructions", "review science and technology lesson".
---

# Naturwissenschaft und Technik: review (Hessen)

Load `darshan-singh-meel-schule` (rubric, formats, language rule) and `darshan-singh-meel-schule-nwt` (what Hessen offers, modules, technical methods, safety, assessment). For calculations and experiments also the physics skill's `konventionen.md` and `experimente.md`. This skill adds the NWT checks and fixes the order of work. It reviews; it changes files only when the user asks.

## Rules
- **Independent.** Solve every task and follow every build or measuring instruction from the material alone before opening the Lösung. Never copy a number from the solution into your own calculation.
- **Evidence.** Each finding names file, task or line, quotes the text and gives the corrected text or value.
- **Curriculum truth.** Hessen has no Kerncurriculum for NWT at the Gymnasium: a citation of one is a Must. The anchor must be a real Inhaltsfeld and standard of Physik, Chemie or Biologie (`module.md`, physics `sek1.md`), plus the Wahlunterricht line.
- **Severity** as in base `review.md`; NWT Must conditions in `references/checks.md`. `check:` lines of the references are Should findings ("verify with <page>").
- **No rewrite.** Findings carry a concrete fix; files stay unchanged until the user says "fix".

## Process (fixed)
1. **Scope** - folder and files (default: every `.html` in `unterricht/nawi-technik/<stufe>/<thema>/`); course frame (Wahlunterricht without Noten, or graded by school decision) from the files, else ask once.
2. **Read** base `review.md`, `bilingual.md`, `formate.md`; NWT `hessen-nwt.md`, `technik.md`, the module row in `module.md`; physics `konventionen.md`, and `experimente.md` when something is built or measured; `references/checks.md` of this skill.
3. **Scripts** - `python <base skill dir>/scripts/check_material.py <folder>` and `python <physics skill dir>/scripts/check_einheiten.py <folder>`. Each FAIL is a Must; each `?` is checked by hand.
4. **Solve and build in the head** - every calculation with a second way or estimate; every requirement tested against the model solution; every build step followed with the listed parts and tools only (missing part, impossible order, unclear dimension = finding).
5. **NWT checks** - walk `references/checks.md` (N1-N10).
6. **Language pairs** - base 3-step test; terms against NWT `begriffe.md` and the physics list; decimal comma/point; same numbers in both lines.
7. **Animation** - `node --check` on the page's last `<script>` block (unescaped apostrophe in a caption stops the player); every step forwards and backwards with the buttons and with ← → after a click on Weiter, a screenshot of every step (labels covered or cut off), each speed, English toggle, print preview; ratios, directions of rotation and order of cause and effect against `technik.md` (system animations).
8. **Base checklist** - areas 1-12 of base `review.md` (area 6 includes author voice: no chat, request or requester in the material).
9. **Report** - `reviews/darshan-singh-meel-schule-nwt-review-<YYYY-MM-DD-HHMM>.md` in the base report format, with the section "Nachgerechnet" (task · own result · material's result · match). Add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, report path, the three most important fixes.
10. **Fixes** only on request: Must first, re-run both scripts, re-solve the changed tasks, append "Nach Korrektur" with the new verdict.

## Reference
| File | Content |
|---|---|
| `references/checks.md` | NWT checks N1-N10 with "Must when", frequent defects |
| `references/examples/review-beispiel.md` | one real report (Jg. 9 Kettentrieb) as a model for form and depth |
