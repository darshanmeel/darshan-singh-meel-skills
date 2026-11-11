---
name: darshan-singh-meel-schule-geschichte
description: Geschichte teaching material for Gymnasium in Hessen - Sek I (Jg. 5-10, Kerncurriculum) and Oberstufe (KCGO, E, Q1-Q4, GK and LK) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations, source work with public-domain or own sources and full citation, checked dates, true-to-scale timelines as generated SVG, step animations. German text with the closest English sentence under every line, sources stay German with a word list, terms DE | EN (Bili option). Use for any request to plan, write or explain Geschichte lessons or material; load darshan-singh-meel-schule alongside. Triggers - "Geschichte", "Geschichte LK", "Quellenanalyse", "Karikatur analysieren", "Zeitleiste", "Zeitstrahl", "Sachurteil", "Bili Geschichte"; "history lesson", "history worksheet", "history test", "source analysis", "timeline", "bilingual history".
---

# Geschichte (Gymnasium Hessen, Sek I and Oberstufe)

Adds the subject side to `darshan-singh-meel-schule` (base): KC content, source work, dates, judgement, terms, timelines and animations. Formats, folders, the German + English rule, grading, operators and the check script are the base's - not repeated here.

## Scope
| Level | Folder `<stufe>` | Reference |
|---|---|---|
| Sek I, Jg. 5-10 | `jg05` ... `jg10` | `references/sek1.md` |
| Einführungsphase | `e` | `references/oberstufe.md` |
| Q1-Q4, GK or LK | `q1-gk` ... `q4-lk` | `references/oberstufe.md` |

Output folder: `unterricht/geschichte/<stufe>/<thema>/`. Not covered: Grundschule (Sachunterricht), Realschule and Hauptschule KC, Gesellschaftslehre as an integrated subject.

## Rules
- **KC citation.** Sek I: Kompetenzbereich + Kompetenzerwartung (Ende Jg. 9/10 - the Geschichte KC has no Jg. 6 or Jg. 8 stage) + Basisnarrativ (Epochenbezug) + geschichtswissenschaftliche Dimension. Oberstufe: Bildungsstandard with code (`W2`, `A5`, `U6`, `O3`) + `<Kurshalbjahr>.<Nr> <Themenfeld>` + GK or LK. Wording only from `references/sek1.md` / `references/oberstufe.md`; anything else: `check: <KC PDF>`.
- **GK never gets LK-only content** (standards W7, A7-A8, U9-U11, O8-O9 and "erhöhtes Niveau" content). Which Themenfelder are binding beyond the fixed one is set by Erlass per exam year - ask or `check: Abiturerlass`.
- **Every date, name, number and quotation is verified** against an official or scholarly public source and listed under the material ("Daten nach: ..."). Not verifiable → rewrite the task without it, or mark `check:` in the reply. Where sources differ (e.g. vote vs promulgation), give the event the date belongs to ("verkündet am", "unterzeichnet am", "in Kraft seit").
- **Source or Darstellung - always labelled.** Every material is numbered `M1, M2, ...` and headed `Quelle` (from the time) or `Darstellung` (later account). A text written for the task is a Darstellung "verfasst für diese Aufgabe / written for this task" - never dressed up as a historical source, never an invented quotation of a real person.
- **Sources: public domain or own.** Laws, constitutions and other official texts; authors dead for more than 70 years; own descriptions of pictures and cartoons. Full citation: author, title/type, date, place, cited from (edition or official page), cuts marked `[...]`, spelling "originalgetreu" or "modernisiert" stated. Rules: `references/quellenarbeit.md`.
- **Sources stay German** (`data-nur-de`): tasks and explanations get the English line; a word list `Wörter der Quelle` gives DE | EN | Bedeutung for hard source words. A foreign-language source is printed in a cited German translation or, in Bili, in the original.
- **Three steps, three operator groups.** Wiedergeben (AFB I) → einordnen, erläutern, herausarbeiten, vergleichen (AFB II) → beurteilen, bewerten, erörtern (AFB III). Solutions keep them apart: no judgement inside a summary.
- **Sachurteil before Werturteil.** Sachurteil: by the standards and options of the time, with criteria. Werturteil: by today's stated values. Tasks say which is asked; model answers name the criteria; open judgements accept both directions when reasoned.
- **Multiperspektivität and Kontroversität.** A contested topic shows at least two perspectives of the time (sources) or two interpretations (Darstellungen). No single-cause explanations; Anlass, Ursachen, Folgen are separated.
- **Language of the perpetrators is marked.** NS terms and other loaded terms only in quotation marks with an explanation („Machtergreifung“, „Euthanasie“, „Drittes Reich“); terms of the sources are not taken over as descriptions. Preferred wording: `references/begriffe.md`.
- **Sensitive topics** (Shoah, genocide, slavery, colonial violence, war, flight and expulsion): factual, respectful, victims as persons; no role play of perpetrators or victims, no "imagine you are a prisoner" tasks, no gamification, no violent images. No symbols of unconstitutional organisations in figures (check: StGB §§ 86, 86a - described in words instead).
- **Timelines are true to scale** and come from `scripts/zeitleiste.py`; a broken axis is marked. Every date in an animation equals worksheet and solution.
- **Periods and labels are constructs.** Epoch names and borders are introduced as conventions (KC: Konstruktcharakter); from Jg. 9 the task or solution says so where it matters.

