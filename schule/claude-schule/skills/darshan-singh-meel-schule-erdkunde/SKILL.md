---
name: darshan-singh-meel-schule-erdkunde
description: Erdkunde / Geographie teaching material for Gymnasium in Hessen - Sek I (Jg. 5-10, Kerncurriculum Erdkunde) and Oberstufe (KCGO Geographie, E, Q1-Q4, GK and LK) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations, climate diagrams and map sketches as generated SVG (no copyrighted maps), material work with source lines, step animations. German text with the closest English sentence under every line, terms DE | EN (Bili option). Use for any request to plan, write or explain Erdkunde or Geographie lessons or material; load darshan-singh-meel-schule alongside. Triggers - "Erdkunde", "Geographie", "Geo LK", "Klimadiagramm", "Kartenarbeit", "Raumanalyse", "Plattentektonik", "Klimazonen", "Bili Erdkunde"; "geography lesson", "geography worksheet", "geography test", "climate diagram", "map skills", "bilingual geography".
---

# Erdkunde / Geographie (Gymnasium Hessen, Sek I and Oberstufe)

Adds the subject side to `darshan-singh-meel-schule` (base): KC content, material and map rules, climate diagrams, terms, animations. Formats, folders, the German + English rule, grading, operators and the check script are the base's - not repeated here.

## Scope
| Level | Subject name in the KC | Folder `<stufe>` | Reference |
|---|---|---|---|
| Sek I, Jg. 5-10 | Erdkunde | `jg05` ... `jg10` | `references/sek1.md` |
| Einführungsphase | Geographie | `e` | `references/oberstufe.md` |
| Q1-Q4, GK or LK | Geographie | `q1-gk` ... `q4-lk` | `references/oberstufe.md` |

Output folder: `unterricht/erdkunde/<stufe>/<thema>/` (also for Oberstufe). Not covered: Grundschule (Sachunterricht), Realschule and Hauptschule KC, Gesellschaftslehre as an integrated subject.

## Rules
- **KC citation.** Sek I: Kompetenzbereich + Kompetenzerwartung (Ende Jg. 9/10 - the Erdkunde KC has no Jg. 6 or Jg. 8 stage) + Inhaltsfeld. Oberstufe: Bildungsstandard with code (`RO1`, `MA4`, `BB3`, `K2`) + `<Kurshalbjahr>.<Nr> <Themenfeld>` + GK or LK. Wording only from `references/sek1.md` / `references/oberstufe.md`; anything else: `check: <KC PDF>`.
- **GK never gets LK-only content** (erhöhtes Niveau). Q-phase: which Themenfelder beyond 1 and 2 count for the Abitur is set by Erlass per exam year - ask or `check: Abiturerlass`.
- **Sek I has no year-by-year plan** in the KC. The year comes from the school's Fachcurriculum: ask, or use the working default in `sek1.md` and say so.
- **A place, a scale, a date.** Every task names the Raum (place or region), the Maßstabsebene (lokal, regional, national, global) and the year of its data. No "in Afrika" for a fact that holds for one country.
- **Material carries the task.** Every map, diagram, table, text, photo description and cartoon is numbered `M1, M2, ...`, has a title, a source line with year, and is named in the task that uses it. A task that needs no material says so by its operator (nennen, beschreiben from memory).
- **Real numbers or marked ones.** Data come from an official source with station/area, period and source line, or are marked "erfundene Daten / invented data". Never estimate real values from memory. Sources: `references/fachpraxis.md`.
- **Maps: drawn, not copied.** Only own SVG: Kartenskizze, Lageskizze, Profil, Schema. Every map has title, legend, scale bar or "nicht maßstabsgetreu / not to scale", north arrow (unless a graticule shows north), source line. No atlas scans, no screenshots of map services, no traced textbook maps.
- **Climate diagrams only from the script** `scripts/klimadiagramm.py` (Walter/Lieth school form, fixed scale 10 °C = 20 mm). Values in the worksheet, the solution and the SVG come from the same input.
- **Describe before explain before judge.** Material tasks run AFB I → II → III: beschreiben / lokalisieren → erklären / analysieren → beurteilen / bewerten. Solutions never put a cause into a description.
- **Judgements name criteria.** Beurteilen = by subject criteria; bewerten = by stated values and norms (KCGO BB1, BB2). Sustainability judgements use the four dimensions Ökologie, Ökonomie, Soziales, Politik (KCGO: 4 + 2 model).
- **No natural determinism, no stereotypes.** Nature limits and enables, people decide. Regions are never described by one deficit ("arm", "rückständig"); terms as in `references/begriffe.md` (e.g. `Länder des Globalen Südens`, country groups with indicator and year).
- **Model is not reality.** Every model and animation (Plattentektonik, Stadtmodell, demographischer Übergang, Zirkulation) is labelled as a model; from Jg. 9 one limit is named.
- **Borders and names.** State names and borders as used by the Auswärtiges Amt / United Nations; disputed areas drawn dashed and labelled as disputed. English place names only where an established exonym exists.

