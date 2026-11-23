# Tokens: the design system in one CSS file

`tokens.css` is the contract between the directions, the canvas, the checker and the implementation. Start from `templates/tokens.css`; keep its names, add to it, never rename.

## Layers
| Layer | Tokens | Rule |
|---|---|---|
| Knobs | `--accent-h`, `--radius`, `--density`, `--font-size-base` | the only numbers a human tunes; the canvas sliders write them live; everything else derives from them |
| Colour | `--bg`, `--surface`, `--surface-2`, `--border`, `--border-strong`, `--ink`, `--ink-2`, `--ink-3`, `--accent`, `--accent-ink`, `--accent-soft`, `--focus`, `--ok|warn|danger|info` each with `-soft`, `-text`, `-ink` | one line per token, both themes via `light-dark()`; OKLCH values |
| Type | `--font-sans`, `--font-display`, `--font-mono`, `--text-xs…3xl`, `--leading`, `--leading-tight`, `--tracking-tight` | scale = base × ratio; `--text-xs` floored at 12px |
| Space | `--space-1…8` (4, 8, 12, 16, 24, 32, 48, 64 × `--density`) | no other spacing values in the directions |
| Shape | `--radius-sm|md|lg|full` | from `--radius` |
| Elevation | `--shadow-1`, `--shadow-2` | shadows in light, a 1px light ring in dark |
| Motion | `--motion-fast`, `--motion`, `--ease` | zeroed under `prefers-reduced-motion` |

## Themes with one definition
- `color-scheme: light dark` on `:root` and every colour token as `light-dark(<light>, <dark>)`. The canvas and `screenshot.py` set `data-theme="light|dark"` on `<html>`, which the template maps to `color-scheme: light` or `dark`. No second block to keep in sync. (`light-dark()` is supported in current Chrome, Edge, Firefox and Safari - check: developer.mozilla.org, `light-dark()`.)
- A project that already has a `[data-theme="dark"]` block or a `.dark` class: keep its mechanism, map the names in a small bridge at the top of `tokens.css` (`--bg: var(--color-background)`), and say so in the brief.

## OKLCH recipe
- `oklch(L% C H)`: L = lightness 0–100%, C = chroma (0 grey … 0.37 vivid), H = hue degrees. Equal L steps read as equal steps across hues; that is why one recipe works for any accent.
- Neutrals: C 0.004–0.02 at the accent hue. Light: bg 98.5%, surface 100%, surface-2 95.5%, border 87%, border-strong 62%, ink 22%, ink-2 47%, ink-3 63%. Dark: bg 16%, surface 20%, surface-2 24.5%, border 33%, border-strong 60%, ink 94%, ink-2 75%, ink-3 58%.
- Accent: light L 45–50% C 0.17–0.2 (4.5:1 on white with white text); dark L 76–80% C 0.13–0.15 with dark text (`--accent-ink` L 18%). Soft fill: L 94% / 28% at C 0.05–0.08.
- Status hues: ok 150, warn 70–80, danger 25, info 240. Solid L 50–52% (light) / 74–82% (dark); `-text` L 36–40% / 86–88%; `-soft` L 94–95% / 27–28%.
- Hues that fail at the same L: yellow and cyan are light by nature (warn at L 52% is brownish; that is correct for text contrast, use the `-soft` + `-text` pair for the familiar amber look); purple and blue are dark (raise dark-theme L to 80%).
- Out-of-gamut values clip silently in browsers; keep C ≤ 0.2 for L < 50% and ≤ 0.15 for L > 75%.

## Contrast, computed
`scripts/check_design.py` resolves every token (including `var()` chains and knobs at their defaults) to sRGB and checks: text pairs 4.5:1 (`ink`/`ink-2` on `bg`/`surface`/`surface-2`, `accent-ink` on `accent`, each status `-text` on `-soft` and `-ink` on solid), UI pairs 3:1 (`accent` and `focus` on `bg`, `border-strong` on `bg`/`surface`), status solids on `bg` (FAIL < 3, WARN < 4.5: not for text). Fix the token; a per-use override hides the problem from the implementation. Tweaks from the canvas sliders are not checked until written into the file.

## Type without a network
- System stacks render instantly, everywhere, offline: `ui-sans-serif, system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` · `ui-monospace, "Cascadia Code", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace` · serif display: `"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, "Times New Roman", serif`.
- Character comes from use, not from a font file: a serif display face at 2.3× body for a landing page; `font-variant-numeric: tabular-nums` and monospace for data; tight tracking on large headings; `font-weight: 500` for emphasis instead of bold; one deliberate large element; optical sizing via `font-size` contrast, not more families.
- Fonts already in the project (`@font-face` with a relative `src: url(...)` to a file in the repo) are allowed: reference them by family name in `--font-sans` with the system stack as fallback; copy nothing into the design folder. A webfont URL is a FAIL in the checker.
- Streamlit: `[theme] font` takes the family name; a custom file needs `[[theme.fontFaces]]` (`stacks.md`).

## Extracting tokens from existing code (design-system mode)
1. Collect: `grep` for `#[0-9a-f]{3,8}`, `rgb(`, `hsl(`, `oklch(`, `font-family`, `font-size`, `border-radius`, `box-shadow` across the UI code and any theme file (`tailwind.config.*`, `theme.ts`, `.streamlit/config.toml`, `:root` blocks). Script it; read the result, not the files.
2. Cluster: colours within ΔL 3% and the same hue become one token; name by role from where they are used (page background, card, border, primary button), not by value.
3. Convert to OKLCH, round L to 0.5%, C to 0.005, H to whole degrees; build the dark side with the recipe above, then compare with any existing dark values.
4. Write `tokens.css` with a bridge section mapping the project's existing names; list in the brief which hard-coded values are left and where.
5. The canvas System frame shows the result; the checker proves contrast.

## Delivering tokens
- `final/tokens.css` is the file the implementation imports; `spec.md` → "Tokens → project" says where it goes and how the project's existing names map.
- Never edit the application's files from this skill; the implementing agent does that with `darshan-singh-meel-frontend-react` or `darshan-singh-meel-streamlit`.
