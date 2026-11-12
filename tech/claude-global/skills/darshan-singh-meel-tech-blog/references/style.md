# Style: every word informs

The script flags the phrases below (`BANNED` = FAIL, `SUSPECT` and patterns = `?`). A `?` is a prompt to look, not a verdict: "the primary key" may stay; "a key insight" goes.

## Sentence rules
| Rule | Instead of | Write |
|---|---|---|
| Active voice, actor named | "The row is updated by the statement" | "The statement updates the row" |
| Second person, present tense | "We will now create a table" · "The user should" | "Create a table" · "You get one row per order" |
| Fact instead of adjective | "a powerful, flexible feature" | "one statement replaces the read-then-write" |
| Number instead of intensifier | "significantly faster" | "6 s instead of 41 s (median of 5 runs)" |
| Specific instead of general | "various issues can occur" | "the second run fails with `UNIQUE constraint failed`" |
| One idea per sentence | 40-word sentence with three clauses | two or three sentences, 35 words at most |
| Term stays the same | "table", then "relation", then "dataset" for one thing | "table" every time |
| Say it once | point, then "in other words", then recap | the point |
| No hedging stack | "it might possibly be worth considering" | "use X when Y" - or state the doubt once, with its reason |
| No difficulty judgements | "simply", "just", "easy", "obviously" | the step |

- Paragraphs: 2-5 sentences, 120 words at most, first sentence carries the point.
- Passive is right when the actor is unknown or irrelevant ("the feature was added in 3.24.0"). Keep those.
- Define an abbreviation at first use unless the reader in the brief uses it daily.
- Code terms, file names, commands, values in code font. UI labels in bold. No bold for emphasis in running text.
- Humour, anecdotes and opinions: allowed when they carry a fact the reader needs; first person for experience ("we", "I"), second person for instructions.
- Plain punctuation: at most one em dash per 300 words; no exclamation marks; no emoji; no rhetorical questions as transitions.

## Slop: cut on sight
| Kind | Examples | Fix |
|---|---|---|
| Scene-setting intro | "In today's data-driven world", "As systems grow more complex", "X has become increasingly popular" | start with the problem or the result |
| Announcing | "In this post, we will explore", "Let's dive in", "Without further ado" | delete; the headings announce |
| Hype | "game-changer", "revolutionary", "seamless", "cutting-edge", "blazing fast", "supercharge", "unlock the power" | the measured effect, or nothing |
| Empty weight | "It's worth noting that", "It's important to note", "Needless to say", "At the end of the day", "When it comes to" | delete the phrase, keep the fact |
| Vague verbs | "leverage", "utilize", "harness", "streamline", "empower", "elevate" | "use", or the exact action |
| Vague praise | "robust", "powerful", "elegant", "modern", "best practice" | what it survives, does, or who recommends it (link) |
| False contrast | "It's not just X - it's Y", "not only X but also Y" | say Y |
| Question-then-answer | "The result? Chaos." "Why does this matter?" | state it |
| Rule of three for rhythm | "fast, reliable, and scalable" with no evidence for any | the one you measured |
| Mirrored closers | a one-line moral at the end of each section; "And that's the beauty of X" | delete |
| Recap endings | "In conclusion, we have seen", "I hope this helps", "Happy coding" | `Takeaways` with rules |
| Generic claims | "many developers struggle with", "experts agree" | who, where (link), or cut |
| Drafting trace | "as discussed", "as you requested", "per your request", "based on our conversation", "you haven't confirmed this on production" | the fact in the author's words: "Not tested on a production workload yet" |
| Signposting | "As mentioned above", "As we will see later" | link the section or reorder |
| Padding lists | bullets that restate the paragraph above; 3-word bullets under every heading | keep one form |
| Decorative structure | a heading over one paragraph; bold lead-ins on every bullet; a table for two items | plain paragraph |

## Before / after
| Before | After |
|---|---|
| "In today's fast-paced world of data engineering, idempotency has become a crucial concept that every engineer should understand." | "A load job that runs twice inserts every row twice - unless the load is idempotent." |
| "It's worth noting that this approach can significantly improve performance in many cases." | "On the 2-million-row test table the merge takes 6 s; delete-and-reload takes 41 s." |
| "Let's dive into how we can leverage the powerful UPSERT feature to seamlessly handle conflicts." | "`ON CONFLICT ... DO UPDATE` turns an insert that hits an existing key into an update." |
| "As you can see, the output clearly shows that everything works as expected." | "The second run leaves the count at 3: no duplicates." |
| "This isn't just a syntax trick - it's a fundamental shift in how you think about pipelines." | "With this, a retry needs no cleanup step." |

## Cut pass (step 8)
1. Delete the first paragraph; if the post still works, keep it deleted.
2. For each sentence: what does the reader learn? Nothing → delete. Already said → delete.
3. For each adjective and adverb: replace with the fact, or delete.
4. For each "this", "it", "that" at the start of a sentence: name the thing.
5. Read the headings alone, then the first sentence of each paragraph alone. Each list must make sense.
