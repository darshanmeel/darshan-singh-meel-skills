# Craft: what makes a screen good

Rules that produce a design a user trusts at first glance. `darshan-singh-meel-frontend` is the floor (its generic-look list, quality floor and UI words apply); this file is how to get above it.

## Composition
- **One focal point per screen.** The element that serves the main job is the largest, highest-contrast or first thing; everything else steps down. Two focal points = none.
- **Reading order = job order.** Left-to-right, top-to-bottom follows what the user does: see → decide → act. The primary action sits where the decision ends (end of a card, end of a form, right of a row), not in a toolbar far away.
- **Group by proximity before boxes.** Space (a `--space-5` gap) separates groups better than borders. Use a border or surface when the group has a different behaviour (selectable, scrollable, a different state), not to decorate.
- **Alignment is one rule per axis.** Text left, numbers right, one left edge for labels. A misaligned 2px reads as sloppy before anyone can say why.
- **Margins step down with nesting.** Page `--space-5`, card `--space-4`, inside a card `--space-2/3`. Never the same gap at every level.
- **Max line length 60–80 characters** for prose; tables and forms are exempt. Set `max-width` on text columns, not on the page.
- **Above the fold is the whole story.** At 1280×800 and 390×844, what is visible without scrolling must answer the top question. Check it in the screenshots, not in the head.

## Hierarchy
- Three levels are enough: primary (h1 and the focal element), secondary (section titles, key values), tertiary (meta, labels). Every element belongs to one; if it is hard to tell, lower it.
- Build hierarchy with size, weight and colour together, in that order of strength. A tertiary label is smaller and `--ink-2`, not bold; a heading is larger and tighter (`--tracking-tight`), not uppercase.
- Numbers that answer a question are large and tabular; their units and time range sit next to them in `--ink-2`. A number without unit or period is noise.
- Emphasis is scarce. One accent colour, used for the primary action and the selected state only. Status colours only for status. If the accent appears more than three times on a screen, it is no longer an accent.

## Type
- Two families at most: UI sans + a monospace for ids, times, codes, durations (tabular numerals align columns). A display face only for landing pages or when the brand asks.
- Scale from one base with one ratio (1.2 minor third for dense apps, 1.25–1.333 for landing pages); nothing on screen below 12px; body 14–16px in apps, 16–18px for reading.
- Line height: 1.2 for headings, 1.45–1.55 for body, 1.3 for table cells. Letter spacing: tighten large headings slightly (−0.01em), never widen lowercase text.
- Weights: regular and one of medium or semibold. Bold everywhere is no hierarchy.
- Character without webfonts (`tokens.md`): the system serif stack for a display heading, monospace for data, tight tracking on large numerals, generous size contrast between h1 and body, one deliberate large element.

## Colour
- Work in OKLCH: lightness (L) steps look equal across hues, so one ramp recipe serves every hue. Neutrals carry a trace of the accent hue (chroma 0.004–0.02) so the screen feels like one thing; pure grey next to a tinted surface looks dirty.
- Palette roles, not palette size: `--bg` (page), `--surface` (cards, inputs), `--surface-2` (hover, table header), `--border`, `--border-strong` (controls), `--ink`, `--ink-2`, `--ink-3` (disabled), `--accent` + `--accent-ink` + `--accent-soft`, four status hues each as solid + `-soft` + `-text` + `-ink`.
- Light theme: bg L≈98%, surface 100%, ink L≈22%, accent L≈45–55% at chroma 0.15–0.2 for 4.5:1 on white. Dark theme: bg L≈16%, surface 20%, ink L≈94%, accent L≈75–80% at lower chroma (bright saturated colour vibrates on dark). Never invert the light palette; dark surfaces get *lighter* with elevation, shadows disappear, borders carry depth.
- Status: green ≈ hue 150, amber ≈ 70–80, red ≈ 25, blue ≈ 240. As text on `--bg` they need 4.5:1 (darker variants in light, lighter in dark); as badges use `-soft` fill + `-text`; as solid fills use `-ink` on top. Never status by colour alone: always a word or icon.
- Contrast is computed, not eyeballed: `check_design.py` reports every token pair; fix the token, not the single use.
- Large flat colour areas (hero bands, coloured headers) must carry information (a state, a section) or go.

