# German with English lines

Purpose: a reader with more English than German follows the German material line by line. The English is a reading aid for the German, not a second version of the lesson.

## The rule
- German is the material. Under (or beside) every German line stands one English line.
- The English line is **the closest English sentence to the German in that context**:
  - same meaning, same facts, same numbers, same operator;
  - same sentence count and the same order of ideas, as far as English grammar allows;
  - same grammatical choices where English has them (imperative stays imperative, question stays question, passive stays passive, "man" → "one"/"you" as fits);
  - correct, natural English - a native teacher would accept the sentence.
- Not allowed: adding, dropping, merging, splitting, explaining, simplifying, "improving" the content.
- Not allowed: German word order or word-for-word idioms that are wrong or odd in English.
- Subject terms: the established English school term, not a calque (`Bruch` → `fraction`, not `break`). Unsure → official bilingual operator list, then the subject skill's term list, then a standard English school curriculum term.
- German compounds and nominal style: keep the noun if English has one (`Lösungsweg` → `solution steps`), else the shortest natural phrase.
- Du/Sie: both → "you". Gendered pairs (`Schülerinnen und Schüler`) → one English noun (`students`).
- Numbers and units: keep the German form in the German line (`3,5 kg`), English form in the English line (`3.5 kg`). Formulas, symbols and names are not translated and not repeated when the line is only a formula.
- Dates and places: keep; exonyms only where standard (`München` → `Munich`).
- Quoted official wording (KC competence, law): German as printed; English line is our own translation - the template says so.

## What gets an English line
| Element | English line |
|---|---|
| Titles, headings, labels | yes, short form after a slash: `Aufgabe 1 / Task 1` |
| Instructions, tasks, sub-tasks, hints | yes |
| Info boxes, explanations, examples, Merksätze | yes |
| Solutions, solution steps, typical mistakes, Erwartungshorizont entries | yes |
| Lesson plan: goals, phase descriptions, differentiation, homework | yes |
| Animation captions | yes (`de` + `en` per step) |
| Figure labels | symbols, or `DE / EN` when there is room; else the caption carries it |
| Glossary | `DE | EN | Bedeutung / Meaning`; German nouns with article, English with part of speech only when ambiguous |
| A line that is only a formula, number, name or unit | no |
| Answer spaces | one per task; students answer once, in the language the teacher sets |

## Deutsch as a subject, DaF/DaZ
- Texts under analysis (poem, story, article, source), dictation texts, example sentences, gap texts, grammar tables and model answers **stay German only**. Mark the block `data-nur-de`.
- English only on: instructions, task wording, explanations of a rule, glossary. In DaF below B1 also on Merksätze.
- Never give the English of the text the student must understand or produce - it removes the task. Vocabulary help goes into the glossary.
- From B2/C1 and in Oberstufe Deutsch the English lines shrink to instructions and glossary; say so in the setup answer.
- History and other subjects with German sources: the source stays German (`data-nur-de`), tasks and explanations get the English line; a glossary covers hard source words.

## Examples: good, too free, too literal
| German | Good (closest natural sentence) | Too free | Too literal |
|---|---|---|---|
| Berechne den Flächeninhalt des Rechtecks und gib das Ergebnis in cm² an. | Calculate the area of the rectangle and give the result in cm². | Work out how big the rectangle is. *(drops the unit, changes the operator)* | Calculate the surface content of the right-corner and give the result in cm² on. |
| Erkläre, warum die Pflanze ohne Licht nicht wächst. | Explain why the plant does not grow without light. | Tell us what plants need in order to grow well. *(new question)* | Explain, why the plant without light not grows. |
| Die Stadt wurde im Jahr 1241 zum ersten Mal urkundlich erwähnt. | The town was first mentioned in a document in the year 1241. | Records show the town is nearly 800 years old. *(computes, drops the date)* | The town became in the year 1241 for the first time documentarily mentioned. |

More pairs for calibration:

| German | English line | Note |
|---|---|---|
| Es gibt drei Möglichkeiten. | There are three possibilities. | not "It gives three possibilities." |
| Schreibe in ganzen Sätzen. | Write in complete sentences. | not "whole sentences" |
| Lies den Text genau. | Read the text carefully. | `genau` here = carefully, not "exactly" |
| Was fällt dir auf? | What do you notice? | not "What falls to you up?" |
| Begründe deine Antwort. | Give reasons for your answer. | official pair style; "Justify your answer." also fits |
| Im Folgenden wird der Versuch beschrieben. | In the following, the experiment is described. | passive kept |
| Man gibt 5 g Salz in das Wasser. | One adds 5 g of salt to the water. | "You add" in Grundschule |
| Je größer die Masse, desto größer die Gewichtskraft. | The greater the mass, the greater the weight force. | structure kept |

## Test of a line (writer and reviewer)
1. Translate the English line back to German in your head: do you land on the German line, with nothing extra and nothing missing?
2. Read the English line alone: correct grammar, a normal sentence, the right subject term?
3. Same operator, same numbers and units, same number of sentences?
- Fail 1 → too free. Fail 2 → too literal. Fix the line, not the German - unless the German itself is unclear; then fix the German first.

## Layout
- Markup: `references/formate.md` (`.bi` pair: German first, then `class="en" lang="en"`).
- Screen: English under the German line by default; "nebeneinander / side by side" puts block pairs into two columns on wide screens.
- "Englisch anzeigen / Show English" is on by default; switching it off hides every English line. Print shows what the screen shows.
- English lines look different by more than colour (bar at the left, lighter weight), same font size.
- Grundschule: at most one short English line per German line; no English on handwriting or reading-practice lines.

## Language options (setup question 4)
| Option | `body data-sprache` | Result |
|---|---|---|
| Deutsch mit englischer Zeile (default) | `de-en` | every line paired; toggle in the page |
| Deutsch + nur Fachbegriffe DE \| EN | `de` | German only; glossary with English terms; no toggle |
| zusätzlich ganz englische Fassung | `en` in a second file `<name>.en.html` | same layout, English only, same closeness rule |
