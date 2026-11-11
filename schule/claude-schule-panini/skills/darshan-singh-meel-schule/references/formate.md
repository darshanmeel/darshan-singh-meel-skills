# Output formats

One template per output in `templates/`. Copy the template, fill it, keep its CSS, script and `data-*` attributes. `scripts/check_material.py` reads the attributes.

## All files
- Self-contained: inline `<style>`, inline `<script>`, inline SVG; images only as `data:` URIs; no links to load anything. Opens offline by double-click.
- `<html lang="de">`, one `<h1>`, `<title>` = type + topic, tables with `<th scope>`.
- Print: A4, 15 mm margins, black on white, 11 pt (Grundschule 14 pt: `<body class="gs">`), no element wider than the page, tasks and table rows do not split across pages.
- Accessibility: text contrast at least 4.5:1; nothing coded by colour alone (add label, pattern or symbol); every SVG has `aria-label` (German / English) or `<title>`; every `<img>` has `alt`; controls reachable by keyboard, at least 44 px high; no text below 10 pt in print.
- No school, teacher or student names. Header fields (`Name`, `Klasse`, `Datum`) stay blank lines.
- Replace every `{{PLATZHALTER}}`; delete unused blocks; delete the template comments you no longer need.

## DE/EN markup
| Case | Markup |
|---|---|
| Sentence or paragraph | `<div class="bi"><p>Deutsch.</p><p class="en" lang="en">English.</p></div>` |
| Inside a table cell, list item, heading, caption | `<span class="bi"><span>Deutsch</span><span class="en" lang="en">English</span></span>` |
| Short label | `Aufgabe 1 <span class="en" lang="en">/ Task 1</span>` |
| German only (text under analysis, DaF text, glossary DE column) | add `data-nur-de` to the block; no `.en` |
| Formula, number, name | plain, no pair |

- A `.bi` has exactly two children: German first, English second. One pair per sentence group of at most 2-3 sentences; long paragraphs are split into several pairs so each English line sits under its German line.
- Toolbar (in every template, hidden in print): `Englisch anzeigen / Show English` (`#en-toggle`, on by default) · `nebeneinander / side by side` (`#neben-toggle`, block pairs in two columns on screens from 700 px) · `Drucken / Print`. Print shows what the screen shows: toggle off → German only.
- `body data-sprache`: `de-en` (default) · `de` (remove `.en` elements and the toggle) · `en` (file `<name>.en.html`, `<html lang="en">`).
- Closeness of the English line: `bilingual.md`.

## stundenentwurf.html (teacher)
| Block | Must contain |
|---|---|
| Kopf | Fach, Jahrgang/Kurs, Schulform, Dauer |
| Bezug zum Kerncurriculum | 4 rows as in `hessen.md`; wording as printed in the KC |
| Lernziele | one Stundenziel (observable: "Die Lernenden ..." + operator verb); 2-4 Teilziele, each with AFB and Kompetenzbereich |
| Lernvoraussetzungen | what the class already knows and can do; which earlier lesson it builds on |
| Verlaufsplan | Einstieg · Erarbeitung · Sicherung · Transfer · Abschluss; per phase: minutes, what teacher and learners do, Sozialform (EA, PA, GA, UG, LV), media/material. `data-min` per row adds up to `data-dauer` (45 or 90) |
| Differenzierung | Basis · Standard · Herausforderung · Sprache/Inklusion (`differenzierung.md`) |
| Sicherung | the Tafelbild or Merksatz exactly as it should stand in the exercise book |
| Hausaufgabe | task + minutes; "keine" is allowed and written out |
| Fachbegriffe | 5-10 terms `DE | EN | Bedeutung` |
| Material | files of the folder that the lesson uses |

- Time: Einstieg at most 10 % of the lesson; Erarbeitung the largest block; Sicherung never dropped; 2-3 min buffer inside Transfer or Abschluss. 90 min: two Erarbeitung/Sicherung rounds.
- Every Teilziel is visible in a phase and in a task of the worksheet.

