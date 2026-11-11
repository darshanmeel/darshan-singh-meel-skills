# Scoring, Prädikate, rubrics

Replaces the Hessen grade rules of the base for DaF courses. Official facts: `pruefungen.md`, `sources.md`. Everything marked "own" is a working rubric modelled on the exams, not an official scheme.

## Tests in a course
| Type | Use | Total | Pass |
|---|---|---|---|
| Lernkontrolle zum Thema | after a unit; mixes Wortschatz, Grammatik, one receptive skill, one short production | 20-40 P (or 100) | 60 % |
| Prüfungstraining | one part or a mock of a named exam | as in the exam | as in the exam |
| Einstufung | placement; rising difficulty, stops when items fail | no pass mark; result = level band | - |

- Pass mark 60 % is the rule in Goethe, DTB and telc Deutsch B1 (read) and the default here; the dual-level telc Deutsch A2·B1 asks 70 % for B1 (`pruefungen.md`).
- Shares in a Lernkontrolle (own default): receptive and form tasks (AFB I-II) 60-70 %, production (AFB III) 30-40 %. A learner who solves the closed tasks and writes an understandable short text passes.
- AFB for the check script (own mapping): I ankreuzen, zuordnen, Lücke mit Wortkasten, Formen bilden · II Lücke ohne Hilfe, Sätze umformen, Fragen zum Text in eigenen Worten, gelenktes Schreiben nach Muster · III freies Schreiben, Sprechen, Mediation, Stellungnahme.
- Time: closed item 30-45 s at A1-A2, 20-30 s from B1; reading text 1 min per 50 words at A1-A2, per 80 words from B1; writing 1 min per 3-4 words at A1-A2, per 5-6 words from B1; teacher needs about one third.

## Prädikat table (Goethe, read) for `erwartungshorizont.html`
| Prädikat | from share | `data-note` |
|---|---|---|
| sehr gut / very good | 90 % | 1 |
| gut / good | 80 % | 2 |
| befriedigend / satisfactory | 70 % | 3 |
| ausreichend / sufficient | 60 % | 4 |
| nicht bestanden / failed | below 60 % | 5 (`data-ab="0"`) |

- Row header in the file: `sehr gut <span class="en" lang="en">/ very good</span>` (the Prädikat is the official German term; the English is our help line, and the check script then gives no warning).
- Points needed = share × total; no rounding in the learner's favour unless the user's institution says so (Goethe rounds results to whole points, 0,5 up).
- Line under the table: `Prädikate wie im Goethe-Zertifikat (Durchführungsbestimmungen, Stand 1. September 2025); bestanden ab 60 %.`
- Courses in schools that must give Noten 1-6: ask for the school's key; do not convert Prädikate into Noten on your own.

## Closed items
- 1 P per item, right or wrong, no half points; several gaps in one sentence = several items.
- Key lists every accepted answer (`Ich bin krank. / Ich habe Fieber.`); spelling counts only when spelling is the target or the word becomes another word. Say so in "Hinweise zur Korrektur".
- Grammar item: point for the target form; an unrelated slip does not cost the point.

## Schreiben: rubric (own, modelled on the exam criteria)
| Criterion | 3 | 2 | 1 | 0 |
|---|---|---|---|---|
| Aufgabenerfüllung (content points, text type, register) | all content points treated, text type and address fit | one point thin or missing, or register slips | several points missing; text type barely recognisable | off topic or too short to judge |
| Kohärenz (order, linking) | clear order; connectors of the level used correctly | order mostly clear; few or repeated connectors | sentences side by side | no connection |
| Wortschatz | fits the task and the level; few wrong choices | limited but sufficient; some wrong choices | gaps hinder the message in places | message not carried |
| Strukturen (grammar, spelling) | structures of the level mostly correct; errors do not disturb | several errors, message clear | errors make reading hard in places | not understandable |

