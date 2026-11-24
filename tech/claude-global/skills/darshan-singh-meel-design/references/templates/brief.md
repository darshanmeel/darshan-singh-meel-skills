# Brief: NAME
Mode: new design | redesign | design system · Route: design canvas | local canvas | both · Stack: plain HTML | React | Streamlit
Status: round 1 | round N | final

## Job
- Product: <what it is, for whom>
- User: <role, how often, on what device>
- Main job of the screen(s): <one sentence per screen, the thing the user comes to do>
- Top 3 questions or actions: 1. … 2. … 3. …

## Screens
| Screen | Job | Entry from | Leads to | Shared parts |
|---|---|---|---|---|
| Runs | see what failed and why | nav | Run detail | header, nav, status badges |

## Inputs
- Screenshots: `before/<file>.png` → <screen> (inferred: regions, components, approximate colours and type; inference, not measurement) · or "Before image: pasted, not on disk"
- Chrome route: material list as approved · files saved to `imports/` · "Tool UI read live; not verified against documentation"
- Existing code: <relative paths of pages, components, tokens, theme files> · Existing tokens: <file or "none">
- Design system: extract from code | create | given (<file>)

## Constraints
- Fonts: system stacks (no network) | fonts already in the project: <names, files>
- Devices: desktop | phone | both
- Viewports: desktop 1280 · phone 390 (the chosen devices only; + tablet 834 when the app is used there)
- Themes: light and dark
- Must keep: <navigation, component library, brand colour, …>
- Accessibility: WCAG AA, keyboard, reduced motion

## Redesign: keep / change / remove
| Element | Decision | Reason (from the job, not taste) |
|---|---|---|
| Left nav | keep | users know it; 8 destinations fit |
| KPI cards ×6 | change → 3 | only 3 answer the top questions; the rest hide the table |
| Decorative gradient header | remove | 180px without information above the fold on mobile |

## Directions (round 1)
| Key | Name | The bet | Layout | Hierarchy (first, largest) | Primary action |
|---|---|---|---|---|---|
| A | … | … | … | … | … |

## Decisions log
- Round 1: <which direction, mix, and the comments that drove round 2>