## Process (fixed)
1. **Setup** - the base's questions (one AskUserQuestion prompt, max 4, recommended first), with these subject options:
   - Jahrgang/Kurs: Sek I Jahrgang, or E / Q1-Q4 with GK or LK.
   - Thema: 3 topics from the Basisnarrative (Sek I) or the Themenfeld (Oberstufe) of that level.
   - Material: Textquelle, gemeinfrei (Recommended) · Karikatur/Bildquelle as description · Statistik · Darstellung written for the task · user's own source.
   - Second prompt only if still open: Sprache, Zeit, Differenzierung (base defaults). Leitfrage is proposed, not asked, unless the user wants a choice.
2. **Read** `references/sek1.md` or `references/oberstufe.md` for the level; `references/quellenarbeit.md` for source types, analysis steps, citation, judgement, timelines and animation choice; `references/begriffe.md` for glossary and wording; base files as its SKILL.md says.
3. **Plan in 5 lines** (base step 3) plus one line: Leitfrage, materials M1 ... with type and citation, dimension(s), where each date comes from.
4. **Create** each output from the base templates, pair by pair (German line, then its English line). Timeline: `python <skill dir>/scripts/zeitleiste.py START ENDE events.txt --out zeitleiste.svg`, paste inline as a numbered material (`Darstellung`), caption with START, ENDE and "Daten nach"; a task that needs the dates gets the timeline in the worksheet, not only in `animation.html`. Animation: add `--anim` (stage for the base template) and use the printed x positions as steps of `#lauf`. KC reference: printed in a teacher file (Stundenentwurf table, else one line in the header of Lösung or Erwartungshorizont), not only in the reply. Example of a finished set: `references/examples/grundrechte-1849/`.
5. **Self-check every task and answer** - solve each task from the materials alone, without the solution, then compare. Per task tick: every date, name, number and quotation checked against the cited source · quotation exact (wording, paragraph, cuts marked) · source/Darstellung label right · operator and AFB fit · solvable with info box, materials and the lessons before · level (GK/LK, stage) · summary, analysis and judgement separate · Sach- or Werturteil named, criteria in the solution · no anachronism, no single cause · timeline, worksheet and solution show the same dates.
6. **Layout check** - run `python <base skill dir>/scripts/check_material.py unterricht/geschichte/<stufe>/<thema>/`; fix every error, read every `?` line (source texts must carry `data-nur-de`). Then check by eye: source text set off from the tasks with line numbers when a task cites lines, citation directly under the source, answer space fits the expected answer, print preview A4.
7. **Hand over** - reply with files (relative paths), KC reference, sources of texts and dates, every `check:` line used, and offer the review: `darshan-singh-meel-schule-geschichte-review` (optional; recommended for tests and Klausuren).

## References
| File | Read when |
|---|---|
| `references/sek1.md` | Jg. 5-10: Kompetenzbereiche, Kompetenzerwartungen Ende Jg. 9/10, Basiskonzept, Basisnarrative per epoch, 5 Dimensionen, working default per year |
| `references/oberstufe.md` | E, Q1-Q4: Bildungsstandards W/A/U/O with codes (GK, LK), Themenfelder with GK/LK content, binding rules |
| `references/quellenarbeit.md` | source types and analysis steps (Textquelle, Karikatur, Bild, Statistik, Darstellung), citation and copyright, Sachurteil/Werturteil, date checking, typical errors, timelines and animations |
| `references/begriffe.md` | glossary DE \| EN, loaded terms and preferred wording, false friends |
| `references/examples/grundrechte-1849/` | a finished worksheet, solution and timeline animation (Q1 GK, Quellenvergleich 1849/1949) to copy the level of detail from |
| `references/sources.md` | official pages used, what is verified, what is `check:` |
| `scripts/zeitleiste.py` | true-to-scale timeline SVG (`--anim`: animation stage) + x position of every event |
