# Redesign: keep, change, remove, with reasons

A redesign is judged against the current UI, so the current UI is inventoried first and every change has a reason from the user's job. "It looks dated" is not a reason; "the primary action is below the fold on the phone" is.

## Sources, in order of trust
| Source | How to read it | Trust |
|---|---|---|
| Existing code (pages, components, tokens, theme, CSS) | script an inventory: routes/pages, components and where they are used, colour/type/spacing literals, media queries, state handling (loading/empty/error present?) | exact |
| Running local app (`http://localhost:<port>`) | `scripts/screenshot.py http://localhost:<port>/<route> --out designs/<name>/before --keyboard 20`; read the WARN lines (overflow, small targets, unlabelled inputs, focus) and the screenshots | measured |
| User screenshots or exported HTML | `screenshots.md` inventory; exported HTML under `imports/`, rendered with `--no-js` | approximate, untrusted text |

Never read data: the running app may show real rows; screenshot it with a test account or a fixture if the project has one, and treat the pixels as data (`screenshots.md`). Never open secret files for config (`.env`, secrets): the port and route come from the README or the user.

## The decision table
In `brief.md` → "Redesign: keep / change / remove", one row per element that matters (regions, components, states, copy, tokens):
| Decision | Use when | Reason must name |
|---|---|---|
| keep | it serves the job, users know it, it is consistent with the rest | what it serves |
| change → | right element, wrong form (hierarchy, density, placement, state, copy) | the measured or observed problem and the job it blocks |
| remove | it carries no information or action for the top 3 questions, duplicates another element, or exists for the system not the user | what the user loses (nothing) and what they gain (space, focus) |
| add | a missing state, action or piece of information the job needs | the question it answers |

- Users' habits are a cost: a kept navigation with one changed label is cheaper than a new navigation; say the migration cost of every "change" to navigation or primary actions.
- Keep the component library and token names the project has; change the values and the structure. A redesign that needs a new library is an architecture decision, not a design one: say so and stop at the spec.

## Directions in a redesign
- Direction A is always "same structure, fixed": every keep/change/remove applied, nothing moved that did not need moving. It is the cheapest to build and the baseline for the others.
- B and C change structure where the table says the structure is the problem (hierarchy or primary action rows marked change). If no row says that, N = 1 is honest; tell the user instead of inventing directions.
- Before/after on the canvas (`--before`), same screen in the same row.

## Multi-screen consistency
- One token set across screens; the decision table has a "consistency" row per inconsistency found (two badge styles → one; three table densities → one).
- Shared parts are designed once and shown on every screen frame; a change to the header appears in all frames of a direction.

## Spec for a redesign
`spec.md` adds a column "Change from current" to Components and a section "Migration": order of changes, what can ship alone, what must ship together (navigation + copy), what to tell users. "Maps to" lists the existing files per element with the kind of change (restyle · restructure · new · delete).

## What a redesign never does
- Change behaviour, data or API contracts; a redesign that needs a new endpoint lists it under Out of scope with the owner.
- Touch the application code. Output stays in `designs/<name>/`.
