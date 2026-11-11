# Areas, topics, item families

Own working rules for this skill (no provider publishes a syllabus on the pages read; `sources.md`). Level: end of Klasse 9/10 (Hauptschul- or Realschulabschluss); nothing that needs Oberstufe.

- `module` = value in the JSON, `prefix` = start of the ids (`ma-pro-001` = Mathe, Prozent, item 1).
- Seconds = `time_seconds` for difficulty 1 → 3. Real tests set their own limits: a target's `profil.json` (job C) overrides this column.
- `check` column: what the item can carry for `check_items.py` (`aufgabenbau.md`).

## Mathe (`mathe`, `ma-`) - no calculator unless the item says so
| Topic | Item families | Seconds | Mistakes that give distractors | `check` |
|---|---|---|---|---|
| Grundrechnen | written +, −, ×, ÷; Punkt vor Strich; brackets; negative numbers | 30-60 | order of operations ignored; carry forgotten; sign lost | expression |
| Kopfrechnen | round and correct (99 × 47), halve and double, × 5, × 25, × 11 | 20-40 | correction forgotten or wrong sign; decimal place shifted | expression |
| Bruchrechnen | compare, expand, simplify, +, −, ×, ÷, fraction ↔ decimal ↔ percent | 30-75 | numerators and denominators added; divided without the reciprocal; not simplified | `F(1, 2) + F(1, 3)` |
| Prozentrechnung | share, base value, rate, discount, surcharge, two changes in a row, VAT | 30-90 | wrong base value; percent taken as euros; answered the discount, not the price | expression |
| Dreisatz | proportional (price, distance), inversely proportional (workers and days), mixtures | 45-90 | proportional used for an inverse case; one step missing | expression |
| Zinsrechnung | yearly interest, months and days (360-day year stated), capital or rate asked, compound interest over 2 years | 45-90 | months not converted; simple instead of compound interest | expression |
| Einheiten | length, area, volume, mass, time, speed; mm ↔ m, cm² ↔ m², l ↔ m³, min ↔ h | 30-60 | factor 100 used for areas instead of 10 000; 1,5 h read as 1 h 50 min | expression |
| Textaufgaben | age, distribution, work and time, price and quantity, average | 60-120 | intermediate value given as answer; condition overlooked | expression |
| Diagramme und Tabellen | read a value, difference, share, growth, average from a bar, line or pie chart or a table | 45-90 | wrong row or scale; absolute and percentage change mixed up | expression over the printed data |
| Gleichungen | one unknown, linear; missing number; "Rechenzeichen einsetzen" | 30-60 | sign changed wrongly when moving a term | expression |

## Logik (`logik`, `lo-`; figures: `raum`, `ra-`)
| Topic | Item families | Seconds | Mistakes that give distractors | `check` |
|---|---|---|---|---|
| Zahlenreihen | constant step, growing step, × and ÷, two alternating rules, two interleaved series, Fibonacci type | 30-75 | last step repeated instead of the rule; only the first rule of two applied; interleaved series read as one | `nach([printed], [rule])` |
| Buchstabenreihen | alphabet steps, skip patterns, mixed letters and numbers | 30-60 | counted from the wrong letter; step off by one | `nach` over letters |
| Matrizen | 3 × 3 figures: rotation, count, shading, addition of rows | 45-90 | rule read by row only; rotation direction swapped | - (cold solve; figure in `figure`) |
| Analogien | "A verhält sich zu B wie C zu ?"; relations: part-whole, tool-job, opposite, category, degree | 20-40 | association instead of the same relation; relation reversed | - |
| Oberbegriffe und Wortgruppen | find the generic term; which word does not belong | 20-40 | too broad or too narrow term; grouped by sound instead of meaning | - |
| Schlussfolgerungen | two premises → which statement is certainly true; orders and rankings; true/false tables | 45-90 | "some" read as "all"; converse taken as true | enumeration where finite |
| Raumvorstellung | nets that fold to a cube, rotated or mirrored figures, counting blocks, views | 45-90 | mirrored taken for rotated; hidden blocks not counted | count from a coded model |
| Würfel | opposite faces, rolled or tipped cube, which cube matches the net | 45-90 | adjacent and opposite faces swapped | coded model |

