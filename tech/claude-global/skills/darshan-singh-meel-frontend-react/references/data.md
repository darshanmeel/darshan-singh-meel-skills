# Data fetching, routing, tables, charts

## Fetching
Docs: tanstack.com/query/latest/docs/framework/react/installation
- One thin API client in `lib/api.ts`: base URL from env, `fetch`, throw on `!res.ok`, parse the body with a zod schema. No HTTP library for this.
- Server data goes through **TanStack Query**: `useQuery({ queryKey, queryFn })` for reads, `useMutation` for writes, then invalidate the affected keys.
- One `QueryClient` + `QueryClientProvider` in `main.tsx`.
- Query keys: arrays that hold every input, `['orders', { status, page }]`. Keep key builders next to the fetch functions.
- Render all three states: `isPending` → skeleton, `error` → message + retry, empty data → empty state.
- No fetch in `useEffect`. No parent-then-child request waterfalls: fetch in parallel or prefetch in the router loader.
- Search-as-you-type: debounce the input, pass the query's `signal` to `fetch` so stale requests cancel.
- Large lists: paginate or filter on the server; never ship thousands of rows to filter in the browser.
- Auth: session cookie (`HttpOnly`, `Secure`, `SameSite`) or the identity provider's SDK. No tokens in `localStorage`.
- Never `dangerouslySetInnerHTML` with data from the API or the user; never build URLs from unchecked input.
- Version flag: confirm the TanStack Query major on its site before pinning.

## Routing
- One screen → no router. Tabs or filters only → URL search params.
- Several screens → TanStack Router (typed params and search params, loaders) or React Router; react.dev recommends both. Next.js → its file router.
- Lazy-load routes that are heavy or rarely visited; nothing else.

## Tables
Docs: tanstack.com/table/latest
| Need | Use |
|---|---|
| Static, under ~100 rows | plain `<table>` with the library's table styles |
| Sort, filter, paginate, select, column visibility | TanStack Table (headless) rendered with the library's table parts |
| Thousands of rows on screen | server pagination first; row virtualization only if that can't work |

- Real `<table>`, `<th scope="col">`, a `<caption>` or `aria-label`; sortable headers are buttons, with `aria-sort` on the `<th>`.
- Column definitions outside the component (or stable), so they aren't rebuilt each render.
- Sort, filter, and page state in URL search params when the view should be shareable.
- Big data set → sort, filter, and paginate on the server: table in manual mode, its state in the query key.
- Format with `Intl.NumberFormat` / `Intl.DateTimeFormat`, one formatter per kind in `lib/format.ts`.
- Version flag: TanStack Table v9 is current and its API differs from v8. Match the installed major; don't mix examples.

## Charts
Docs: ui.shadcn.com/docs/components/chart
- Chart choice and styling: `darshan-singh-meel-frontend`.
- Default: shadcn chart (`npx shadcn@latest add chart`, Recharts underneath); colors from theme CSS variables, so light and dark both work.
- Shape and aggregate data in the API or one pure function, not inside the chart JSX.
- Every chart: title, units, time range, and a text alternative (`aria-label` summary or a table toggle).
- A single number or a tiny trend needs no chart library: text or inline SVG.
