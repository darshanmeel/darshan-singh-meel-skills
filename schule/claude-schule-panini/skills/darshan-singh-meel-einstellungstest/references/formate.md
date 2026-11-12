# Formats

Default format: JSON is the source, sheets are printed from it. Base templates, CSS, toolbar, DE/EN markup and print rules stay as in `darshan-singh-meel-schule`; blocks to add: `templates/bloecke.html`.

## Folder
```
unterricht/einstellungstest/
  <modul>/<thema>/            practice: one topic
    kapitel.json  fragen.json
    en/kapitel.json  en/fragen.json
    arbeitsblatt.html  loesung.html
  probetest/<slug>/           mock test, mixed areas
    fragen.json  en/fragen.json  profil.json (target only)
    test.html  erwartungshorizont.html
```
- `<modul>`: the `module` value (`mathe`, `logik`, `deutsch`, …; `bereiche.md`). `<thema>`: ASCII slug (`prozent`, `zahlenreihen`).
- `<slug>`: `allgemein-01`, or the target (`bankkaufmann-01`; an employer's name only when the user named it).
- Pairs always together: `arbeitsblatt` + `loesung`, `test` + `erwartungshorizont`, every German JSON + its `en/` sidecar of the same name.
- Reviews: `reviews/` (base rule).

## Question (`fragen.json`: a list)
```json
{"id": "ma-pro-003", "module": "mathe", "topic": "Prozentrechnung", "difficulty": 1,
 "question": "…", "options": ["12 €", "65 €", "68 €", "92 €"], "answer": 2,
 "explanation": "Way. Typischer Fehler: … Trick: …", "time_seconds": 40, "check": "80 * (100 - 15) / 100"}
```
| Key | Rule |
|---|---|
| `id` | unique across all files; one prefix per file (`ma-pro-`), then a running number; a prefix is used in one file only |
| `module`, `topic` | `bereiche.md`; `topic` = the `topic` of a chapter, letter for letter |
| `difficulty` | 1, 2, 3 |
| `options` | exactly 4 strings |
| `answer` | 0-based index of the correct option; `-1` only for `persoenlichkeit` and `sjt` |
| `explanation` | `aufgabenbau.md`; for `-1` items `persoenlichkeit-sjt.md` |
| `time_seconds` | whole seconds, 5-600 |

Optional keys (only when needed):
| Key | Use |
|---|---|
| `check` | expression that recomputes the result (`aufgabenbau.md`) |
| `material` | text shown before the question: Textverständnis text, Merkfähigkeit material, Postkorb messages, Konzentration pairs (one pair per line, `left   |   right`; sheets print them as a two-column table in a monospace font). Items of one group carry the identical string |
| `figure` | one inline `<svg viewBox role="img" aria-label="Deutsch / English">` for Matrizen, Raumvorstellung, Würfel, Diagramme: black on white, nothing by colour alone, labels as letters or numbers, no `xmlns` attribute, no external reference. Options name labelled parts (`Figur B`) |

## Chapter (`kapitel.json`: a list)
```json
{"id": "les-ma-pro-01", "module": "mathe", "topic": "Prozentrechnung", "title": "…", "concept": "…", "example": "…",
 "example_explained": "…", "tips": ["…", "…", "…", "…"], "traps": ["X ist Y, nicht Z.", "…"], "practice_topics": ["Prozentrechnung"]}
```
`tips` 4-6, `traps` 2-4. Paragraphs inside a string: `\n\n`; lines of an example: `\n`. Content rules: `aufgabenbau.md`.

## English sidecar (`en/<same name>.json`: an object by id)
```json
{"ma-pro-003": {"question": "…", "options": ["€12", "€65", "€68", "€92"], "explanation": "… Typical mistake: … Trick: …"}}
{"les-ma-pro-01": {"title": "…", "concept": "…", "example": "…", "example_explained": "…", "tips": ["…"], "traps": ["…"]}}
```
- Every id of the German file, no other id; the same number of options, tips and traps, in the same order. `material` is added when the question has one.
- Closeness: base `bilingual.md` (same meaning, numbers, sentence count; English number form `€1,250.50`, `33.3%`).
- Text that is the test object stays as it is: German spelling, grammar and comprehension texts and their options; English items. The sidecar then repeats the string and translates only the instruction part and the explanation.
- `figure` and `check` are not repeated.

## Practice sheet: `arbeitsblatt.html` + `loesung.html`
- Base templates; header `Einstellungstest-Training · <Bereich>`, fields Name and Datum only.
- Meta line: number of questions, time (sum of `time_seconds`, rounded up to minutes), the stars ★ ★★ ★★★ = difficulty 1, 2, 3 (`data-niveau` basis, standard, herausforderung; `data-afb` I, II, III - a working aid for the base check script, not a statement about the test).
- Info box "Das brauchst du": how to answer (circle the letter), aids (pen and paper; calculator only if the items allow it), the rule or formula of the topic in at most 2 lines.
- Each question: `<section class="aufgabe" data-aufgabe="n" data-frage="<id>" …>` → heading with number, stars, seconds → `material` and `figure` when present → stem pair → options `(A)`-`(D)` in JSON order (`data-option`). No answer lines: the answer is a letter (replaces the base rule "one answer space per task").
- Options that are numbers stand alone; word and sentence options get the pair, German first. German-only test objects: `data-nur-de`.
- `loesung.html`: key line (`1A · 2D · …`); per question the same `data-aufgabe` and `data-frage` plus `data-loesung`; line "Lösung: (C) 68 €"; the explanation split into its three parts as pairs. Unkeyed items: `data-loesung="-"` and the explanation.
- Glossary (5-8 terms) and the footer block at the end of both files.

## Mock test: `test.html` + `erwartungshorizont.html`
| Block | Content |
|---|---|
| Meta line | "Probetest", working time, aids, total `data-gesamt` = number of keyed questions (1 point each) |
| Regeln | one of four answers is correct; letter into the answer sheet; work section by section, each with its own time; whether going back is allowed (default: not across sections) |
| Sections | one per area, in the order of `profil.json` or the general mix (`bereiche.md`); heading with number of questions and minutes; each question a `.teil` with `data-aufgabe`, `data-frage`, `data-punkte="1"`, `data-afb` |
| Unscored part | Persönlichkeit and SJT last, untimed, without `data-punkte` |
| Antwortzettel | last page: one cell per question (`data-antwort`), grouped by section |

Answer key (`erwartungshorizont.html`; replace the header text "nur für Lehrkräfte" by "Lösungsbogen · erst nach dem Test öffnen / Answer key · open only after the test"):
| Block | Content |
|---|---|
| Lösungsbuchstaben | one line per section |
| Table | per question: letter and value, explanation, difficulty, 1 point; rows carry `data-frage`, `data-loesung`, `data-punkte`, `data-afb`; sum row `data-gesamt` |
| Auswertung | table per area: questions · correct · percent; fields to fill in; then "Schwächster Bereich zuerst üben" |
| AFB table | points per difficulty, with the sentence that I/II/III stands for difficulty 1/2/3 and is a working aid |
| Fehlerarten | four boxes to tally wrong answers: verrechnet/Flüchtigkeit · nicht gewusst · Zeit zu knapp · falsch gelesen |

- Size: short 24 questions (about 20 min) · standard 40-50 (about 45 min) · full as in the profile.
- Questions per section = weight × size. Section time = sum of `time_seconds`, rounded up to full minutes; only the full size uses the profile's minutes. A short or standard test of a target says "Kurzfassung" and the real total time (or "unbekannt") in the meta line.
- No grade key and no pass mark: employers do not publish cut-offs on the pages read. The result is percent per area. Delete the grade-key section of the template.
- No deduction for wrong answers; the rules box says that a real test may deduct and that its instructions say so.

## `profil.json` (job C only)
```json
{"key": "bankkaufmann", "target": "Ausbildung Bankkaufmann/-frau", "target_en": "…", "total_minutes": null,
 "sections": [{"name": "…", "name_en": "…", "module": "mathe", "topics": ["…"], "questions": null, "minutes": null, "weight": 25, "how": "…", "how_en": "…"}],
 "sources": ["<name of an official page read>"], "unverified": ["check: <page> - …"]}
```
- `weight` in percent, sum 100. `how`: what the task looks like and how it is answered, one sentence. `name_en`: the section heading's English line.
- `questions`, `minutes`, `total_minutes`: only when a page read states them; else `null` and a line in `unverified`.
- `unverified` lines state the open point as a fact about the test (`check: <page> - Dauer je Teil nicht angegeben`), never as a note to or about the requester.
- `sources`: page names (and plain URLs without parameters) actually read. No personal data (`SKILL.md`, Rules).

## Checks
1. `python <this skill dir>/scripts/check_items.py <folder>` - JSON, sidecars, `check`, sheets against JSON.
2. `python <base skill dir>/scripts/check_material.py <folder>` - HTML form, DE/EN pairs, points = total, test = key file.
3. Not checked by a script: whether an item without `check` is right, option texts of figures, level, wording, print length - process A step 8 and the review skill.
