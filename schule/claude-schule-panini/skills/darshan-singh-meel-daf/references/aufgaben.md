# Tasks, outputs and conventions for DaF/DaZ

Base formats: `darshan-singh-meel-schule/references/formate.md`. This file says what changes for language teaching.

## Instruction verbs (the operators of DaF)
One verb per task, first word, in bold (`class="op"`). Adults: Sie-form. Teens: du-form (`Lies`, `Kreuze an`, `Ergänze`, `Ordne zu`, `Schreib`, `Sprich`). English line: the verb in the EN column, same position.

| From | Sie-form | English line | AFB |
|---|---|---|---|
| A1 | Lesen Sie | Read | I |
| A1 | Hören Sie | Listen to | I |
| A1 | Kreuzen Sie an | Tick | I |
| A1 | Ordnen Sie zu | Match | I |
| A1 | Ergänzen Sie | Fill in (a gap, a word, a form) / Complete (a sentence, text, table) | I-II |
| A1 | Markieren Sie / Unterstreichen Sie | Mark / Underline | I |
| A1 | Schreiben Sie | Write | II-III |
| A1 | Antworten Sie | Answer | II |
| A1 | Fragen Sie / Sprechen Sie | Ask / Speak | II-III |
| A1 | Buchstabieren Sie | Spell | I |
| A2 | Bilden Sie Sätze | Form sentences | II |
| A2 | Verbinden Sie | Connect | II |
| A2 | Korrigieren Sie | Correct | II |
| A2 | Berichten Sie / Erzählen Sie | Report / Tell | III |
| A2 | Spielen Sie das Gespräch | Act out the conversation | III |
| B1 | Formen Sie um | Transform | II |
| B1 | Fassen Sie zusammen | Summarise | II-III |
| B1 | Begründen Sie | Give reasons for | III |
| B1 | Vergleichen Sie | Compare | II-III |
| B1 | Notieren Sie | Note down | II |
| B2 | Nehmen Sie Stellung | Give your opinion on | III |
| B2 | Erläutern Sie | Explain with examples | III |
| B2 | Beschreiben Sie (die Grafik) | Describe (the chart) | II-III |
| B2 | Diskutieren Sie | Discuss | III |
| C1 | Erörtern Sie | Discuss in depth | III |
| C1 | Geben Sie wieder | Report (what was said) | II-III |

- Instructions at A1-A2: at most 8 words per sentence, one action per sentence, an example item (`Beispiel: 0`) before the first item of every closed task.
- State the form of the answer: `in ganzen Sätzen`, `circa 40 Wörter`, `zu jedem Punkt ein bis zwei Sätze`.

## Task types per skill
| Skill | Closed (I) | Guided (II) | Open (III) |
|---|---|---|---|
| Lesen | richtig/falsch, Multiple Choice (a-c), Zuordnung (Überschrift, Anzeige ↔ Person) | W-Fragen in Stichworten, Tabelle ausfüllen | Text weitergeben, Meinung zum Text |
| Hören | richtig/falsch, Multiple Choice, Bild oder Notiz zuordnen | Notizzettel, Telefonnotiz ergänzen | Gehörtes weitergeben |
| Wortschatz | zuordnen (Wort ↔ Bild, Wort ↔ Erklärung), Wortkasten-Lücke, was passt nicht | Wortfamilie, Kollokation ergänzen | eigene Sätze |
| Grammatik | Form markieren, Lücke mit Vorgabe, Sätze ordnen (Satzbau-Karten) | Lücke frei, Sätze verbinden, umformen | freie Sätze zur Situation |
| Schreiben | Formular | Text nach Muster, Antwort auf E-Mail mit 3 Leitpunkten | freier Text der Textsorte |
| Sprechen | Nachsprechen, Dialog lesen | Dialog mit Rollenkarten und Redemitteln | freies Gespräch, Vortrag, Diskussion |
| Mediation | - | Information aus Text/Anruf als Notiz weitergeben | Inhalt für eine bestimmte Person aufbereiten |

- Multiple choice: one clearly right option; distractors are true to the level and wrong only against the text, never trick grammar.
- Richtig/falsch items follow the text order; no item is answerable without the text; no "nicht im Text" option below B1.
- Gap items: exactly one gap per decision; context before and after the gap; the answer is not given by another item.
- Order in every lesson and worksheet: understand → notice → practise closed → practise guided → use freely.

