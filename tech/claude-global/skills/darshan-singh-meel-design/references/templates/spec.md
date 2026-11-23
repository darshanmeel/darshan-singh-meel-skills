# Spec: NAME
Design: `designs/NAME/final/index.html` (+ one file per further screen) · States: `designs/NAME/final/states.html` · Tokens: `designs/NAME/final/tokens.css` · Stack: <React | Streamlit | plain HTML>

<Lede: what this screen is, for whom, and the one bet the design makes, in one sentence. A second sentence names what changes for the user.>

Implement from this file and the HTML alone. Where the HTML and this spec differ, the spec wins; say so in the implementation notes. Every state named below is drawn in `states.html`; every copy string is in the Copy table.

## Layout
- Regions, in reading order: <header → filter bar → main table → detail panel>; what sits above the fold at 1280×800 and at 390×844.
- Grid: <columns, gutters in tokens, max width>; alignment rule: <e.g. numbers right-aligned, labels left>.
- Hierarchy: the first element the eye meets is <…> because the job is <…>.

## Components
| Component | Variant(s) | Content | Tokens | Maps to existing |
|---|---|---|---|---|
| Status badge | ok · warn · danger · info; solid (counts) · soft (rows) | text + icon, never colour alone | `--ok-soft` + `--ok-text`, `--radius-full` | `src/components/Badge.tsx` (extend variants) |

## Behaviour
| Element | Trigger | What happens | Counts and labels | Focus afterwards |
|---|---|---|---|---|
| Filter chip "Failed" | click, Enter, Space | rows narrow to failed; chip `aria-pressed=true`; URL `?status=failed` | h2 count updates; "All" chip shows the total | stays on the chip |
| Retry button | click | request sent; label "Retrying…", disabled; on success the card fades out over `--motion` and the counts update; on failure an inline error under the card | h1 "<n> failed" decreases | the next card's primary button, or the h1 when none is left |
| Search | input, 200 ms debounce | rows filter by pipeline and owner; "No runs match" when empty | result count under the field | stays in the field |
- Default sort: <newest first>; the sort column and direction are visible.
- Async outcomes: loading <skeleton>, success <in place, no toast>, failure <inline message with the fix and a Retry>.

## States
| View | Loading | Empty | Error | Success / other |
|---|---|---|---|---|
| Runs table | 8 skeleton rows, header stays | "No runs in the last 24 h" + "Widen the time range" | "Could not load runs — retry" with a Retry button | row hover, selected row |
Interactive states for every control: default · hover · focus-visible (`--focus`, 2px, offset 2px) · active · disabled (`--ink-3`, no pointer) · invalid (`--danger` border + message below with the fix). All drawn in `states.html`.

## Responsive
| Width | What changes |
|---|---|
| ≥ 1280 | <full layout> |
| 720–1279 | <detail panel becomes a drawer; 3 KPI columns → 2> |
| ≤ 719 | <one column; table → cards or horizontal scroll inside the table only; primary action at 44px> |
No page-level horizontal scroll at 390.

## Accessibility
- Landmarks: one `<main>`, one `<h1>`, `<nav aria-label>`; heading levels in order.
- Focus order: <the sequence>; focus never trapped; skip link when the nav has more than 5 items.
- Contrast: text 4.5:1, controls 3:1 in both themes (checked from tokens; `check_design.py` 0 FAIL).
- Targets ≥ 24×24 px (44 on touch-first screens); labels on every input; status by text + icon, not colour alone; `accent-color: var(--accent)` on native controls; placeholders ≥ 4.5:1 or replaced by helper text.
- Motion: `--motion` only on user-caused change; `prefers-reduced-motion` turns it off.

## Copy
| Where | Text |
|---|---|
| h1 | <…> |
| Primary button | <verb + object, e.g. "Retry failed runs"> |
| Empty state | <…> |
| Error | <what happened + how to fix it> |
| Labels, placeholders, helper text | <every string, including hints and legends> |

## Motion
- <element>: <property> over `--motion` with `--ease`, triggered by <action>. Nothing else moves.

## Tokens → project
- `designs/NAME/final/tokens.css` → <project token file, or `.streamlit/config.toml [theme]` mapping: primaryColor = `--accent`, …>.
- Fonts: <system stack as in tokens | project fonts: file paths>.

## Maps to
| Design element | Existing file or component (relative path) | Change |
|---|---|---|
| Header | `src/components/AppHeader.tsx` | keep; new primary action slot |
| Runs table | `src/pages/Runs.tsx` | restructure columns per Layout |
| Detail drawer | to create: src/components/RunDrawer.tsx | new component |
Paths in backticks must exist in the project; files to create are written without backticks, prefixed "to create:".

## Acceptance checks
Each check names the file, the viewport and the value, so it can be run without this spec's context.
- [ ] `screenshot.py final/index.html --viewports 1280x800,390x844 --themes light,dark --keyboard 20`: 0 WARN lines (overflow, targets, text size, labels, placeholder, accent-color, focus)
- [ ] KEYS line at 1280 light lists, in order: <nav links → primary action → chips → search>
- [ ] `check_design.py designs/NAME --final`: 0 FAIL
- [ ] `states.html` shows, for every view in States: loading, empty, error (count: <n> frames)
- [ ] in `index.html` at 1280×800 <job-specific, e.g. every failed run of the fixture is visible without scrolling>
- [ ] every string in the Copy table appears verbatim in the HTML or `states.html`
- [ ] no colour literal outside `tokens.css`; both themes render from the same markup

## Out of scope
- <what the design does not cover and who decides>
