# Components, state, effects

Docs: react.dev/learn · react.dev/blog/2024/12/05/react-19 · react.dev/learn/you-might-not-need-an-effect

## Components
- Plain function components, typed props (`type Props = {…}`), named exports, one main component per file.
- Split when a part is reused, has its own state, or the file passes ~150 lines. Not before.
- Props down, events up (`onChange`, `onSelect`). Pass `children` instead of drilling props through layers.
- Lists: stable `key` from the data, never the array index for lists that reorder or change.
- No class components, no higher-order components, no `forwardRef` in new code (React 19: `ref` is a normal prop).
- No `useMemo` / `useCallback` / `memo` by default; add only for a measured problem (or use the React Compiler).

## State: where it lives
| Kind | Put it in |
|---|---|
| One component | `useState` (`useReducer` when several values change together) |
| A few siblings | lift to the nearest shared parent |
| Server data | TanStack Query cache (never copied into `useState` or a store) |
| Shareable view state (filters, tab, page, sort) | URL search params |
| App-wide, rarely changes (theme, user, locale) | context |
| Shared and changed often from distant places | small store (Zustand) — only then; confirm its current API |

- Derive, don't store: anything computable from props or state is computed during render.
- Reset a subtree's state by changing its `key`, not with an effect.

## Effects
- Effects only sync with something outside React: a subscription, a browser API, a non-React widget.
- Not for: deriving data, reacting to a user action (use the event handler), fetching (use the query library or a loader).
- Every effect that subscribes returns a cleanup. External store → `useSyncExternalStore`.

## React 19 APIs worth using
| API | Use for |
|---|---|
| `useActionState(action, initial)` → `[state, submit, isPending]` | form submit with pending and error state (replaces `useFormState`) |
| `<form action={fn}>` · `useFormStatus()` | forms without manual handlers; submit button reads `pending` |
| `useTransition` | keep the UI responsive during an async update |
| `useOptimistic` | show the result at once, auto-revert on failure |
| `use(promise)` / `use(Context)` | read a cached promise under `<Suspense>`; read context conditionally. Never a promise created in render |
| `<Context value>` | provider without `.Provider` |
| `<title>`, `<meta>` in a component | page metadata, hoisted to `<head>` |

## Errors and loading
- One error boundary at the app root and one per independent region (a failed chart must not blank the page).
- `<Suspense>` with a skeleton that matches the final layout; no layout jump when data lands.

## TypeScript
- `strict` on; no `any`, no non-null `!` to silence errors.
- Derive types from zod schemas (`z.infer`) or the API client; don't hand-write them twice.
- Union of string literals over `enum`; discriminated unions for "loading / error / data" shapes.