- Total 12; scale to the points of the task (`points = rubric / 12 × task points`, round to half points).
- Aufgabenerfüllung 0 → whole task 0 (as in the exams: check: Modellsatz).
- Per content point the simple A1 scheme (Goethe A1 Teil 2: read) may replace the rubric at A1: 3 P fulfilled and understandable · 1,5 P partly fulfilled · 0 P not fulfilled or not understandable; understandability decides, not the number of errors.
- Level anchors for "Strukturen 3": A1 main clauses with verb in position 2 · A2 `weil/dass/wenn` with verb at the end, Perfekt · B1 several subordinate clause types, tenses consistent · B2 complex sentences, few systematic errors · C1 errors rare and hard to spot.

## Sprechen: rubric (own, modelled on the exam criteria)
| Criterion | 3 | 2 | 1 | 0 |
|---|---|---|---|---|
| Aufgabenerfüllung, Interaktion | does what the task asks; reacts to the partner, asks back | task mostly done; reacts with delay or only when asked | needs much help; hardly reacts | no usable contribution |
| Kohärenz, Flüssigkeit | speaks connectedly for the length the level expects | pauses and restarts, thread stays clear | single words and chunks | - |
| Wortschatz | fits task and level | limited, sufficient | gaps hinder | - |
| Strukturen | mostly correct for the level | errors, message clear | errors hinder in places | not understandable |
| Aussprache, Intonation | understandable without effort | some effort for the listener | much effort | not understandable |

- Total 15; scale as above. Record on the sheet per learner by placeholder (`TN 1`), never a name in a saved file.
- Speaking in class: assess one criterion per activity, not all five.

## Official criteria names
| Exam | Schreiben | Sprechen | Status |
|---|---|---|---|
| DTB A2-C1 | I Kommunikative Aufgabenbewältigung · II Kommunikative Gestaltung · III Formale Richtigkeit · IV Spektrum sprachlicher Mittel | I Kommunikative Aufgabenbewältigung · II Aussprache/Intonation · III Formale Richtigkeit · IV Spektrum sprachlicher Mittel | read (Prüfungshandbuch 2021); no counting of words or content points |
| Goethe A1 | Teil 2: Erfüllung der Aufgabenstellung per content point (3 / 1,5 / 0) | per task: full / half / 0 points for Erfüllung der Aufgabenstellung und sprachliche Realisierung; understandability decides | read (Prüfungsziele, Testbeschreibung) |
| Goethe A2-C1 | check: Modellsatz, Prüferblätter (commonly: Erfüllung, Kohärenz, Wortschatz, Strukturen) | check: same (plus Aussprache) | not read |
| telc Deutsch B1 | I Aufgabenbewältigung · II Kommunikative Gestaltung · III Formale Richtigkeit; each A 5 · B 3 · C 1 · D 0; sum × 3 = at most 45 P | 1 Ausdrucksfähigkeit · 2 Aufgabenbewältigung · 3 Formale Richtigkeit · 4 Aussprache und Intonation | read (Übungstest 1, 2020); band descriptors: check: same PDF |
| DTB B2 | ratings A-D = B2 gut erfüllt · B2 erfüllt · B1 erfüllt · unter B1 | same ratings | read (Übungstest 1, 2020) |
| telc, other exams | check: Übungstest of the exam | check | not read |

For Prüfungstraining use the official criteria names of that exam when read; otherwise the own rubric with the note `Raster in Anlehnung an die Prüfung - Originalkriterien im Modellsatz prüfen`.

## Error marking in learner texts
| Mark | Meaning |
|---|---|
| `G` | Grammatik (form, case, tense) |
| `W` | Wortwahl |
| `St` | Wortstellung |
| `R` | Rechtschreibung |
| `Z` | Zeichensetzung |
| `∨` | word missing |

- Mark at most the errors of the lesson's target structure plus those that block understanding; A1-A2 texts are not covered in red.
- Feedback line: one thing done well in the task's terms, one target for next time, both at the learner's level (German + English line up to B1).

## bewertungsraster.html (extra output)
- Built from the base `erwartungshorizont.html` template; table rows = criteria, columns = point bands; every descriptor with its English line.
- Header: task, level, total points, scaling rule. One line of space per criterion for a note. No learner names.
