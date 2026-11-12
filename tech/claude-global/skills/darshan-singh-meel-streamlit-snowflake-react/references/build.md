# Build: one self-contained file

Docs: vite.dev/config/build-options · vite.dev/guide/api-plugin

## Three build shapes: which fits
| Shape | Fits | Runtime | How |
|---|---|---|---|
| **One inlined file** `component/dist/index.html` | A new widget built for Streamlit | Warehouse (v1 `path=`), any (`components.html` string) | This file's `vite.config.ts`: `base: "./"`, inline plugin |
| **Frame folder** `frame/index.html` + `assets/` + bridge scripts | An existing SPA whose build serves another host (`base: "/"`, fonts as files) | Warehouse (v1 `path=`) | Keep the app's build; `build_bundle.py` copies `assets/`, rewrites CSS `url(/assets/…)` to relative, writes `index.html` with `data-bundle` (`spa.md`) |
| **Inlined strings** `js` / `css` / `html` passed to v2 | Container runtime, widget or SPA | Container (v2) | Widget: `vite.v2.config.ts` library build. SPA: bundle wrapped in `function startApp(){…}` + bridge; fonts → `data:` URLs in the CSS |
- One file is simplest when the source is ours: no paths to get wrong, one artifact line, works with both v1 mounts.
- The frame folder avoids a second build for an app that already ships elsewhere; large fonts stay separate files instead of base64 in one page.
- v2 has no file serving for inline components → strings or a package `asset_dir`.

## Layout (widget mode)
```
my_app/
  snowflake.yml            deploys only the files Python needs
  environment.yml
  streamlit_app.py
  widget.py                typed wrapper, declares the component
  component/
    frontend/              source: package.json, lock file, vite.config.ts, index.html, src/  (never deployed)
    dist/index.html        build output, committed, deployed
  tools/check_dist.py
  tests/test_widget.py
```
- Build output outside the source folder (`outDir: "../dist"`), so the source hash never includes its own output and the artifact list stays one line.
- `node_modules/` ignored in `component/frontend/.gitignore`.

## vite.config.ts (template)
| Setting | Why |
|---|---|
| `base: "./"` | Streamlit serves a component under its own sub-path; `"/"` → blank widget, 404 on the bundle |
| `outDir: "../dist"`, `emptyOutDir: true` | Stale hashed files never pile up |
| `inlineAll()` plugin | Moves the entry JS and CSS into `index.html` and deletes the separate files → one file that works with `path=` and as a `components.html` string; no static file serving needed |
| `assetsInlineLimit: 100_000_000` | Fonts and images become `data:` URIs inside the CSS |
| `cssCodeSplit: false`, `modulePreload: { polyfill: false }` | One CSS asset to inline; no extra preload script |
| `sourcemap: false` | Maps would double the file and expose source |
| source-hash `<meta>` | `check_dist.py` recomputes it; a source change without a rebuild fails |
| `test: { environment: "jsdom", pool: "threads" }` | Vitest in the same config; threads because the forks pool can time out starting workers on Windows |

- The inline plugin escapes `</script` inside the bundle; without that a string in a library can end the tag early.
- No dynamic `import()` in the widget: a second chunk would be a file the inlined page can't load, so both Vite configs stop the build on it.
- Checked: the template builds to one `index.html` of ~146 kB and `widget.js` of ~215 kB (React included) with Vite 6; written for Vite 8. A Vite major changes plugin hooks → rerun the build and `check_dist.py`.
- Container-only apps still run `npm run build`: the source hash lives in `dist/index.html`, and the v1 build is what local tests mount.

## Self-contained means
- No `<script src>`, `<link href>`, CSS `url(http…)` or `@import` of another site. Allowed: `data:` URIs and `#` anchors.
- No `eval()`, `new Function()`: the CSP blocks them. Some chart or template libraries use them → pick another, or check the bundle with `check_dist.py` before adopting one.
- Fonts: system stack by default. A brand font → npm `@fontsource/<family>` (latin subset only) or a local `.woff2` with its licence file beside it, imported from CSS so Vite inlines it.
- Icons as inline SVG components, not an icon font from a CDN.
- No analytics, error-reporting or feature-flag SDKs: each calls out.

## Size
- Warehouse runtime: 32 MB per backend↔frontend message, not configurable. The static mount sends the whole page on every rerun; the args always travel.
- Budget: page ≤ 2 MB (`MAX_BYTES` in `check_dist.py`), args ≤ a few hundred kB. React + ReactDOM ≈ 140 kB minified.
- Over budget → drop a dependency (date, chart or UI kit), import per function, subset fonts. Full Tailwind + shadcn is usually too heavy here; plain CSS + a few Radix primitives.
- Stage file-size limits for app files: not documented on the SiS pages; one small file avoids the question.

## Committed build, source hash
- The build is committed, so the deploy needs no Node and CI deploys exactly what was reviewed.
- Hash = sha256 over every file git tracks in `component/frontend/` (path, NUL, bytes with CRLF read as LF, NUL), first 16 hex. The same in `vite.config.ts` and `check_dist.py`.
- Order: `git add component/frontend` → `npm run build` → commit source and `component/dist/` together. Untracked new files are not in the hash → `git add` before the build, or the build throws when nothing is tracked.
- Not a git checkout (zip download) → the check skips the hash with a note, never fails it.
- `.gitattributes`: `* text=auto eol=lf` keeps diffs clean; the hash already ignores CRLF.

## Python version
- `environment.yml` pins `python=3.11.*`; the wrapper uses `str | None`. On 3.9 or 3.10 add `from __future__ import annotations` or use `Optional`.
