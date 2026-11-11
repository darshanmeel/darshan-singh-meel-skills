---
name: darshan-singh-meel-schule-geschichte
description: Geschichte teaching material for Gymnasium in Hessen - Sek I (Jg. 5-10, Kerncurriculum) and Oberstufe (KCGO, E, Q1-Q4, GK and LK) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations, source work with public-domain or own sources and full citation, checked dates, true-to-scale timelines as generated SVG, step animations. German text with the closest English sentence under every line, sources stay German with a word list, terms DE | EN (Bili option). Use for any request to plan, write or explain Geschichte lessons or material; load darshan-singh-meel-schule alongside. Triggers - "Geschichte", "Geschichte LK", "Quellenanalyse", "Karikatur analysieren", "Zeitleiste", "Zeitstrahl", "Sachurteil", "Bili Geschichte"; "history lesson", "history worksheet", "history test", "source analysis", "timeline", "bilingual history".
---

# Geschichte (Gymnasium Hessen)
Subject side of `darshan-singh-meel-schule` (base). Formats, folders, DE+EN rule, grading, operators, check script → base.

## Scope
- Sek I Jg. 5-10 → `jg05`…`jg10` · `references/sek1.md`
- E, Q1-Q4 GK/LK (KCGO) → `e`, `q1-gk`…`q4-lk` · `references/oberstufe.md`
- Out: `unterricht/geschichte/<stufe>/<thema>/`. Not covered: Grundschule, Realschule/Hauptschule KC, Gesellschaftslehre.

## Rules
- KC cite: Sek I = Kompetenzbereich + Kompetenzerwartung (Ende Jg. 9/10 only) + Basisnarrativ + Dimension. Oberstufe = Standard code (`W2`, `A5`, `U6`, `O3`) + `<Halbjahr>.<Nr> <Themenfeld>` + GK/LK. Wording only from refs; else `check: <KC PDF>`.
- GK never gets LK-only content (W7, A7-A8, U9-U11, O8-O9, "erhöhtes Niveau"). Binding Themenfelder per Erlass/year → ask or `check: Abiturerlass`.
- Every date, name, number, quotation verified vs official/scholarly public source, listed under material ("Daten nach: …"). Unverifiable → rewrite task or `check:`. Sources differ → name the act ("verkündet am", "unterzeichnet am", "in Kraft seit").
- Material `M1…` headed `Quelle` (of the time) or `Darstellung` (later). Own text = Darstellung "verfasst für diese Aufgabe / written for this task"; never faked as source, never invented quotation of a real person.
- Sources: public domain or own (laws, constitutions, official texts; authors dead >70 y; own picture/cartoon descriptions). Citation: author · title/type · date · place · cited from · cuts `[...]` · "originalgetreu"/"modernisiert". → `quellenarbeit.md`.
- Sources stay German (`data-nur-de`): tasks get EN line; word list `Wörter der Quelle` DE | EN | Bedeutung. Foreign source → cited German translation, or original in Bili.
- Wiedergeben (AFB I) → einordnen, erläutern, herausarbeiten, vergleichen (II) → beurteilen, bewerten, erörtern (III). No judgement in a summary.
- Sachurteil = standards of the time + criteria · Werturteil = today's stated values. Task names which; model answer names criteria; open judgements accept both directions if reasoned.
- Contested topic → ≥2 perspectives (sources) or interpretations (Darstellungen). No single cause; Anlass · Ursachen · Folgen apart.
- Loaded/NS terms only in quotes + explanation („Machtergreifung“, „Euthanasie“, „Drittes Reich“); not adopted as description. Wording → `begriffe.md`.
- Sensitive (Shoah, genocide, slavery, colonial violence, war, flight/expulsion): factual, respectful, victims as persons; no role play, no "imagine you are a prisoner", no gamification, no violent images, no unconstitutional symbols (check: StGB §§ 86, 86a → describe in words).
- Timelines true to scale via `scripts/zeitleiste.py`; broken axis marked. Animation dates = worksheet = solution.
- Epochs/labels are constructs (KC: Konstruktcharakter); from Jg. 9 say so where it matters.

## Process
1. Setup → base questions, one AskUserQuestion (max 4, rec first):
   - Jahrgang/Kurs · Thema (3 from Basisnarrative/Themenfeld)
   - Material: Textquelle gemeinfrei (rec) · Karikatur/Bildquelle as description · Statistik · Darstellung for the task · user's own source
   - 2nd prompt only if open: Sprache, Zeit, Differenzierung. Leitfrage proposed, not asked.
2. Read level ref · `quellenarbeit.md` · `begriffe.md` · base files per base SKILL.md.
3. Plan 5 lines (base step 3) + Leitfrage, M1… with type + citation, Dimension(en), origin of each date.
4. Create from base templates, DE line → EN line. Timeline: `python <skill dir>/scripts/zeitleiste.py START ENDE events.txt --out zeitleiste.svg` → inline as numbered `Darstellung`, caption START, ENDE, "Daten nach"; in worksheet if a task needs dates. Animation: `--anim`, printed x positions = steps of `#lauf`. KC ref in a teacher file. Example: `references/examples/grundrechte-1849/`.
5. Self-check: solve from material only, then compare. Per task: facts checked vs cited source · quotation exact · Quelle/Darstellung label · operator/AFB · solvable from info box + material + prior lessons · level · summary ≠ analysis ≠ judgement · Sach-/Werturteil named + criteria · no anachronism, no single cause · timeline, worksheet, solution same dates.
6. Layout: `python <base skill dir>/scripts/check_material.py unterricht/geschichte/<stufe>/<thema>/` → fix errors, read `?` (sources need `data-nur-de`). By eye: source set off, line numbers if cited, citation under source, answer space fits, A4 preview.
7. Hand over: files (relative) · KC ref · text/date sources · every `check:` · offer `darshan-singh-meel-schule-geschichte-review` (rec for tests/Klausuren).

## References
- `references/sek1.md` · Jg. 5-10: Kompetenzbereiche, Erwartungen, Basiskonzept, Basisnarrative, 5 Dimensionen, default per year
- `references/oberstufe.md` · E, Q1-Q4: W/A/U/O codes (GK, LK), Themenfelder, binding rules
- `references/quellenarbeit.md` · source types, analysis steps, citation/copyright, Sach-/Werturteil, date checks, errors, timelines, animations
- `references/begriffe.md` · glossary DE | EN, loaded terms, false friends
- `references/examples/grundrechte-1849/` · finished Q1 GK set
- `references/sources.md` · official pages, verified vs `check:`
- `scripts/zeitleiste.py` · true-to-scale SVG (`--anim`) + x positions
