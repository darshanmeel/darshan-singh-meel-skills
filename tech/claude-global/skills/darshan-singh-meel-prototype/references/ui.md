# UI branch

Several structurally different variants of one screen, switched by `?variant=`, so the user flips between them in the browser and picks one or combines parts. Load `darshan-singh-meel-frontend` (design rules) and the build skill for the stack.

## Where the variants live
| Situation | Place | Run command |
|---|---|---|
| The screen, or the page it belongs on, exists (preferred) | on that page, behind `?variant=`; the page's data loading, auth and surrounding layout stay | the app's own dev command |
| The app exists, the screen has no home | a new route or page named `*prototype*`, in the project's routing convention | the app's own dev command |
| No app yet | `prototypes/<name>/index.html`, one self-contained file (`templates/ui/variants.html`) | `python -m http.server 8765 --directory prototypes/<name>`, then `http://localhost:8765/?variant=A` |
| Streamlit project, no fitting page | `prototypes/<name>/app.py` | `streamlit run prototypes/<name>/app.py` |

- Prefer the existing page: a variant is judged against the real header, navigation, density and data shape. An empty page hides problems.
- Files added to the real tree contain `prototype` in their names (`OrdersPrototypeVariants.tsx`, `orders_prototype.py`) and are listed in `NOTES.md`. The edit to the host page is one import and one mount line.

## Variants
- **Default 3. Minimum 2, maximum 5.**
- **Structurally different** = at least two of these differ between any two variants:
  - layout (table · master-detail · board · timeline · single column · split view);
  - hierarchy: what is largest and first;
  - primary action: what it is and where it sits;
  - navigation model (tabs · steps · one long page · drill-down).
- Not a variant: another colour, font, spacing, copy, icon set, or the same grid with other card sizes.
- Each variant: one component or function, a key (`A`, `B`, `C`) and a name that states its structure ("Table with side filter"). `NOTES.md` lists `- <key> - <structure>`.
- Variants share data and small parts (a button, a formatter); never a layout component.
- Same synthetic data in every variant, shaped by the real schema; realistic values, no lorem ipsum, no real rows, no PII.
- Read-only. An action that would write → a stub that changes local state and shows it.
- Loading, empty and error states only when the question is about them.

## Switcher
- Small bar, fixed at the bottom centre: previous · `B - Table with side filter` · next; wraps around. High contrast, clearly not part of the design.
- It writes the key to the URL (`?variant=B`), so a reload keeps the variant. Unknown or missing key → the first variant.
- Left and right arrow keys switch too, except while focus is in an input, textarea, select or contenteditable element.
- Never in a production build: render it only in development mode.

### React
- Project uses a router → its search-param API. React Router: `const [params, setParams] = useSearchParams()` from `react-router` (v6: `react-router-dom`; read `package.json`), `setParams({ variant: key })`. Next.js and TanStack Router: their own hooks - check: nextjs.org/docs, tanstack.com/router.
- No router → web platform only:
  ```tsx
  const KEYS = ["A", "B", "C"] as const;
  const [key, setKey] = useState(() => new URLSearchParams(location.search).get("variant") ?? "A");
  const pick = (k: string) => { history.replaceState(null, "", `?variant=${k}`); setKey(k); };
  ```
- Mount: `{key === "B" ? <VariantB data={data} /> : key === "C" ? <VariantC data={data} /> : <VariantA data={data} />}` plus `<PrototypeSwitcher keys={KEYS} current={key} onPick={pick} />`.
- Development only: Vite `import.meta.env.DEV` - check: vite.dev/guide/env-and-mode; other bundlers: the project's existing flag.
- The project's component library and tokens; no second library.

### Streamlit
- Streamlit 1.67 (docs.streamlit.io): a widget syncs itself with the URL through `bind="query-params"`; `key` is the parameter name.
  ```python
  VARIANTS = {"A": ("Table with side filter", variant_a), "B": ("KPI row, then chart", variant_b), "C": ("Master-detail", variant_c)}
  key = st.segmented_control("Prototype variant", list(VARIANTS), key="variant", default="A", required=True,
                             bind="query-params", format_func=lambda k: f"{k} - {VARIANTS[k][0]}")
  st.divider()
  VARIANTS[key][1](data)
  ```
- `required=True` (single mode) stops the user from deselecting, so `key` is never `None`.
- Pinned version without `bind` → `st.query_params` by hand (available since 1.30; values are strings):
  ```python
  key = st.query_params.get("variant", "A")
  picked = st.segmented_control("Prototype variant", list(VARIANTS), default=key, key="variant_pick")
  if picked and picked != key:
      st.query_params["variant"] = picked
      st.rerun()
  ```
- Check the project's pinned Streamlit against the version each parameter was added in - check: docs.streamlit.io, `st.segmented_control`, version selector. Streamlit in Snowflake lags: `darshan-singh-meel-streamlit-snowflake`.
- The control sits at the top of the page above a divider, or in the sidebar when the design under test does not use it. No CSS against Streamlit's DOM to make it float.
- Multipage apps: moving to another page clears query parameters, except those bound to a widget.
- Each variant is a plain function `variant_x(data)`; data comes from one synthetic-data function, cached only if slow.

### Plain HTML
- `templates/ui/variants.html`: one `<section data-variant="A" data-name="…">` per variant, inline CSS and JS, no CDN, no build step, no network.
- Per-variant styles are scoped by `[data-variant="A"]`.

## Hand-over
- Give the URL with each key. Ask which parts of which variant to keep: the usual answer is a combination.

## Clean-up (on the user's word)
- Rebuild the chosen structure properly under `darshan-singh-meel-frontend` + the build skill; do not rename a variant file into the real tree.
- Remove every file listed in `NOTES.md`, the mount line and the switcher; search the real tree for `prototype` and `variant=` to confirm nothing is left.