## arbeitsblatt.html + loesung.html
- Info box first: what is needed (formula, rule, material) in at most 4 lines.
- Tasks in three levels, marked ★ Basis (AFB I), ★★ Standard (AFB I-II), ★★★ Herausforderung (AFB II-III). Each task: `data-aufgabe`, `data-niveau`, `data-afb`, one operator, one answer space.
- Answer space sized for the expected answer in the students' handwriting: `.zeile` (9 mm; Grundschule 12 mm) for text - one line per expected 8-10 words; `.karo` (5 mm squares, set `height`) for calculations and drawings.
- 45 min lesson: 15-20 min of worksheet time → about 3-5 tasks. Standard-level students finish ★ and ★★.
- Lösung: one section per task with the same `data-aufgabe`: result (with unit), solution steps a student can follow, typical mistake. Open tasks: criteria plus one model answer.
- Glossary at the end.

## test.html + erwartungshorizont.html
- Header: type (Klassenarbeit, Lernkontrolle, Klausur), working time, permitted aids, total points (`data-gesamt`).
- Every part: `data-aufgabe`, `data-punkte`, `data-afb`, operator, points printed at the right, one answer space. Material (text, table, figure) stands before the tasks that use it.
- Order: easy to hard inside a task; AFB mix and legal rules: `bewertung.md`. Working time check: a prepared teacher needs about one third of the students' time.
- Erwartungshorizont: per part the expected result, steps and how the points split; AFB; points. Rows match the test (`data-aufgabe`, `data-punkte`, `data-afb` identical). Sum row = `data-gesamt` = total on the test.
- AFB table: points and share per AFB; shares add up to 100 %.
- Grade key: Sek I rows 1-6 (school key or default), Oberstufe rows 15-0 (OAVO Anlage 9a); `data-ab` = lowest points for the grade, falling strictly, last row 0; name the source of the key under the table.
- Hinweise zur Korrektur: Folgefehler, other correct ways, language/form rule for the level.
- The test never shows AFB labels or solutions; the Erwartungshorizont is marked "nur für Lehrkräfte".

## erklaerung.html (student)
- Order: Darum geht es (1-2 sentences) → figure → Schritt für Schritt (3-6 steps) → Beispiel (worked, with numbers) → Merke → Typische Fehler (wrong · right · why) → Probier es selbst (2-3 tasks, short solutions) → Fachbegriffe.
- Language by age: Grundschule sentences up to about 10 words, one idea each, no nominal chains; Jg. 5-6 up to about 15; Oberstufe: subject language, defined on first use.
- One figure that carries the idea, labelled inside the picture. One example that could be an exam task.
- One page A4 where possible; two at most.

## animation.html
Use only when change over time, movement, a construction or a step sequence is the point. Otherwise a figure in `erklaerung.html`.

| Part | Rule |
|---|---|
| Stage | one inline `<svg id="buehne" viewBox role="img" aria-label>`; every part that changes has an `id`; text in the picture at least 16 units high |
| Steps | `STEPS` list in the script: per step `de` caption, `en` caption (closest sentence), `set` = attribute changes; steps are cumulative; 4-8 steps; one idea per step |
| Controls | Zurück/Back, Start/Pause, Weiter/Next, step counter, Tempo/Speed (0.5×, 1×, 2×); keys ←, →, space |
| Captions | German and English under the stage (`#cap-de`, `#cap-en`), announced to screen readers; English follows the toggle |
| Reduced motion | `prefers-reduced-motion`: steps switch without transition; a note says so |
| Print | the script builds one still picture per step with both captions (`#bilder`), one per row (two per row print the labels in the picture below 10 pt); player hidden |
| No script | start picture plus a note |

- The engine tweens numbers inside SVG attribute values (`cx`, `opacity`, `stroke-dashoffset`, `transform`, `d` with the same shape). Draw a line: `pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"` → `0`.
- No autoplay, no sound, no flashing; a step lasts at least 1.8 s at normal speed.
- Content first: every number, label and end state in the animation equals the worksheet and the explanation.
- Do not rewrite the engine; change the SVG, `STEPS`, `DAUER`, `HALT`.

## Check
`python <skill dir>/scripts/check_material.py <folder>` → fix all `FAIL` lines; read all `?` lines (German text without an English line: add the pair, or mark `data-nur-de` when it must stay German). `--template` allows `{{...}}`.