## Process (fixed)
1. **Setup** - the base's questions (one AskUserQuestion prompt, max 4, recommended first), with these subject options:
   - Jahrgang/Kurs: Sek I Jahrgang, or E / Q1-Q4 with GK or LK.
   - Thema: 3 topics from the Inhaltsfeld (Sek I) or Themenfeld (Oberstufe) of that level.
   - Material: Klimadiagramm aus amtlichen Werten (Recommended when climate is the topic) · Kartenskizze · Statistik/Diagramm · Text or Karikaturbeschreibung.
   - Second prompt only if still open: Sprache, Zeit, Differenzierung (base defaults). Raumbeispiel is asked only when the KC leaves it open and the user named none.
2. **Read** `references/sek1.md` or `references/oberstufe.md` for the level; `references/fachpraxis.md` for material, maps, climate diagrams, typical errors and animation choice; `references/begriffe.md` for the glossary; base files as its SKILL.md says.
3. **Plan in 5 lines** (base step 3) plus one line: Raum, Maßstabsebene, materials M1 ... with source, Basiskonzept in focus.
4. **Create** each output from the base templates, pair by pair (German line, then its English line). Climate diagram: `python <skill dir>/scripts/klimadiagramm.py NAME HOEHE T1,...,T12 N1,...,N12 --out m1.svg`, paste the SVG inline, copy the printed key values into the solution. KC reference: printed in a teacher file (Stundenentwurf table, else one line in the header of Lösung or Erwartungshorizont), not only in the reply. Example of a finished set: `references/examples/klimadiagramm-frankfurt/`.
5. **Self-check every task and answer** - solve each task from the material alone, without the solution, then compare. Per task tick: fact and number correct (recomputed) · place, scale level and year named · operator and AFB fit · solvable with the info box, the materials and the lessons before · level (GK/LK, stage) · description and explanation separate · every reading can really be read off the figure at print size · figure, table, solution and animation show the same values.
6. **Layout check** - run `python <base skill dir>/scripts/check_material.py unterricht/erdkunde/<stufe>/<thema>/`; fix every error, read every `?` line. Then check by eye: map and diagram labels at least 10 pt in print, legend complete, nothing coded by colour alone (pattern, symbol or label), answer space fits the expected answer, print preview A4.
7. **Hand over** - reply with files (relative paths), KC reference, data sources, every `check:` line used, and offer the review: `darshan-singh-meel-schule-erdkunde-review` (optional; recommended for tests and Klausuren).

## References
| File | Read when |
|---|---|
| `references/sek1.md` | Jg. 5-10: Kompetenzbereiche, Kompetenzerwartungen Ende Jg. 9/10, inhaltliche Konzepte, 6 Inhaltsfelder, regional rule, working default per year |
| `references/oberstufe.md` | E, Q1-Q4: Bildungsstandards RO/MA/BB/K with codes, Basiskonzepte, Themenfelder with GK/LK content, binding rules |
| `references/fachpraxis.md` | material types and their analysis steps, map rules, climate diagram rules and script, data sources, calculations, typical student errors, which animation for which process |
| `references/begriffe.md` | glossary DE \| EN per field; false friends; wording to avoid |
| `references/examples/klimadiagramm-frankfurt/` | a finished worksheet and solution (Jg. 7, climate diagram from DWD values) to copy the level of detail from |
| `references/sources.md` | official pages used, what is verified, what is `check:` |
| `scripts/klimadiagramm.py` | climate diagram SVG + key values (annual mean, sum, range, arid months) |
