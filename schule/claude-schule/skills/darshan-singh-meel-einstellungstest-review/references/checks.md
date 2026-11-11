# Einstellungstest checks (E1-E14)

Added to the 12 areas of the base `review.md`. Rule sources: `bereiche.md`, `aufgabenbau.md`, `formate.md`, `ziel.md`, `persoenlichkeit-sjt.md` of `darshan-singh-meel-einstellungstest`.

## Blind-solving table (step 3, before any key is opened)
| id | Diff. | Own result | Own index | Way | Second way or Python | Seconds | (A) | (B) | (C) | (D) |
|---|---|---|---|---|---|---|---|---|---|---|
| ma-pro-003 | 1 | … | … | … | … | … | mistake or "none" | … | … | … |

- Columns (A)-(D): "richtig" for the correct option; for each wrong option the mistake that produces it, or "none found".
- Seconds: your own time without calculator. Limit: half of `time_seconds`.
- Own Python check: computes from the stem's data and prints which options equal the result. Exactly one must.
- Unkeyed items (`answer` -1) are listed without result: columns (A)-(D) hold what each option shows in your own words, written before reading the explanation.

## Checks: items and chapters
| # | Check | How | Must when |
|---|---|---|---|
| E1 | Key correct | own result = option at `answer`; same letter in key line, solution section, key row, `data-loesung` | any key wrong; JSON and sheet disagree |
| E2 | Exactly one correct option | each wrong option tested against the stem under every reasonable reading (inclusive or exclusive counting, which value is the base, rounding, "pro Monat" or "pro Jahr", order of two changes); language items: no second spelling or word that is also accepted; knowledge items: no second true option | two options defensible; none correct |
| E3 | Stem complete and unambiguous | all data given, none unused; unit and period stated; one question; deciding words present; series with enough terms to fix the rule (two rules must not give different next terms that are both options) | data missing; two readings with different answers |
| E4 | Explanation consistent | leads to the keyed value with the item's numbers; `Typischer Fehler:` names an option that exists and the mistake really gives that value (recompute); `Trick:` works and is faster; no reference to an option letter that changes when options are shuffled | explanation reaches another value or justifies another option (Should when only the mistake line or the trick is wrong) |
| E5 | Distractors | each wrong option follows from a nameable mistake; correct value not marked by form (only round number, longest option, only one with a unit); options in one form, numbers ascending | - (Should); Must when a distractor is also correct (then E2) |
| E6 | Difficulty and time | 1: one known idea · 2: two steps or a choice · 3: reverse question or two rules; difficulty from the idea, not from ugly numbers; solvable without calculator in `time_seconds`; own time within half of it; mix in the file | arithmetic not feasible in the time without calculator; an item labelled 1 that needs a 3-idea, or the reverse, so clearly that a learner is misled |
| E7 | Level and area | only content of `bereiche.md` for the module; Klasse 9/10 knowledge; Branchenwissen = basics before the Ausbildung; facts stable and true today (recheck every date, office, amount, law against a named official source or mark "not verified") | content beyond the level is required; a knowledge fact is wrong or outdated |
| E8 | `check` field | present on every computable item; computes from the stem's numbers; series use `nach` with the printed terms; not a constant; your own computation agrees | `check` restates the answer on an item whose key is wrong; computable Mathe item without `check` in a set that claims "recomputed" (else Should) |
| E9 | Unkeyed items | `answer` -1 only in `persoenlichkeit` and `sjt`; statements: one idea, first person, no double negation, nothing private, part of them reverse-worded; situations: Azubi setting, four possible reactions, none absurd; explanation in the three parts of `persoenlichkeit-sjt.md`, without "richtig ist", ranking or advice to fake | an explanation tells the learner which answer to tick to look better; a key or ranking is given; a statement asks for private data (health, family, religion, politics, origin) |
| E10 | Chapter | `concept` says why and gives the first step; `example` and `example_explained` tell the same numbers and are right (recompute); steps in order, one per sentence; tips are instructions with an example; traps as "X ist Y, nicht Z." and true; each trap is a distractor mistake of the chapter's questions; question topics = chapter topic | a wrong statement, number or rule in a chapter; a trap that teaches the wrong side |
| E11 | Target fidelity (job C) | `profil.json` sections, formats and weights follow the pages in `sources`; every page used is named; facts only on rank-3 pages or inferred are `check:`; no pass mark, no claimed scoring rule; open each named page that is reachable and compare | a test fact stated as certain that the named page does not say, or that changes how the learner prepares (calculator, pause, deduction, duration); a page used but not named |
| E12 | Originality and claims | footer "keine Originalaufgaben" on every sheet; no provider logo or product name used as if the material were official; no item that reproduces a published sample question's wording, numbers, figure or option set (compare with the sample questions on the pages in `sources`) | copied or translated item; material presents itself as a provider's or employer's test |
| E13 | Generic material | no person's name or data, no invitation detail (access code, login, link with a token, test date, reference number), no e-mail address or machine path in any file; profile `sources` name pages only; Konzentration items use invented strings | any of these present |

