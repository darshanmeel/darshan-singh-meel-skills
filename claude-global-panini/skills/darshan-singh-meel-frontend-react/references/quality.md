# Accessibility and tests

## Accessibility
The floor (contrast, focus, reduced motion, responsive) is in `darshan-singh-meel-frontend`. React specifics:
- **Semantic element first:** `<button>` for actions, `<a href>` for navigation, `<nav>` / `<main>` / headings in order. Never a clickable `<div>`.
- **Interactive widgets** (dialog, menu, combobox, tabs, tooltip, popover) come from the library's primitives (Radix handles ARIA, focus trap, keyboard). Don't hand-build them.
- Icon-only button → `aria-label`. Decorative icon → `aria-hidden`.
- Dialog: focus moves in on open and back to the trigger on close; `Esc` closes.
- Route change: move focus to the new page's `<h1>` and update `<title>`.
- Async updates (saved, error, result count): announce with `aria-live="polite"` or the library's toast.
- Loading: `aria-busy` on the region; skeletons hidden from screen readers.
- Lint with `eslint-plugin-jsx-a11y`; it catches the cheap mistakes.
- Automated checks find only part of WCAG. Always do a keyboard-only pass: tab order, visible focus, no trap.

## Tests: few, at the right level
| Level | Tool | Test |
|---|---|---|
| Pure logic (formatters, schemas, reducers) | Vitest | inputs → outputs, edge cases |
| Component behaviour | Vitest + Testing Library | what the user sees and does: render, type, click, assert text |
| Key flows end to end | Playwright | 3–5 journeys that must never break (sign in, main task, save) |
| Accessibility | `@axe-core/playwright` | no violations on each main screen |

Docs: vitest.dev/guide · testing-library.com/docs/react-testing-library/intro · playwright.dev/docs/intro · playwright.dev/docs/accessibility-testing

- Setup: `npm i -D vitest @testing-library/react @testing-library/dom` plus a DOM environment (jsdom); Playwright via `npm init playwright@latest`.
- Query by role and label (`getByRole('button', { name: 'Save changes' })`), the way a user finds things. `data-testid` only as a last resort.
- Test behaviour, not implementation: no assertions on state, hooks, or class names. No snapshot tests of whole components.
- Mock at the network edge (stub `fetch` or the API client), never the component's own hooks. Fresh `QueryClient` (retries off) per test.
- Fixtures are synthetic and small; no copied production data.
- Axe check:
```ts
const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
expect(results.violations).toEqual([]);
```
- After a change: run the tests for the changed files (`npx vitest run <path>`), then ask once about the full suite.
- Version flag: Vitest 5 needs Vite 6.4+ and Node 22.12+. Confirm the jsdom setup and `@testing-library/user-event` on their sites.
