---
name: darshan-singh-meel-schule-erdkunde
description: Erdkunde / Geographie teaching material for Gymnasium in Hessen - Sek I (Jg. 5-10, Kerncurriculum Erdkunde) and Oberstufe (KCGO Geographie, E, Q1-Q4, GK and LK) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations, climate diagrams and map sketches as generated SVG (no copyrighted maps), material work with source lines, step animations. German text with the closest English sentence under every line, terms DE | EN (Bili option). Use for any request to plan, write or explain Erdkunde or Geographie lessons or material; load darshan-singh-meel-schule alongside. Triggers - "Erdkunde", "Geographie", "Geo LK", "Klimadiagramm", "Kartenarbeit", "Raumanalyse", "Plattentektonik", "Klimazonen", "Bili Erdkunde"; "geography lesson", "geography worksheet", "geography test", "climate diagram", "map skills", "bilingual geography".
---

# Erdkunde / Geographie (Gymnasium Hessen)
Subject side of `darshan-singh-meel-schule` (base). Formats, folders, DE+EN rule, grading, operators, check script → base.

## Scope
- Sek I Jg. 5-10 (KC Erdkunde) → `jg05`…`jg10` · `references/sek1.md`
- E, Q1-Q4 GK/LK (KCGO Geographie) → `e`, `q1-gk`…`q4-lk` · `references/oberstufe.md`
- Out: `unterricht/erdkunde/<stufe>/<thema>/`. Not covered: Grundschule, Realschule/Hauptschule KC, Gesellschaftslehre.

## Rules
- KC cite: Sek I = Kompetenzbereich + Kompetenzerwartung (Ende Jg. 9/10 only) + Inhaltsfeld. Oberstufe = Standard code (`RO1`, `MA4`, `BB3`, `K2`) + `<Halbjahr>.<Nr> <Themenfeld>` + GK/LK. Wording only from refs; else `check: <KC PDF>`.
- GK never gets LK-only content. Q-phase Abitur Themenfelder per Erlass/year → ask or `check: Abiturerlass`.
- Sek I year plan not in KC → ask school Fachcurriculum, or use `sek1.md` default → KC line marks it as proposal.
- Every task: Raum · Maßstabsebene (lokal/regional/national/global) · data year.
- Material `M1…`: title · source line with year · named in its task. No material → operator says so (nennen, beschreiben).
- Data: official source with station/area, period, source line, or marked "erfundene Daten / invented data". Never real values from memory. Sources → `fachpraxis.md`.
- Maps: own SVG only (Kartenskizze, Lageskizze, Profil, Schema) · title · legend · scale bar or "nicht maßstabsgetreu / not to scale" · north arrow (unless graticule) · source line. No atlas scans, screenshots, traced maps.
- Climate diagrams only via `scripts/klimadiagramm.py` (Walter/Lieth, 10 °C = 20 mm); worksheet, solution, SVG share one input.
- AFB I → II → III: beschreiben/lokalisieren → erklären/analysieren → beurteilen/bewerten. No cause in a description.
- Beurteilen = subject criteria · bewerten = stated values/norms (BB1, BB2). Sustainability = Ökologie · Ökonomie · Soziales · Politik.
- No determinism, no stereotypes; no one-deficit regions; terms per `begriffe.md` (`Länder des Globalen Südens` + indicator + year).
- Every model/animation labelled "Modell"; from Jg. 9 name one limit.
- Names/borders per Auswärtiges Amt / UN; disputed = dashed + labelled. English exonyms only if established.

## Process
1. Setup → base questions, one AskUserQuestion (max 4, rec first):
   - Jahrgang/Kurs · Thema (3 from Inhaltsfeld/Themenfeld)
   - Material: Klimadiagramm aus amtlichen Werten (rec if climate) · Kartenskizze · Statistik/Diagramm · Text/Karikatur
   - 2nd prompt only if open: Sprache, Zeit, Differenzierung. Raumbeispiel only if KC leaves it open and none named.
2. Read level ref · `fachpraxis.md` · `begriffe.md` · base files per base SKILL.md.
3. Plan 5 lines (base step 3) + Raum, Maßstab, M1… with source, Basiskonzept.
4. Create from base templates, DE line → EN line. Climate: `python <skill dir>/scripts/klimadiagramm.py NAME HOEHE T1..T12 N1..N12 --out m1.svg` → SVG inline, key values into solution. KC ref in a teacher file. Example: `references/examples/klimadiagramm-frankfurt/`.
5. Self-check: solve from material only, then compare. Per task: fact/number recomputed · place, scale, year named · operator/AFB · solvable from info box + material + prior lessons · level · description ≠ explanation · readings possible at print size · figure, table, solution, animation agree.
6. Layout: `python <base skill dir>/scripts/check_material.py unterricht/erdkunde/<stufe>/<thema>/` → fix errors, read `?`. By eye: labels ≥10 pt print · legend complete · no colour-only coding · answer space fits · A4 preview.
7. Hand over: files (relative) · KC ref · data sources · every `check:` · offer `darshan-singh-meel-schule-erdkunde-review` (rec for tests/Klausuren).

## References
- `references/sek1.md` · Jg. 5-10: Kompetenzbereiche, Erwartungen, 6 Inhaltsfelder, default per year
- `references/oberstufe.md` · E, Q1-Q4: RO/MA/BB/K codes, Basiskonzepte, Themenfelder GK/LK
- `references/fachpraxis.md` · material types, map and climate rules, data sources, calculations, student errors, animation choice
- `references/begriffe.md` · glossary DE | EN, false friends, wording to avoid
- `references/examples/klimadiagramm-frankfurt/` · finished Jg. 7 set
- `references/sources.md` · official pages, verified vs `check:`
- `scripts/klimadiagramm.py` · SVG + key values