## Checks: mock tests
| # | Check | How | Must when |
|---|---|---|---|
| E14 | Mock test | sections and order as in `profil.json` or the general mix of `bereiche.md`; questions per section = weight × size; weights sum to 100; section time = sum of `time_seconds` rounded up (full size: the profile's minutes); a short test of a target says "Kurzfassung"; `data-gesamt` = number of keyed questions; unscored part last and without points; answer-sheet cells = questions; rules box matches the scoring block; no key, difficulty or strategy on the test file; no grade key | totals or times wrong; a key visible on the test; a pass mark or grade stated; an assumed fact not marked `unverified` |

## Frequent defects
| Defect | Example | Finding |
|---|---|---|
| Base value open | "Der Preis steigt um 20 % und fällt um 20 %" without saying of what | E3 |
| Period open | interest "für 6 Monate" with a yearly rate not named as yearly | E3 |
| Series fits two rules | 2, 4, 8, ? (× 2 → 16; +2, +4, +6 → 14) with both as options | E2: add a term |
| Rounding decides | 33,3 % and 33 % both offered | E2 |
| Second correct spelling | variant allowed by the official rules listed as wrong | E2, E7 |
| Fact has an expiry date | "Wie hoch ist der Mindestlohn?" | E7: do not ask |
| Explanation names a letter | "B ist richtig" while options may be shuffled | E4 (Should): name the value |
| Key follows a pattern | correct option always the second-largest | E5 |
| Distractor without a mistake | 3 random neighbours | E5 |
| English changes the task | "höchstens" → "at least"; 1.250 → 1.250 instead of 1,250 | base area 7, Must |
| Test-object text translated | spelling item whose options are "corrected" in English | base area 7, Must |
| SJT with a hidden key | explanation: "Am besten ist Antwort C." | E9 |
| Unnamed source | profile weight taken from a prep page that is not in `sources` | E11 |
| Faking advice | "Stimme bei Teamfragen immer voll zu." | E9, Must |
| Sheet differs from JSON | options reordered on the sheet, key letter not adjusted | E1 (script) |

## Report additions
- Section "Nachgerechnet": the blind-solving table, shortened to: id · difficulty · own result · own index · key · match · other options wrong · seconds. Unkeyed items: id · "ohne Schlüssel" · explanation fair (yes/no).
- Section "Not checked": always list what could not be verified - originality against all published tests (no systematic comparison), knowledge facts without an official source at hand, target facts marked `check:`, pages that could not be opened, print on paper.
- Verdict words as in base `review.md`. A wrong key or a second defensible option (E1, E2) is a Must in base area 2 and leads to "Überarbeiten" when more than one item in ten is affected. E9 faking advice and E13 findings block use until fixed, whatever the count.