## Density
- Density follows how often the user looks: a console seen 20 times a day is dense (row 32–36px, `--density: 0.8–0.9`, 13–14px); a form filled once a month is airy (row 44px, 15–16px); a landing page is generous (`--density: 1.2`).
- Dense does not mean cramped: keep `--space-3` between controls and 24px targets; cut decoration, chrome and repeated labels instead of whitespace.
- Tables: header sticky, row height constant, numbers right and tabular, one row of secondary text at most, long text ellipsized with the full text on hover or in a detail panel.
- Show the data at real volume: 8–15 rows, long names, a 2-line error, an empty column. A design judged on three short rows breaks on day one.

## Interaction states
- Every control has: default · hover (`--surface-2` or a brightness step, 100–150ms) · focus-visible (2px `--focus` ring, 2px offset; never `outline: none` without a replacement) · active (pressed, slightly darker) · disabled (`--ink-3`, `--border`, no hover, cursor default) · and, for inputs, invalid (`--danger` border + message below, with the fix).
- Selected state is different from hover (`--accent-soft` fill or a left bar) and survives when the pointer leaves.
- Every data view has: loading (skeleton with the real layout, header stays), empty (what it means + the next action), error (what happened + retry), and partial (some rows failed to load) when the API can do that.
- Destructive actions: secondary style, confirmation only when irreversible, undo when possible.
- Touch: 44px targets for primary actions on phone screens, 24px minimum everywhere, 8px gaps between adjacent targets.

## Motion
- Motion shows what changed: a row that appears, a panel that slides from where it was invoked, a value that updates. Durations: 100–150ms for hover and toggles, 200–250ms for panels, nothing on a UI response above 300ms.
- One easing (`--ease`, ease-out shape) for entering; ease-in for leaving. No bounce, no entrance animation on page load, no parallax, no hover scale on cards.
- `prefers-reduced-motion: reduce` sets durations to 0; state changes still happen instantly.

## Point of view
A screen that passes every rule above can still be the default console: a status-edged card row above a table, near-white ground, one blue accent, nothing anyone remembers. The rules are the floor; the point of view is the design.
- **One memorable element per direction**, named in `data-pitch` and the critique: the thing a user would describe to a colleague. A headline that reads like a sentence ("3 failed, 1 late"), a time axis instead of a list, a number set so large it is the page, an error line in the user's own log format, a detail panel that never leaves the list, a single colour used once at full strength.
- **Type carries character cheaply.** A serif display face for the situation line against monospace data; numerals twice the body size; one weight contrast instead of five. The template's system stacks already contain a serif and a monospace (`tokens.md`).
- **Ground is not always white.** Light theme surfaces at L 97–98% with a visible accent tint, or a deep ground with light cards for a tool used at night; the recipe in `tokens.md` gives both. Decide per direction and say why in the pitch.
- **Structure before decoration.** Character comes from what is first and largest, from an axis (time, severity, ownership) the layout follows, and from one bold typographic move; never from gradients, icons or a third colour.
- **The default-console check:** if a direction can be described as "cards above a table" or "sidebar, table, panel" with no further words, it has no point of view yet. Add the element or drop the direction.

## Copy inside the design
- The heading states the situation ("3 failed, 1 late"), not the page name. The page name goes in the nav.
- Buttons: verb + object ("Retry run", "Save changes"), the same verb through the flow; primary once per view.
- Empty and error states speak to the user about their data; no apologies, no exclamation marks.
- Fixture content is synthetic but plausible: realistic names (`finance_close_daily`), ranges, one long value, one edge case per view. Never lorem ipsum, never a real customer, never a real colleague.

## Self-critique (before the user sees it)
Look at the screenshots at 1280 and 390, light and dark, and answer in `critique.md`:
1. What does the eye land on first? Is it the job? If not, what is louder than it should be?
2. Which element could be deleted without losing information? Delete it.
3. Where do two things look the same but mean different things (or the reverse)?
4. Which generic-look item from the frontend skill's list is present? Replace it.
5. What breaks at 390: overflow, a stacked toolbar, a table with no mobile shape, a target under 24px?
6. What breaks in dark: shadows gone, images too bright, status soft fills muddy, pure black text?
7. Does the copy name the job or the system? Do the counts add up to the rows shown?
8. What is the memorable element? If the answer is "the cards" or "the table", the direction has no point of view yet.
9. Is the fixture possible? Start + duration ends before the clock in the header; counts in the headline equal the rows; the same run has the same times, state and numbers on every screen and in every round.
10. Do repeated cards or rows still align when their content lengths differ (a long button label, a two-line error, a missing field)? Put variable-length parts on their own line and keep actions on one edge.
Fix what the answers show before building the canvas again; keep the critique as a file in the round.
