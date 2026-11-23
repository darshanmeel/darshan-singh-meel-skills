# Sources and verification status

No network fetches were approved while writing this skill. Status: **ran** = executed while writing · **own** = this skill's working default · **check** = from memory, not read on the page named; verify there before relying on it.

## Facts used and where to verify them
| Fact in this skill | Where to verify | Status |
|---|---|---|
| WCAG 2.x contrast: 4.5:1 for text, 3:1 for large text and for UI components and graphical objects (1.4.3, 1.4.11); target size minimum 24×24 CSS px (2.5.8, WCAG 2.2) | w3.org/TR/WCAG22 | check |
| Relative luminance and contrast ratio formulas (sRGB linearisation, 0.2126/0.7152/0.0722, (L1+0.05)/(L2+0.05)) as implemented in `check_design.py` | w3.org/TR/WCAG22, "relative luminance" and "contrast ratio" definitions | check (formula from memory; results match common online calculators on spot checks) |
| OKLCH → OKLab → linear sRGB matrices in `check_design.py` | bottosson.github.io/posts/oklab; developer.mozilla.org, `oklch()` | check (coefficients from memory; neutral greys and the accent round-trip to plausible hex) |
| Alpha compositing fg over bg (`over()`), `/ alpha` and 8-digit hex | developer.mozilla.org, `<color>` | check |
| CSS `light-dark()` and `color-scheme` as the one-definition theme mechanism; browser support | developer.mozilla.org, `light-dark()` | ran in Chrome 157 (frames, `::placeholder`); other browsers: check |
| `prefers-reduced-motion`, `prefers-color-scheme` media queries | developer.mozilla.org | check |
| Python Playwright: `sync_playwright`, `chromium.launch(channel="chrome"|"msedge")`, `emulate_media(color_scheme=…)`, `new_context(java_script_enabled=…, reduced_motion=…)`, `context.route("**/*", …)` with `route.abort()` / `route.continue_()` | playwright.dev/python/docs/api/class-browsertype, class-page, class-browsercontext, class-route | ran (channel `chrome`, Playwright for Python on Python 3.11, Chrome 157); `msedge` and bundled Chromium paths not exercised |
| Canvas 2D `fillStyle` accepts any CSS colour (incl. `oklch()`) and `getImageData` returns sRGB bytes: used by `screenshot.py` for placeholder contrast | developer.mozilla.org, CanvasRenderingContext2D.fillStyle | ran in Chrome 157 |
| `getComputedStyle(el, '::placeholder').color` returns the placeholder colour | developer.mozilla.org, `::placeholder` | ran in Chrome 157 |
| Chrome makes a scrollable region keyboard-focusable (appears as a Tab stop) | chromestatus.com, "keyboard focusable scrollers" | check (observed in the example's keyboard walk) |
| Streamlit theme keys in `config.toml` (`primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor`, `font`; newer `baseRadius`, `borderColor`, `linkColor`, `headingFont`, `codeFont`, `baseFontSize`, `[theme.sidebar]`, `[[theme.fontFaces]]`, dark theme config) | docs.streamlit.io, "Theming" and the `config.toml` reference, version selector on the project's pin | check |
| Streamlit widgets named in `stacks.md` (`st.badge`, `st.dialog`, `st.navigation`, `st.metric` `delta_color`, `st.dataframe` `column_config` and `on_select`, `st.container(border=True)`, `st.button` `type="tertiary"`, `st.skeleton`) and the version each needs | docs.streamlit.io API reference | check |
| shadcn/ui theme variable names (`--background`, `--foreground`, `--primary`…) | ui.shadcn.com/docs/theming | check |
| Claude in Chrome tools (`mcp__claude-in-chrome__*`), `claude --chrome`, file upload through the extension, the claude.ai/design UI | not documented here; the route reads the live page | check (unverified; the tools were not available while writing) |

## Ran while writing
- `tests/run.py`: 29 checks, 0 failed, with Chrome 157: checker false positives and negatives, calc()/none tokens, dark-block overrides, alpha, `-text`/`-soft` pairs, final-folder checks, gitignore parsing, apostrophes; canvas build with `</script>` and backslashes, Before column and placeholders, in-frame link and form guard, Reset labels, Pick export, column toggles, no overflow at 390; screenshot loopback stem sanitising, lookalike hosts refused, exit 2, meta-refresh handled, placeholder and accent-color measurements, distinct hover targets.
- `scripts/build_canvas.py` on the example rounds 1 and 2 with `--before` and `--screens Runs,Run`: Before column aligned by screen, System last and hidden by default.
- `scripts/screenshot.py` on the example rounds, `final/` and both canvases: 1280×800 and 390×844, light and dark, `--keyboard`; the measurements found and fixed a 57px overflow, 11.2px text, 10.2px list text, an 18px back link, a 405px states page, placeholder contrast read wrongly before the canvas-based colour parser.
- `scripts/check_design.py` on the example: 0 FAIL, 0 WARN; on planted errors every expected FAIL appeared (colour literals, filler, webfont URL, absolute path, real-looking e-mail, a token lightened to 2.55:1, a missing spec section, a structural twin).
- Canvas driven in headless Chrome from `file://`: viewports, theme, zoom, knobs, notes persisted in localStorage, export dialog, download, copy, Reset, an in-frame link click (frame stays `about:srcdoc`).

## Own defaults (not official)
- Token names and the knob set; the OKLCH recipe numbers; `--text-xs` floored at 12px; density scale; motion durations.
- "Directions differ in at least two of layout, hierarchy, primary action, navigation" (shared with `darshan-singh-meel-prototype`); "one memorable element per direction".
- Folder layout `designs/<name>/round-N/`, `final/` with `states.html`, `before/`, `imports/`; the `data-direction|name|screen|pitch` attributes; the spec and handoff sections.
- Checker thresholds: status solids on `bg` WARN below 4.5:1, FAIL below 3:1; `ink-3` WARN below 3:1; sizes and durations in px/ms as WARN; the structural-similarity heuristic (same ordered sequence of structural elements); the required screenshot subset (1280 light, 390 light, 1280 dark per file); internal-host and private-IP patterns; the secret-value heuristic (known prefixes, or a key with a 12+ character value that mixes letters and digits).
- Screenshot heuristics: focus "visible" = outline with width > 0 or any box-shadow; tiny text < 12px; small target < 24px on either side; placeholder contrast < 4.5:1; `accent-color: auto` on native controls.
- Canvas: Fit = visible columns scaled to the window, floor 20%; System column 640px wide and hidden by default.

## How to re-check
Open the page in the table, find the API or criterion, compare with the rule here and in the scripts. Streamlit and Playwright change between releases: re-read for the version the project pins.
