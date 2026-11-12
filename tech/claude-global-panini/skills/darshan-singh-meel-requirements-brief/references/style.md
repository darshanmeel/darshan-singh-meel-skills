# Style and voice of the brief

## Voice
- Solution engineer who owns the brief writes it. First person where a decision is stated ("We load all sources daily", "I recommend dbt"), plain statements elsewhere.
- No trace of chat: never "you said", "as requested", "the requester", "asked us", "the user", "Claude", "as discussed", "confirm with", how the brief was made, what was skipped or could not be checked.
- Headings from input: a source, a conflict, a flow. Never a wrapper fitting any brief ("Overview", "Per need", "Work items"); blocks needing no heading sit directly in section.
- Open points = facts about the solution: "Owner to decide: retention period" · "Service interval per model: no source" · "Data not yet profiled." Never a request to the reader.
- Platforms named in input = "given": brief says how they carry the need, not whether they should.

## Words
- Tables + one-line bullets; prose only in a section `lead` (one or two sentences, the conclusion).
- One fact per bullet, ≤ 15 words where possible, never over 40.
- Say once: fact lives in owning section; others reference it ("section 5", "W1", "FLT-3").
- Concrete: "daily at 05:00", not "periodic"; "17 of 20 VINs", not "most".
- No intros, outros, diagram restated in prose, marketing words (robust, seamless, leverage), best-practice padding, emoji.
- Input's own ids everywhere: requirement rows, needs, work items, risks. Ids we assign (`R1…`) marked ours.

## Diagrams
- Only where picture beats table: context (always) · identity + linking (≥ 2 sources join) · timeline (timing/hand-offs matter). Not for a list.
- Each: title + `key` line; ≤ 12 boxes; ≤ 2 lines per box label; edge labels ≤ 12 characters.
- Print-readable: no colour-only meaning (tags + chips carry the word).

## Data
- Never a data row, never a real value of a sensitive-looking column; Data findings numbers from `profile.py` only, status counts from build.
- Never a person: no names, e-mails, phones from input (build fails on address/number); roles instead ("depot planner", "finance").
- Example values in text synthetic + recognisable (`YV2…`, `W-1234`).
- Secret files never opened; config value = `<redacted>`.

## Generic
- Any domain, any platform: no company, product, person names from input beyond what requirement names (source systems, given platforms).
- Paths relative to project root.
