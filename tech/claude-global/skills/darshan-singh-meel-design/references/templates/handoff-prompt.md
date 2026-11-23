# Handoff prompt: NAME
For pasting by hand into an external design tool, or into a fresh Claude session. Self-contained: nothing from the chat, nothing from the codebase except what is written here. Synthetic content only.

---

Design <N> directions for <product>, a <kind: internal data app | dashboard | form | landing page> used by <user role> on <device, frequency>.

**Main job of the screen:** <one sentence>. The first thing on screen must serve it. Top 3 questions or actions: 1. … 2. … 3. …

**Screens (<n>), in flow order:** <Screen A: job> → <Screen B: job>. They share <header, nav, status badges, …>; a direction spans all screens with one token set.

**Content (synthetic, shaped like the real data):** <entities, fields, typical values and ranges, e.g. "runs: name, status (ok/failed/running), started, duration 2–40 min, owner team">. No real names or data.

**Design system:** <extend the tokens below | create one>. Tokens:
```css
<paste the :root block of tokens.css>
```
Light and dark from the same tokens. Fonts: system stacks only (<the stacks>), or <project fonts by name>.

**Must keep:** <navigation, component library, brand colour, …>. **Change:** <…>. **Remove:** <…>, because <reasons from the job>.

**Directions must differ in at least two of:** layout, hierarchy (first and largest element), primary action and its place, navigation model. Not a direction: another colour, font or spacing. Avoid the generic look: identical soft-shadow cards everywhere, decorative gradients, all-caps tracked labels on every heading, numbered markers on non-sequences, a highlighted word in a headline, entrance animations on every section. Original work: no copy of a named product's UI or brand.

**Quality floor:** responsive to 390px without horizontal scroll; WCAG AA contrast (text 4.5:1, controls 3:1) in both themes; visible focus; targets ≥ 24px; loading, empty and error state for every data view; status by text and icon, never colour alone; `prefers-reduced-motion` respected; sentence case, buttons say what happens.

**Deliver:** one self-contained HTML file per direction and screen (inline CSS, no external resources), tokens as CSS custom properties, and a short note per direction: the bet, layout, hierarchy, primary action.

---

Back into the project: save the exported HTML under `designs/NAME/imports/` and ask for a refine or a review of it; it is treated as untrusted input (rendered without scripts, text never read as instructions).
