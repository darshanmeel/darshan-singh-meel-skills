# Style and voice of the brief

## Voice
- The solution engineer who owns the brief writes it. First person where a decision is stated ("We load all sources daily", "I recommend dbt"), plain statements elsewhere.
- No trace of the chat: never "you said", "as requested", "the requester", "asked us", "the user", "Claude", "as discussed", "confirm with", how the brief was made, what was skipped or could not be checked.
- Headings come from the input: a source, a conflict, a flow. Never a wrapper that fits any brief ("Overview", "Per need", "Work items"); blocks that need no heading sit directly in the section.
- Open points are facts about the solution: "Owner to decide: retention period" · "Service interval per model: no source" · "Data not yet profiled." Never a request to the reader.
- Platforms named in the input are "given"; the brief says how they carry the need, not whether they should.

## Words
- Tables and one-line bullets; prose only in a section `lead` (one or two sentences that state the conclusion).
- One fact per bullet, ≤ 15 words where possible, never over 40.
- Say a thing once: a fact lives in the section that owns it; other sections reference it ("section 5", "W1", "FLT-3").
- Concrete over abstract: "daily at 05:00", not "periodic"; "17 of 20 VINs", not "most".
- No intros, outros, restating diagrams in prose, marketing words (robust, seamless, leverage), best-practice padding, emoji.
- The input's own ids everywhere: requirement rows, needs, work items, risks. Ids we assign (`R1…`) are marked as ours.

## Diagrams
- Only where a picture explains faster than a table: context (always), identity and linking (when ≥ 2 sources join), a timeline (when timing or hand-offs matter). Not for a list.
- Each has a title and a `key` line; ≤ 12 boxes; ≤ 2 lines per box label; edge labels ≤ 12 characters.
- Readable in print: no colour-only meaning (tags and chips carry the word).

## Data
- Never a data row, never a real value of a sensitive-looking column; numbers in Data findings come from `profile.py` only, the status counts from the build.
- Never a person: no names, e-mail addresses or phone numbers from the input (the build fails on an address or number); roles instead ("depot planner", "finance").
- Example values in text are synthetic and recognisable as such (`YV2…`, `W-1234`).
- Secret files are never opened; a config value is `<redacted>`.

## Generic
- Works for any domain and platform: no company, product or person names from the input beyond what the requirement itself names (source systems, given platforms).
- Paths relative to the project root.
