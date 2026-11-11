---
name: darshan-singh-meel-schule-powi-review
description: Review teaching material for Politik und Wirtschaft and Wirtschaftswissenschaften (Hessen, Gymnasium Sek I and Oberstufe) - solves every task independently, checks curriculum fit (Inhaltsfelder, KCGO Themenfelder, GK/LK), neutrality (Beutelsbacher Konsens), sources and dates of every real figure, labels on model data, institutions and law, models and diagrams, judgement tasks and their marking, the German lines and their English lines, animations, and writes a report with verdict and Must / Should / Other findings to reviews/. Use with darshan-singh-meel-schule and darshan-singh-meel-schule-powi. Triggers - "PoWi-Material prüfen", "Arbeitsblatt Politik und Wirtschaft überprüfen", "Klausur PoWi gegenlesen", "Erwartungshorizont prüfen", "ist das neutral", "Beutelsbacher Konsens prüfen", "Daten und Quellen prüfen", "Review Wirtschaft"; "review my economics worksheet", "check the politics test", "is this material balanced", "check sources and dates", "review the market animation".
---

# Review: Politik und Wirtschaft · Wirtschaftswissenschaften
Reviews, never rewrites → fixes only on ask, then re-run checks.

## Load
- `darshan-singh-meel-schule`: `references/review.md` (process, 12-area checklist, severity, report, verdict) · `bilingual.md` · `operatoren.md` · `bewertung.md` (tests).
- `darshan-singh-meel-schule-powi`: level reference (`sek1.md` · `oberstufe.md` · `wirtschaftswissenschaften.md`) · `fachregeln.md` · `modelle-animationen.md` (model) · `begriffe.md`.
- This skill: `references/checks.md`.

## Process
1. Scope → files (default every `.html` in topic folder) · ask only if level or GK/LK unreadable from files.
2. `python <base skill dir>/scripts/check_material.py <folder>` → every FAIL = Must · every `?` by hand.
3. Solve first → every task from material alone, before opening `loesung.html` / `erwartungshorizont.html` · note result, steps, for judgement tasks 2 defensible positions + criteria · recompute table rows vs curve, intersections, flow sums, %, percentage points, point totals, grade thresholds.
4. Compare with solution → differences = findings (wrong solution · ambiguous task · missing alternative · points not awardable).
5. Subject checks → `references/checks.md` P1-P10.
6. Base checklist areas 1-12 · DE/EN pairs (3-step test) · terms vs `begriffe.md`.
7. Animation → step forwards + backwards · captions vs picture · end state vs solution.
8. Report → `reviews/darshan-singh-meel-schule-powi-review-<YYYY-MM-DD-HHMM>.md` (base format) · first use → add `/reviews/` to `.gitignore` · reply: verdict · counts · report path (relative) · 3 top findings.

## Severity (adds to base table)
- Must → one-sided material or solution rewarding one position · real figure without source/Stand/date, or real + model mixed, or untraceable · wrong statement on institution, legal rule, model mechanism, number · real person/party/firm judged, or outdated office holder/majority shown as current · copied cartoon, press text, textbook task.
- Should → model without any limit · judgement criteria missing in task but demanded in marking · data >2 years old without note · `check:` items the material relies on.
- Other → stronger controversy · better material type · clearer diagram.

## Report additions
- "Unabhängig gelöst / Solved independently" → per task: own result · solution's result · `gleich` or difference.
- "Daten und Quellen / Data and sources" → per real figure: value · source line present · date · verified (yes/no, why).
- Verifying figures → needs network + official pages only (`fachregeln.md` list) · else list under "Not checked".