## DaF version of each output
| Output | What changes against the base format |
|---|---|
| `stundenentwurf.html` | KC table → GER table (`niveaus.md`); Stundenziel = Kann-Beschreibung; phases keep their names: Einstieg (situation, picture, question) · Erarbeitung (text, then noticing the structure) · Sicherung (rule or Redemittel on the board) · Transfer (role play, own text) · Abschluss; speaking time of learners at least half of the lesson; Tafelbild German only (`data-nur-de`) with English line for the rule sentence up to B1; Fachbegriffe table = glossary of new words |
| `arbeitsblatt.html` | info box "Das brauchen Sie" = Redemittel or rule (German, `data-nur-de`) with one English help line under the heading; tasks ★ with Wortkasten or model · ★★ without help · ★★★ free use in the situation; each `<h2>` names the skill: `Aufgabe 1 · Lesen`; texts and dialogues in `<div class="quelltext" data-nur-de>`; glossary at the end |
| `loesung.html` | answers German only (`data-nur-de`); "Lösungsweg" = why (rule in one sentence, with English line); "Typischer Fehler" = wrong form, right form (German only) and reason (with English line); open tasks: criteria + Musterlösung at level; Hörtext zum Vorlesen for Hören tasks |
| `test.html` | header: Lernkontrolle or Prüfungstraining (exam, version date); parts named by skill; no English on items; English line on instructions as the level allows (`niveaus.md`); in Prüfungstraining instructions German only if the exam is German only - say so |
| `erwartungshorizont.html` | key per item; accepted variants; rubric for Schreiben/Sprechen with model answer; Hörtext; AFB table; Prädikat table (`bewertung.md`); notes: spelling rule, Folgefehler (a wrong article does not cost the point of the verb form) |
| `erklaerung.html` | one structure or Sprachhandlung; order of the base; figure = sentence diagram or table of forms; example sentences German only; rule and "Warum" with English line; contrast with English in one line where it prevents an error |
| `animation.html` | see below |
| `wortschatz.html`, `bewertungsraster.html` | `wortschatz.md`, `bewertung.md` |

- Headings that are fixed in the templates (`Das brauchst du`) are changed to the Sie-form for adults (`Das brauchen Sie / This is what you need`).
- `data-nur-de` on: `.quelltext`, example-sentence paragraphs and list items, table cells with German forms, model answers, Redemittel lists, the Tafelbild block. The check script then expects no English there.
- Names in dialogues: invented first names from different languages plus neutral surnames; firms invented (`Firma Lindner`). Below B1 keep `Herr` + name out of the accusative and dative (`Herrn` is n-Deklination): write `Frau Petrova ruft in der Bäckerei an`, not `... ruft Herrn Brandt an`.
- Print layout: `test.html` - the Bewertung box stands right under the header, not alone on a last page · `erwartungshorizont.html` - table of expected performance first, Hörtext after it (a table split across pages prints its sum row on each page) · figure labels end inside the `viewBox` (long `DE / EN` labels: `text-anchor="end"` at the right edge).

## Grammar terms DE | EN
| Deutsch | English |
|---|---|
| das Nomen, der Artikel | noun, article |
| das Verb, der Infinitiv, das Partizip II | verb, infinitive, past participle |
| das trennbare Verb | separable verb |
| das Modalverb | modal verb |
| der Hauptsatz, der Nebensatz | main clause, subordinate clause |
| die Konjunktion / der Konnektor | conjunction / connector |
| das Subjekt, das Objekt | subject, object |
| der Nominativ, Akkusativ, Dativ, Genitiv | nominative, accusative, dative, genitive |
| die Satzklammer | sentence bracket |
| das Präsens, das Perfekt, das Präteritum | present tense, perfect tense, simple past |
| der Konjunktiv II | subjunctive II |
| das Passiv | passive |
| die Präposition | preposition |
| der Relativsatz | relative clause |

## Typical learner errors (use for distractors and the "Typischer Fehler" lines)
| Area | Error | Right |
|---|---|---|
| Verbposition | `Heute ich arbeite nicht.` | `Heute arbeite ich nicht.` |
| Nebensatz | `..., weil ich bin krank.` | `..., weil ich krank bin.` |
| Satzklammer | `Ich rufe an Sie morgen.` | `Ich rufe Sie morgen an.` |
| Perfekt | `Ich habe gegangen.` | `Ich bin gegangen.` |
| Artikel, Kasus | `mit der Chef` | `mit dem Chef` |
| Negation | `Ich habe nicht Zeit.` | `Ich habe keine Zeit.` |
| English transfer | `Ich bin 30 Jahre.` · `Ich will ein Arzt werden.` · `seit zwei Jahre` | `Ich bin 30 Jahre alt.` · `Ich möchte Arzt werden.` · `seit zwei Jahren` |
| False friends | `bekommen` ≠ become · `der Chef` ≠ chef · `also` ≠ also · `eventuell` ≠ eventually · `aktuell` ≠ actual | |
| Register | `Hallo Herr Novak, kannst du ...` | `Guten Tag Herr Novak, könnten Sie ...` |

## Animations that earn their place
| Topic | What moves |
|---|---|
| Verb in position 2 | an adverbial moves to position 1, subject and verb swap |
| Satzklammer | prefix, Partizip or infinitive slides to the end of the clause |
| Nebensatz (`weil, dass, wenn`) | two main clauses; the connector appears; the finite verb moves to the end |
| Relativsatz | noun is doubled as pronoun, clause is inserted, verb moves to the end |
| Passiv | object becomes subject, `werden` + Partizip II appear |
| Wechselpräpositionen | figure moves (Wohin? → Akkusativ) versus rests (Wo? → Dativ) |
| Dialogue flow (phone call) | steps of a call light up in order with the Redemittel |

- Words in the picture are German (target language); captions `de` + `en` explain each step. The end state equals the sentence in worksheet and explanation.
- Words of a sentence in the picture: one `<text>` with one `<tspan id>` per word (the browser sets the gaps), or measure each word with `getComputedTextLength()` before setting `x`. Estimated `x` values leave uneven gaps (`Balkon .`).
- Not for: vocabulary lists, tables of forms, anything a still table shows as well.
