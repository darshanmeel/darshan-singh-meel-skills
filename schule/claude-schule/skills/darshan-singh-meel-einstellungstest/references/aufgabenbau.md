# Building chapters and items

Own working rules (`sources.md`). Example of everything below: `examples/mathe-prozent/`.

## Chapter
| Field | Rule |
|---|---|
| `title` | topic plus what the learner can do afterwards, at most 8 words |
| `concept` | 2-3 short paragraphs: why the test asks this and under which time pressure · the idea in everyday words · the one first step that always works. No formula without its meaning |
| `example` | one task as it could stand in the test, then the calculation or reasoning line by line (8-15 lines where the topic allows) |
| `example_explained` | the same example in sentences, one step per sentence, in the order of the lines; ends with a check ("Zur Probe …"). Readers see it sentence by sentence: no sentence depends on a later one |
| `tips` | 4-6: head-calculation shortcuts, what to read first, how to estimate, when to skip. Each tip one instruction with one example |
| `traps` | 2-4 in the form "X ist Y, nicht Z." - the right statement first, the tempting wrong one after "nicht". Each trap is the mistake behind at least one distractor of the chapter's questions |
| `practice_topics` | the `topic` values of the questions that train this chapter; contains at least the chapter's own `topic` |

- One chapter = one `topic` = about 8 questions. A question's `topic` equals a chapter `topic` letter for letter.
- Every number in `example` and `example_explained` is recomputed; both tell the same numbers.

## Question
| Part | Rule |
|---|---|
| Stem | 1-3 short sentences, one question, last sentence. Every number needed, none unused. Negations and deciding words (`nicht`, `genau`, `mindestens`, `höchstens`, `vor`, `nach`) only where the task needs them |
| Options | exactly 4, same form (all amounts, all words, all sentences), similar length; numbers ascending, unit in every option; German notation (`1.250,50 €`, `33,3 %`, fractions `3/4`) |
| Key | exactly one option correct under every reasonable reading; `answer` 0-3 |
| Explanation | way · `Typischer Fehler:` · `Trick:` (below) |
| `time_seconds` | from the table in `bereiche.md`; a prepared adult solves it in half that time |

- Never: "alle genannten", "keine der genannten", two options that mean the same, an option that is longer and more exact than the others, a stem that gives the answer away, trick wording.
- Stories: everyday life of a 16- to 19-year-old (Ausbildungsvergütung, Monatsticket, Berufsschule, Betrieb, shopping). Invented first names, mixed. No real companies, brands or persons.
- One item tests one thing. Reading load is not the difficulty, except in Textverständnis.

## Difficulty
| `difficulty` | Means | Steps | Share in a file |
|---|---|---|---|
| 1 | one known idea, direct numbers | 1-2 | about 40 % |
| 2 | two steps, or the idea must be chosen (which value is the base?) | 2-3 | about 40 % |
| 3 | reverse question, two rules at once, or a tempting shortcut that is wrong | 3-4 | about 20 % |

- Difficulty comes from the idea, never from ugly numbers: results are whole or have one decimal place; divisions come out even.
- Order in a file: easier first inside each topic.

## Distractors
One mistake → one wrong option. Sources, in order of preference:

| Mistake family | Example (15 % discount on 80 €, new price 68 €) |
|---|---|
| answered another quantity of the task | 12 € (the discount) |
| percent or unit taken as a plain number | 65 € (80 − 15) |
| wrong direction | 92 € (added) |
| wrong base or reference | discount computed on the new price |
| stopped one step early, or one step too many | intermediate value |
| inverse operation or reciprocal | 48 : 12 instead of 12 : 48 |
| decimal place or unit factor | 6,8 € · 680 € |
| typical spelling, grammar or meaning confusion (language items) | `seid` for `seit` |

- The explanation names the mistake behind the most tempting distractor; the plan (process A step 3) names all three.
- The correct value is not the only round number, the only one with a unit, or always the middle value.
- When fewer than three real mistakes exist, the item is rewritten; neighbours of the result (± 1) are a last resort and at most one per item.

## Key balance
- Decide the result first, then choose distractors so that the ascending order puts the result on the planned index.
- Per file: every index 0-3 about equally often. `check_items.py` fails a file of 8 or more keyed items where the most and the least used index differ by more than 2 (from 24 items: by more than an eighth of the items).
- Not the same index three times in a row in a printed sheet; the result is not always the largest or the smallest option.

## Explanation
1. **Way:** the steps a learner can repeat, with the numbers of the item, ending in the keyed option's value.
2. **`Typischer Fehler:`** the most tempting wrong option, the mistake that produces it, and why that is wrong.
3. **`Trick:`** the fastest safe way in the test: estimate, simplify the fraction, go via 10 %, eliminate two options, put the options in.

- 3-5 sentences in total. The English explanation uses `Typical mistake:` and `Trick:` at the same places; sheets split the text there into line pairs.
- Name values and words, never option letters or positions ("30 €", not "A"): options may be shuffled on screen.
- Language items: the rule in one sentence, then the example. Knowledge items: the fact, then how to remember it.

## The `check` field
A Python expression in the question that computes the result from the item's numbers. `check_items.py` evaluates it and requires: the option at `answer` equals the value, no other option does.

| Item | `check` |
|---|---|
| 20 % of 150 € | `"150 * 20 / 100"` |
| price after 15 % discount on 80 € | `"80 * (100 - 15) / 100"` |
| 1/2 + 1/3 | `"F(1, 2) + F(1, 3)"` (option `5/6`) |
| series 3, 6, 12, 24, ? | `"nach([3, 6, 12, 24], [3 * 2**i for i in range(6)])"` |
| letters A, C, E, G, ? | `"nach('ACEG', [chr(65 + 2 * i) for i in range(6)])"` (value `'I'`, compared with the option text) |
| 4 workers need 6 days, 3 workers? | `"4 * 6 / 3"` |

- Allowed: numbers, strings, `+ - * / // % **`, brackets, comparisons, lists, list comprehensions, `F` (exact fraction), `nach(printed terms, series built from the rule)`, `round abs min max sum len range sorted int str chr ord`. Nothing else: no names, attributes or imports.
- `nach` fails when the printed terms are not the start of the rule's series: it proves the stem, not only the answer.
- A number value is compared with the first number of each option (German notation); a string value with the whole option text. Mixed numbers (`1 1/2`) and times (`2:30 h`) are written as string values.
- The expression computes from the stem's data; it is never the constant result and never the shortcut of the explanation. Mathe items without `check` are listed with `?`.
- Why a field and not a separate script: the expression sits next to the item, survives copying the item into another file, and needs no code execution beyond a whitelisted expression.
- Not computable (language, knowledge, figures, Persönlichkeit): no `check`; solved cold twice (process A step 8) and by the reviewer.

## Originality
- Allowed: the general task types of aptitude tests (number series, analogies, percent, comparison of strings).
- Not allowed: a provider's, employer's or book's item with its wording, numbers, figure, story or option set - also not translated or with changed numbers only.
- Write from the plan (idea + result), not from a remembered item. Do not open a practice-test PDF while writing.
