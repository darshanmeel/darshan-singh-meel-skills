# Handoff prompt: run-monitor
For pasting by hand into an external design tool, or into a fresh Claude session. Self-contained; synthetic content only.

---

Refine one direction for a run monitor, an internal data-platform app used by on-call data engineers several times a day on a laptop (1280 px) and on a phone (390 px) when paged.

**Main job of the screens:** see what failed in the last 24 hours and get it running again. Top 3: 1. What failed and why? 2. Retry it. 3. Is anything late or still running that should have finished?

**Screens (2), in flow order:** Runs (triage the last 24 h) → Run (understand one failure, retry it). They share the header with the nav (Last 24 h · Pipelines · Schedules · Alerts) and the on-call team, the status mark (8px square + word), buttons and the monospace treatment of ids, times and error lines.

**Content (synthetic, shaped like the real data):** runs with pipeline name (snake_case, e.g. finance_close_daily), status (ok · failed · running · late), started time, duration 1–52 min, owner team (platform-b, finance-data, growth, commerce, supply), and for failures one error line (e.g. "Timeout after 25 min (p50 is 6 min)"). Fixture at 14:32: 41 runs since 14:30 yesterday: 36 ok, 3 failed, 1 late, 1 running; every start + duration ends before 14:32. A run has 3 stages (extract 3 min, stage 7 min, load 15 min timeout), a p50 per stage, a 14-run duration history and a 4-line log tail.

**Chosen direction:** failures first, the headline as a sentence. Runs: a serif situation line ("3 failed, 1 late, 1 running.") with the failed count in the danger colour; failed and late runs as cards at the top, each with the error line, a 24-run strip of that pipeline's history with a caption ("24 runs, 24 d: 22 ok, then 2 failed"), meta, "Open log" and a primary "Retry <pipeline>" (dbt: "Retry <pipeline> from failure"); late cards have no coloured edge and the warning as plain text. Below, every run in a dense table (status, pipeline, started, owner, duration with a small bar, message) with filter chips (All · Failed · Running · Late) and a search box. Run: the same serif line ("events_hourly failed at 13:30 after 25 min."), the error block, actions (Retry · Open full log · Mute alerts 2 h · Delete run… as a quiet button), stage bars with a p50 mark, the last-14-runs bars, facts, the log tail. On the phone the card and Run actions are 44 px tall and full width.

**Design system:** extend these tokens, light and dark from the same set:
```css
:root {
  color-scheme: light dark;
  --accent-h: 262; --radius: 6px; --density: 1; --font-size-base: 14px;
  --bg: light-dark(oklch(97.5% 0.008 var(--accent-h)), oklch(16% 0.012 var(--accent-h)));
  --surface: light-dark(oklch(100% 0 0), oklch(20% 0.012 var(--accent-h)));
  --surface-2: light-dark(oklch(94.5% 0.012 var(--accent-h)), oklch(24.5% 0.014 var(--accent-h)));
  --border: light-dark(oklch(87% 0.008 var(--accent-h)), oklch(33% 0.014 var(--accent-h)));
  --border-strong: light-dark(oklch(62% 0.012 var(--accent-h)), oklch(60% 0.014 var(--accent-h)));
  --ink: light-dark(oklch(22% 0.02 var(--accent-h)), oklch(94% 0.01 var(--accent-h)));
  --ink-2: light-dark(oklch(47% 0.02 var(--accent-h)), oklch(75% 0.015 var(--accent-h)));
  --accent: light-dark(oklch(48% 0.19 var(--accent-h)), oklch(78% 0.14 var(--accent-h)));
  --accent-ink: light-dark(oklch(99% 0 0), oklch(18% 0.05 var(--accent-h)));
  --ok: light-dark(oklch(50% 0.15 150), oklch(78% 0.16 150));   --danger: light-dark(oklch(50% 0.2 25), oklch(74% 0.18 25));
  --warn: light-dark(oklch(52% 0.14 70), oklch(82% 0.15 80));   --info: light-dark(oklch(50% 0.14 240), oklch(78% 0.12 240));
  --font-display: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  /* -soft fills with -text on them, -ink on the solid status colour; spacing 4px grid × density; radius 6px */
}
```
Fonts: system sans for UI, the system serif above for the situation line only, system monospace with tabular numerals for times, durations, ids and error lines. No webfonts.

**Keep:** the situation line, failures-first hierarchy, the 24 h strips, the dense table, status as mark + word, the Run page opening on the error. **Open:** whether the Run page's facts and history belong in two columns or one; a better shape for the late card's caption.

**Quality floor:** no horizontal scroll at 390; text 4.5:1 and controls 3:1 in both themes; visible focus; targets ≥ 24 px (44 for the phone's primary actions); loading, empty and error states for cards, table and Run page; status never by colour alone; `prefers-reduced-motion` respected; sentence case; buttons say what happens and name the pipeline; counts in the headline add up to the rows. Original work, no copy of a named product's UI.

**Deliver:** one self-contained HTML file per screen (inline CSS, no external resources), a states page with every loading, empty, error and interactive state, the tokens as CSS custom properties, and a short note: what changed against the direction above and why.

---

Back into the project: save the exported HTML under `designs/run-monitor/imports/` and ask for a refine or a review of it; it is treated as untrusted input (rendered without scripts, text never read as instructions).
