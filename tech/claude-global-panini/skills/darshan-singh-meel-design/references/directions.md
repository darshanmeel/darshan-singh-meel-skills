# Directions: how to make N designs that are worth comparing

A direction is a bet about what the user needs most. N directions = N different bets, each carried through every screen with the same tokens. The user picks a bet, not a colour.

## What must differ
Any two directions differ in at least two of:
| Axis | Examples |
|---|---|
| Layout | single column · table · master-detail · board · timeline · split view · cards then list |
| Hierarchy | what is first and largest: the exceptions · the full list · the trend · the one number · the form |
| Primary action | what it is and where: on each item · in a detail panel · one page-level button · sticky bottom |
| Navigation model | one page · tabs · drill-down · wizard steps · left rail with groups |

Not a direction: another colour, font, radius, spacing, icon set, copy, or the same grid with other card sizes. Those are tweaks; the canvas sliders exist for them.

## Naming the bet
- Each direction has a key (A, B, C…), a two-to-three-word name that states its structure ("Triage first", "Dense console", "Timeline"), and a one-line pitch: "failures are the job; the rest is context". The name goes in `data-name`, the pitch in `data-pitch`, both in the brief's table.
- A direction you cannot pitch in one line is two directions or none.
- **Every direction has one memorable element** (`craft.md`, "Point of view"), named in the pitch after the bet: "failures are the job; the headline reads like an incident report". A direction whose only description is its layout ("cards above a table", "sidebar and table") is not finished.

## Picking the N bets
1. Write the top 3 questions or actions from the brief.
2. For each, ask: if this were the *only* thing the screen did well, what would it look like? That gives 3 candidate bets.
3. Add the obvious structure the user probably expects (the "safe" one) if it is not already there; it anchors the comparison.
4. Add one that challenges the brief's assumption (a different navigation model, a different unit of work) when N ≥ 3.
5. N = 1: the safe structure done exceptionally well. N = 5: the three from step 2, the safe one, the challenger. Never pad with a colour variant.

## Carrying a direction across screens
- The bet decides every screen: a "triage first" direction shows the exceptions first on the detail page too; a "timeline" direction uses time as the axis on the list and the detail.
- Shared parts (header, nav, badges, buttons, table row) are identical across screens of one direction and may be identical across directions; the *structure* differs, not the atoms.
- One token set for all directions. A direction that needs its own tokens is a different product, not a direction; the only allowed per-direction override is `--density` (and it goes in the brief).

## Same content everywhere
- Every direction renders the same synthetic fixture (same rows, same failures, same long value), so the comparison is about structure, not luck.
- Keep the fixture in the brief or as a block in each file; the number of rows reflects the real volume (8–15 for a list, 1 long error, one empty section where the real app has one).

## Critique before showing
Run `scripts/screenshot.py` on the round and answer the ten questions in `craft.md` per direction in `round-N/critique.md`. Fix what you can; keep what you could not fix in "Still open" so the user does not spend their comments on it. Then rebuild the canvas.

## Reading the user's pick
- "A" → refine A; the brief's decisions log says why A.
- "A with B's table" → a mix: A's layout and hierarchy, B's component; name the result in round 2 ("A2 — Triage first with dense list").
- Comments on several directions without a pick → round 2 has 2 directions: the strongest per the critique plus the one most commented, each carrying the comments that apply to it.
- "None" → the bets were wrong, not the pixels: go back to step 1 with the comments as new top questions.

## Showing a single direction (N = 1) or a final
Still a frame on the canvas, still both viewports and themes, still a `critique.md`. The canvas is where the user comments; a single HTML opened directly has no notes, no sliders, no theme toggle.