## Deutsch (`deutsch`, `de-`) - target texts stay German
| Topic | Item families | Seconds | Mistakes that give distractors |
|---|---|---|---|
| Rechtschreibung | which spelling is correct; which sentence has no mistake; das/dass, seid/seit, wieder/wider, capitalisation of nominalised words, ss/ß, compound or separate | 15-30 | the frequent wrong spellings themselves |
| Grammatik | case after prepositions, plural, tense, Konjunktiv II, relative pronoun, adjective ending | 20-40 | Dativ for Genitiv; wrong article gender |
| Kommasetzung | which sentence has correct commas; where is a comma missing (subordinate clause, infinitive group, list, apposition) | 20-40 | comma before "und" in a list; none before "dass" |
| Textverständnis | text of 80-150 words in `material`; statement true, false or not in the text; main idea; meaning of a word in context | 45-90 per question | statement from general knowledge, not from the text; detail turned around |
| Wortschatz | synonym, opposite, foreign word, idiom, which word fits the gap | 15-30 | similar-sounding word; related but not equal meaning |

## Other areas
| Area (`module`, prefix) | Topics and item families | Seconds | Notes |
|---|---|---|---|
| Englisch (`english`, `en-`) | vocabulary, tenses, prepositions, if-clauses, short text comprehension, everyday work phrases (e-mail, phone); level A2-B1 | 20-60 | item and options in English; German instruction; sidecar repeats the English and translates the explanation |
| Allgemeinwissen (`wissen`, `wi-`) | Politik und Staat (Bundestag, Bundesländer, EU), Geschichte, Geografie, Wirtschaft (Inflation, Brutto/Netto), Naturwissenschaft, Kultur | 15-30 | only stable facts; a fact that changes with an election or a year is not asked; every fact has a named source in the plan |
| IT-Grundwissen (`it`, `it-`) | hardware, operating system, file and folder, office programs, Internet and e-mail, data protection and passwords, bits and bytes | 20-45 | no product versions; technical Ausbildung may add number systems and simple logic |
| Konzentration (`konzentration`, `ko-`) | compare two strings (addresses, numbers, e-mail-like strings made of invented words), count a sign in a row, check target and actual numbers, sort | 6-20 | difficulty = length and similarity; exactly one difference type per distractor; never a real address or e-mail |
| Merkfähigkeit (`merken`, `me-`) | `material` to memorise (list, short profile, route, 60-120 s), then questions without it | 15-30 | questions ask positions, pairs and details; sheets print the material on its own page |
| Postkorb (`postkorb`, `po-`) | `material` = 5-8 short messages with times and senders (invented); order by urgency and importance, delegate, spot a clash of dates | 60-120 | key defensible by a stated rule: deadline first, then importance; no item where two orders are equally good |
| Persönlichkeit (`persoenlichkeit`, `pe-`) | statements with a 4-step agreement scale; how questionnaires work is taught in the chapter, not asked with a key | untimed: 20 | no key: `persoenlichkeit-sjt.md` |
| Situational Judgement (`sjt`, `sj-`) | short work situation of an Azubi, 4 reactions | 45-90 | no key: `persoenlichkeit-sjt.md` |
| Branchenwissen (`branche-<name>`, `br-`) | Bank (Konto, Zins, Kredit, Überweisung), Versicherung (Risiko, Beitrag, Haftpflicht), öffentlicher Dienst (Staatsaufbau, Grundgesetz, Verwaltung), Handel (Einkauf, Kalkulation, Kundengespräch), Technik/IT (Physik basics, technical understanding, hardware), Bahn (safety, timetable reading, service) | 20-60 | basics an applicant can know before the Ausbildung, not Ausbildung content; facts from the sector's official bodies; laws and amounts that change yearly are not asked |

## Mix of a general practice test (when no `profil.json` says otherwise)
| Area | Share |
|---|---|
| Mathe | 25 % |
| Logik (incl. Raumvorstellung) | 25 % |
| Deutsch | 20 % |
| Konzentration, Merkfähigkeit | 10 % |
| Allgemeinwissen | 10 % |
| Englisch | 10 % |

Persönlichkeit and SJT are added unscored at the end. Occupation shifts the mix: kaufmännisch → more Deutsch, Prozent, Dreisatz, Postkorb; technisch → more Raumvorstellung, Einheiten, technical understanding; IT → more Logik, IT-Grundwissen, Englisch; öffentlicher Dienst → more Deutsch, Allgemeinwissen (Staat).
