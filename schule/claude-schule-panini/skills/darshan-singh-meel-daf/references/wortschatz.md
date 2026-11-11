# Vocabulary by level

Official word lists exist for A1, A2 and B1 (Goethe-Institut, free PDFs; `sources.md`). They are copyrighted: use them to check whether a word is at level, never copy a list or its example sentences. Lists written here are our own, grouped by word field.

## Format of an entry
| Word class | German column | English column | Example sentence (German only) |
|---|---|---|---|
| Nomen | article + noun, plural ending: `der Termin, -e` · `die Krankmeldung, -en` · `das Attest, -e`; umlaut plural written in full: `der Aufzug, die Aufzüge` (never `-¨e`); no plural: `(Sg.)`; plural only: `(Pl.)` | the noun without article | one sentence at level using the word in the lesson's situation |
| Verb | infinitive; from A1.2 with 3rd person if irregular and Perfekt: `anrufen, ruft an, hat angerufen`; case or preposition: `jemandem (D) helfen`, `warten auf (+ A)` | `to call` | as above |
| Adjektiv | base form; irregular Komparativ: `gut, besser, am besten` | adjective | as above |
| Chunk / Redemittel | whole phrase: `Gute Besserung!` | closest natural phrase: `Get well soon!` | none |

- Order inside a list: by word field, then nouns (der, die, das), verbs, adjectives, phrases. Alphabetical only for a reference list.
- Mark separable verbs with a dot or stress line only in A1-A2: `an·rufen`.
- English: the meaning in this context, one or two words; a second meaning only if the lesson uses it. False friends get a note (`bekommen | to get, not: to become`).
- Size: lesson glossary 8-12 words; unit list 30-50; never a list without example sentences below B2.
- B2-C1 entries add: register (`ugs.`, `formell`), collocations (`eine Entscheidung treffen`), word family (`entscheiden, die Entscheidung, entscheidend`).
- Beruf lists add the Handlungsfeld and typical collocations (`einen Termin vereinbaren / verschieben / absagen`).

## Word fields per level (what a full course covers)
| Level | Word fields |
|---|---|
| A1 | Person (Name, Herkunft, Alter, Adresse) · Familie · Zahlen, Uhrzeit, Wochentage, Monate · Lebensmittel, Getränke · Wohnung, Möbel · Stadt, Verkehrsmittel · Berufe (Grundwörter) · Freizeit · Körper (Grundwörter) · Farben · Wetter |
| A2 | Arbeit, Ausbildung, Schule · Gesundheit, Arztbesuch · Kleidung · Reisen, Unterkunft · Wohnungssuche, Haushalt · Feste, Einladungen · Bank, Post, Behörden · Medien (Grundwörter) · Gefühle (Grundwörter) |
| B1 | Arbeitswelt (Bewerbung, Arbeitszeit, Kollegen) · Umwelt · Medien · Konsum, Geld · Ernährung, Gesundheit · Beziehungen · Bildung · Verkehr · Meinung, Zustimmung, Widerspruch |
| B2 | Gesellschaft, Politik (Grundbegriffe) · Wirtschaft · Wissenschaft, Technik · Kultur · abstrakte Nomen, Nomen-Verb-Verbindungen · Redemittel für Argumentation, Grafik, Vortrag |
| C1 | Fach- und Bildungssprache · Funktionsverbgefüge · Synonyme und Register · Idiomatik · Redemittel für Zusammenfassung, Diskussion, Forumsbeitrag |

Beruf word fields: `beruf.md`.

## Is the word at level?
1. A1, A2, B1: look it up in the Goethe word list of that level (`sources.md`). In the list → at level. Not in the list → glossary entry, or replace it.
2. B2, C1: no official list. Rule: transparent derivations and compounds of B1 words are at level; technical terms and idioms get a glossary entry.
3. International words (`das Hotel, das Taxi, die E-Mail`) are fine from A1; check article and plural.

## wortschatz.html (extra output)
- Built from the base `arbeitsblatt.html` template; `data-typ="arbeitsblatt"` stays, title `Wortschatz - <Thema>`.
- One table per word field: `Deutsch | English | Beispielsatz`; German and example cells `data-nur-de`; the English cell `lang="en"`.
- Ends with 2-3 short tasks (zuordnen, ergänzen, eigene Sätze) with `data-aufgabe`, so the list is practised; solutions in `loesung.html`.
- Level, topic and number of words in the header line.
