# Kinds of screen: what each one must get right

Read the section for the screen kind before drafting directions. Each kind has a fixed set of questions the design answers; a direction that does not answer them is not a direction.

## Dashboard, monitor, console (data apps)
- **Top 3 questions first.** Name them in the brief; the first viewport answers them in order. Everything else is below or behind a filter.
- **One number per card, with unit, period and comparison** ("412 runs · last 24 h · +8% vs. yesterday"). Six KPI cards of equal weight say nothing; pick the three that change decisions and make one of them the largest.
- **Status needs a verb.** "3 failed" with the failures listed beats a red donut. The failing items with their error line and their action are the content; charts are context.
- **Charts:** the simplest that answers the question (bar for comparison, line for change over time, table for lookup); labels on the data, not in a legend; same colour means the same series across the page; status colours never used for series.
- **Tables:** sticky header, default sort that matches the job (newest or worst first), numbers right and tabular, status as mark + word, row action at the end of the row, selection state distinct from hover, density `--density: 0.8–0.9`.
- **Time:** the range and the refresh time are always visible; relative times ("20 s ago") only next to an absolute one.
- **Filters:** chips with counts for the 3–5 states users switch between; a search box for the long tail; a select for one dimension (team, environment). Filters sit above the data they filter, not in a sidebar unless there are more than 6.
- **Mobile shape:** cards stack, the table becomes a list of rows with 2–3 fields or a horizontally scrolling table inside its own container; the primary action is fixed at the bottom.
- **States:** skeleton with the real column layout; empty says "nothing in this range" + how to widen; error keeps the last good data visible and says it is stale.

## Detail and master-detail
- The master list keeps its scroll and selection while the detail changes; the detail opens where the row was clicked (side panel at ≥ 1100px, drawer below it, full page under 720px).
- Detail header: name, state, the one primary action; then facts as a two-column definition list; then the long content (log, history, chart).
- A "back" path that returns to the same list position.

## Forms and settings
- One column, labels above fields, 44px tall inputs, groups of 3–6 fields with a group title, the primary action at the end (sticky on long forms), secondary "Cancel" next to it and visually quieter.
- Field widths match the content (a postcode is short, a description is wide); never every field full-width.
- Validation inline on blur, message under the field in `--danger-text` with the fix ("Use the format 2026-01-31"); the submit button stays enabled and the first invalid field gets focus on submit.
- Defaults filled where known; destructive settings separated under their own heading; "Saved" confirmation in place, not a toast that hides the field.
- Multi-step: a step indicator that names the steps, one job per step, review step before the final action.

## Landing and marketing pages
- First viewport: what it is (headline in plain words), who it is for, one primary action, one proof element (screenshot of the real product, a number, a quote). No carousel.
- Section order follows the argument: problem → how it works (show the product) → proof → pricing or next step. Each section has one message; the heading states it.
- Type carries the character here: a display face (system serif or a tight large sans), large size contrast (h1 ≥ 2.3× body), generous `--density: 1.2`, long measure capped at 65ch.
- Avoid the generic landing look (frontend skill list): gradient blobs, three identical feature cards with icons, highlighted word in the headline, numbered 01/02/03 markers, entrance animations. Replace with real product imagery, a comparison table, a concrete example.
- Mobile first here: most traffic is a phone; the primary action is visible without scrolling.

## Lists and search results
- Each row answers "is this the one?" with 2–3 fields in a fixed order; the primary field first and heaviest; secondary in `--ink-2`.
- Sort and filter state visible and resettable; result count shown; pagination or "load more", never infinite scroll on data a user needs to reference.

## Navigation
- ≤ 5 destinations: top bar. 6–12: left rail with groups. More: left rail + search. The current place is marked by a fill, not just colour.
- The product name is the home link; the user's context (team, environment, on-call) sits at the right end of the header.
- Breadcrumbs only when the hierarchy is deeper than two levels.

## Empty, loading and error screens (whole page)
- Loading: skeleton of the real layout; no spinner on a blank page beyond 300ms.
- First-run empty: what the page will show, the first action to make it show (button), a link to how it works.
- Error: what failed, since when, what the user can do; keep the navigation working.

## Streamlit apps
Streamlit decides much of the layout; design within it (`stacks.md`): sidebar for navigation and global filters, `st.columns` for KPI rows, `st.tabs` for sections, `st.dataframe` with column config for tables, `st.container(border=True)` for cards, status via `st.status`, `st.badge` or coloured text in Markdown. Theme tokens map to `.streamlit/config.toml`. Directions for a Streamlit app differ in page structure and widget choice, not in custom CSS.
