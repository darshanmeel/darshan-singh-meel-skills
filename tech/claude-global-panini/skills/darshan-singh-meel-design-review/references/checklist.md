# Design review checklist

The one source of severity. Used by `darshan-singh-meel-design-review` (all columns) and by the design skill's own critique (Must column). Judge against the job: product, user, the one thing the screen is for.

| # | Area | Check | Must when | Should when |
|---|---|---|---|---|
| 1 | Job | brief or spec names product, user, main job and top 3 questions; the first viewport at 1280 and 390 answers them | the job cannot be told from the screen; the first viewport answers something else | top 3 answered but one needs a scroll or a click that the job does not justify |
| 2 | Hierarchy | one focal point; reading order = job order; primary action where the decision ends; three levels, not more | two competing focal points; the primary action unreachable without scrolling at 390 and nothing fixed; the key number without unit or period | a fourth level; a secondary element louder than the focal one; the primary action far from the decision |
| 3 | Layout | one alignment rule per axis; gaps step down with nesting; measure ≤ 80ch; no page-level horizontal scroll; table and toolbar have a mobile shape | horizontal overflow at 390; content cut off; a table unusable on the phone | misalignment; same gap at every level; measure over 80ch |
| 4 | Type | ≤ 2 families; one scale and ratio; nothing < 12px; line height 1.2 headings, 1.45–1.55 body; weights regular + one | content text < 12px; uppercase tracked labels as the hierarchy device | a third family; line height or weight outside the rules; body > 80ch |
| 5 | Colour and contrast | tokens only; neutrals tinted consistently; accent ≤ 3 uses per screen; text ≥ 4.5:1, controls ≥ 3:1, placeholders ≥ 4.5:1 in both themes (computed); status never by colour alone; native controls `accent-color` from the tokens | any text or placeholder pair < 4.5:1 or control < 3:1; colour-only status, selection or error; a colour literal outside the token file in a design folder; a status hue used for a non-status action | elevation lost in dark; soft fills muddy; `accent-color: auto`; status solid used as text |
| 6 | Spacing and density | spacing from the scale; density matches the frequency of use; 24px targets, 8px gaps, 44px for phone primary actions | a primary control under 24px; controls touching | a primary action under 44px on a phone-first screen; density wrong for the frequency |
| 7 | States | every control: hover, focus-visible, active, disabled, invalid; every data view: loading, empty, error, drawn in `states.html`; selection distinct from hover; destructive actions distinct | focus invisible or `outline: none` without replacement; a destructive action styled as primary or without confirmation when irreversible | a missing loading, empty or error state; a state in the spec but not drawn; selection equal to hover |
| 8 | Accessibility | landmarks, one h1, heading order, labels on inputs, alt on meaningful images, tab order = reading order, reduced motion honoured, no information in hover only | a control unreachable by keyboard; an unlabelled input; hover-only information; motion that cannot be turned off | heading order broken; an empty table header; a decorative image with alt text |
| 9 | Copy | heading states the situation; buttons verb + object, same verb through the flow; errors say what and how to fix; empty states say what next; sentence case; user words; counts add up; no chat voice | a label or button that misstates what happens; chat voice or a maker's note in UI copy; counts that contradict the rows | "Submit"/"OK"; a page name as the heading; an error without the fix; a placeholder that reads as a value |
| 10 | Generic look | the frontend skill's list, plus the default-console shape from `craft.md` (status-edged cards above a table with nothing else to say) | three or more list items present; a named product's UI or brand reproduced | one or two list items; no memorable element |
| 11 | Directions and consistency | several directions differ in ≥ 2 of layout, hierarchy, primary action, navigation, with the same fixture; several screens share header, nav, badges, table density, button styles, one token set | a pair of directions equal in 3 of 4; a different primary colour or navigation model between screens of one design | a different fixture; a shared part that differs between screens (badge, density, button) |
| 12 | Spec, tokens, privacy | `spec.md` matches the HTML both ways incl. behaviour; `Maps to` backticked paths exist; acceptance checks runnable alone; `tokens.css` values are the ones used and equal between root and final; handoff self-contained; no PII, secret, client name, internal host, absolute path or chat reference anywhere; application code untouched | spec contradicts the HTML on a component, state, behaviour or copy; any PII, secret, internal host or absolute path; application files changed by the design | spec omits a component, state or string the HTML has; a `Maps to` path missing; an acceptance check that needs the spec's context; tokens drift between root and final; handoff not self-contained |

## Severity
| Level | Meaning |
|---|---|
| Must | a user will misread, miss or fail the job, an accessibility or privacy rule is broken, or an implementer would build the wrong thing: the "Must when" column |
| Should | the screen works but reads worse, slower or less consistently than it could; something an implementer would have to invent: the "Should when" column |
| Other | optional, at most 5: taste with a reason, a token worth renaming, a later idea |

- Every finding: place (screenshot path + region, selector or `file:line`) · what (quoted or measured) · why (the job or the rule) · fix (one line) · and, for a Must, whether the fix is **local** (one rule, one token, one string, one attribute) or **structural** (a region moves, a component changes shape, a navigation model changes).
- Measurements come from `screenshot.py` WARN/KEYS lines, `check_design.py` output, or the checker's contrast functions run by hand; a ratio or size stated without one of these is not a finding.
- A `FAIL` of `check_design.py` is a Must candidate; read it in context (an example row in a template is not PII; an external URL in a comment is still a FAIL).

## Verdict (complete: exactly one row applies)
| Verdict | When |
|---|---|
| Ship | no Must |
| Fix first | one or more Must, every one with a local fix, and none in area 1 or a privacy Must in area 12 |
| Redesign | any Must in area 1 (the screen answers the wrong job), any privacy Must, or any Must with a structural fix; recommend `darshan-singh-meel-design` with the findings as the brief's keep/change/remove table |
The number of Must findings never decides the verdict on its own: ten one-line fixes are "Fix first"; one moved region is "Redesign".
