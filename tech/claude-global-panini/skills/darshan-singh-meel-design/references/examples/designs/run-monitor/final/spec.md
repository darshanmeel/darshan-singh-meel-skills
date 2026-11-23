# Spec: run-monitor
Design: `designs/run-monitor/final/index.html` (Runs), `designs/run-monitor/final/run.html` (Run) · States: `designs/run-monitor/final/states.html` · Tokens: `designs/run-monitor/final/tokens.css` · Stack: React (new build)

The Runs screen states the situation in one line, puts every failed or late run first with its error and a retry, and lists all runs of the last 24 hours in a dense filterable table; the Run screen opens on the error line and the stage that caused it. An on-call engineer sees what broke, why, and retries it without opening a log.

Implement from this file and the HTML alone. Where the HTML and this spec differ, the spec wins; say so in the implementation notes. Every state named below is drawn in `states.html`; every copy string is in the Copy table.

## Layout
- Runs, reading order: header (product, nav, on-call) → h1 situation line → attention cards (failed, then late) → "All runs" chips and search → table.
- Run, reading order: header → back link → h1 situation line → error block → actions → stages → last 14 runs and facts → log tail.
- Above the fold at 1280×800: Runs shows the h1 and all four attention cards; Run shows the h1, the error, the actions and the stages. At 390×844: Runs shows the h1 and the first card with its 44px actions; Run shows the h1, the error and the actions.
- Grid: `main` max 1180px (Runs) / 920px (Run), padding `--space-5`; cards `repeat(auto-fit, minmax(min(100%, 440px), 1fr))` → 2×2 at 1280, one column at 390.
- Hierarchy: the first element after the heading is the first failed run: its strip head (23 low boxes, one red one at the end) and its error line, because the job is "what failed and why". The h1 is the only serif on the page; no word in it is coloured.
- Alignment: durations right-aligned, tabular numerals; times, ids and error lines in `--font-mono`.

## Components
| Component | Variant(s) | Content | Tokens | Maps to existing |
|---|---|---|---|---|
| Situation line (h1) | failures · all fine | "<n> failed, <m> late, <k> running."; subtitle with totals and refresh time | `--font-display`, `--text-3xl` (2xl at ≤ 719) | to create: SituationLine |
| Attention card | failed (`--danger-soft` error block) · late (warning as text) · retrying · queued · retry failed | the 24-run strip as the card's head (full width, the differing box at full height), pipeline, state and end time, caption, error line, meta, actions right-aligned | `--surface`, `--border`, `--radius-md` | to create: AttentionCard |
| Run strip | card head | 24 boxes, one per run of that pipeline (hourly: 24 h, daily: 24 d), ok low, failed or late full height; caption states the counts | `--surface-2` band, `--ok-soft`, `--danger`, `--warn` | to create: RunStrip |
| Status mark | ok · failed · running · late | 8px square + word, never the square alone | `--ok`, `--danger`, `--info`, `--warn` | to create: StatusMark |
| Filter chip | default · pressed | label + count | `--border-strong`, `--radius-full`; pressed `--ink` on `--bg` | to create: Chip |
| Search | default · with hint · invalid | placeholder "Pipeline or owner", hint with the match count | `--border-strong`, `--danger` when invalid | to create: SearchField |
| Runs table | default · hover · skeleton · empty · error | status, pipeline, started, owner, duration with bar, message (ellipsis) | `--surface-2` header, `--border` rows | to create: RunsTable |
| Stage bars | ok · failed | stage name, bar scaled to the run's longest stage, p50 mark, duration and state | `--ok`, `--danger`, `--ink-3` mark | to create: StageBars |
| Duration history | 14 bars | last 14 runs, failed in `--danger` | `--ok`, `--danger` | to create: DurationBars |
| Buttons | default · primary · quiet · disabled | verb + object | `--border-strong`; primary `--accent`/`--accent-ink` | to create: Button |
| Banner | error · stale | one sentence + one action | `--danger-soft`/`--danger-text`, `--warn-soft`/`--warn-text` | to create: Banner |
| Confirmation dialog | delete run | question, consequence, destructive + keep | `--surface`, `--danger` button | to create: ConfirmDialog |

## Behaviour
| Element | Trigger | What happens | Counts and labels | Focus afterwards |
|---|---|---|---|---|
| Filter chip | click, Enter, Space | rows narrow to that status; chip `aria-pressed=true`, the others false; URL `?status=failed` | h2 "All runs" unchanged; hint under the search "<n> of 41 runs" | stays on the chip |
| Search | input, 200 ms debounce | rows filter by pipeline and owner, case-insensitive substring; invalid characters show the invalid state and keep the last valid filter | hint "<n> of 41 runs"; "No runs match "<text>"" when 0 | stays in the field |
| Row | click, Enter | opens the Run screen for that run | – | the Run h1 |
| Retry (card or Run) | click | POST retry; label "Retrying…", both buttons disabled; success: label "Queued" for 3 s, then the card fades out over `--motion` and the h1 counts drop; failure: inline error under the actions, buttons enabled | h1 "<n> failed" decreases on success | the next card's primary button; the h1 when none is left; on the Run screen the Retry button |
| Cancel run (late) | click | POST cancel; same labels as Retry with "Cancelling…" | h1 "<m> late" decreases | as Retry |
| Open log / Open full log | click | opens the log view in a new route; nothing on this screen changes | – | the log |
| Mute alerts 2 h | click | mutes the pipeline's alerts until now + 2 h; stale banner "Alerts for <pipeline> muted until <hh:mm>" with Unmute | – | the Unmute button |
| Delete run… | click | confirmation dialog; "Delete run" removes the run and returns to Runs with a stale banner "Run 4a1f deleted"; "Keep it" closes | – | "Keep it" on open; the Runs h1 after delete |
| Refresh | every 30 s, and on focus | table and cards update in place; the subtitle's "refreshed <s> s ago" counts up between refreshes; a failed refresh shows the error banner and keeps the last data with the stale banner | counts recomputed | unchanged |
- Default sort: started, newest first; no user sorting in this version.
- Async outcomes: loading skeletons (cards: 2, table: 8 rows), success in place, failure inline with the fix; never a toast.

## States
| View | Loading | Empty | Error | Success / other |
|---|---|---|---|---|
| Attention cards | 2 skeleton cards | "Nothing needs attention. All 41 runs since yesterday 14:30 finished on time." | banner "Could not load runs — the last refresh was <hh:mm>." + Retry; last cards kept | retrying · queued · retry failed |
| Runs table | 8 skeleton rows, header stays | "No runs match "<text>"." + Clear filters | same banner; stale banner while the last data shows | row hover |
| Run screen | skeleton h1, error block, facts | "Run <id> is not in the last 30 days." + Back to runs | banner "Could not load run <id> — retry" | retrying, muted banner, delete confirmation |
Controls: default · hover (`--surface-2`) · focus-visible (`--focus` 2px, offset 2px) · active · disabled (`--ink-3`, `--border`; primary disabled `--accent-soft`) · pressed chips (`--ink` fill) · invalid search (`--danger` border + hint). All drawn in `states.html`.

## Responsive
| Width | What changes |
|---|---|
| ≥ 1280 | 2×2 cards; full table with Owner and Message |
| 720–1279 | cards 2 columns while the container is ≥ 900px, then 1; table unchanged, scrolls inside `.scroll` if needed; Run page facts in 2 columns |
| ≤ 719 | nav scrolls horizontally inside the header; one card column; card and Run actions 44px tall and full width; table drops Owner, Message and the duration bars; search spans the row; stage bars wrap under their names; Run facts in 1 column |
No page-level horizontal scroll at 390: the table scrolls inside its own container only.

## Accessibility
- Landmarks: `<header>`, `<nav aria-label="Main">`, one `<main>`, one `<h1>` per screen; cards are `<article>` with an `<h2>`; the table has a `<thead>`; strips and bar charts carry `aria-label` text with the numbers.
- Focus order Runs: nav → first card's Open log → Retry → next cards → chips → search → rows. Run: nav → back link → Retry → Open full log → Mute → Delete.
- Contrast from tokens: text ≥ 4.5:1, controls ≥ 3:1 in both themes (`check_design.py designs/run-monitor --final`: 0 FAIL); placeholders in `--ink-2`.
- Targets: buttons 36px tall (44px at ≤ 719); chips 28px tall and ≥ 60px wide with 8px gaps (secondary filter); status always text + mark; `accent-color: var(--accent)` on the search field.
- Motion: background change on hover over `--motion-fast`; a retried card fades out over `--motion`; nothing else moves; `prefers-reduced-motion` disables both.
- Error lines are `<pre>` with `white-space: pre-wrap`, read in full by screen readers.

## Copy
| Where | Text |
|---|---|
| Runs h1 | "<n> failed, <m> late, <k> running." · all fine: "All runs on time." |
| Runs h1 subtitle | "<total> runs since <hh:mm> yesterday · <ok> ok · refreshed <s> s ago" |
| Card state | "failed <hh:mm>" (end time) · "failed <hh:mm> · 2nd try" · "running <n> min" · "queued <hh:mm>" |
| Strip captions | "24 runs, 24 d: 22 ok, then 2 failed" · "24 runs, 24 h: 23 ok, then 1 failed" · "24 runs, 24 d: 4 of the last 6 failed" · "24 runs, 24 d: 23 ok, 1 late now" |
| Late line | "Late: usually done in <p50> min · waiting on warehouse queue (<n> ahead)" |
| Card primary | "Retry <pipeline>" · dbt, resumable: "Retry <pipeline> from failure" · late: "Cancel run" |
| Card secondary | "Open log" |
| Retrying / queued / failed | "Retrying…" · "Queued" · "Retry failed: the scheduler did not answer. Try again, or open the log." |
| Empty cards | "Nothing needs attention. All <total> runs since yesterday <hh:mm> finished on time." |
| Table section | "All runs" · chips "All <n>" · "Failed <n>" · "Running <n>" · "Late <n>" |
| Search | placeholder "Pipeline or owner" · hint "<n> of <total> runs" · invalid "Letters, digits, _ and - only" · empty "No runs match "<text>"." + "Clear filters" |
| Table header | Status · Pipeline · Started · Owner · Duration · Message |
| Load error | "Could not load runs — the last refresh was <hh:mm>." + "Retry" · stale: "Showing runs as of <hh:mm>; refreshing in the background." |
| Run h1 | "<pipeline> failed at <hh:mm> after <n> min." · subtitle "run #<id> · started <hh:mm> by schedule · p50 is <n> min · owner <team>" |
| Run back link | "← Runs, last 24 h" |
| Run actions | "Retry <pipeline>" · "Open full log" · "Mute alerts 2 h" · "Delete run…" |
| Stages | "Stages · bar = this run · mark = usual (p50)" · per stage "<n> min · ok" / "<n> min · timeout" |
| Run sections | "Last 14 runs, duration" · "Facts" · "Log, last lines" |
| Muted | "Alerts for <pipeline> muted until <hh:mm>." + "Unmute" |
| Delete dialog | "Delete run <id>?" · "The log and the stage timings are removed. The pipeline and its schedule stay." · "Delete run" · "Keep it" |
| Run not found | "Run <id> is not in the last 30 days." + "Back to runs" |

## Motion
- Button and row background on hover: `background` over `--motion-fast` with `--ease`. A retried card fades out over `--motion` after the API confirms. Nothing else.

## Tokens → project
- `designs/run-monitor/final/tokens.css` → src/styles/tokens.css (to create), imported once in the app root; components use `var(--…)` only; `color-scheme` follows the OS, a toggle sets `data-theme` on `<html>`.
- Fonts: system stacks as in the tokens; the display serif is the system's (Iowan Old Style, Palatino, Georgia); no webfont.

## Maps to
New build, no existing files. To create: src/pages/Runs.tsx, src/pages/Run.tsx, src/components/SituationLine.tsx, AttentionCard.tsx, RunStrip.tsx, StatusMark.tsx, Chip.tsx, SearchField.tsx, RunsTable.tsx, StageBars.tsx, DurationBars.tsx, Button.tsx, Banner.tsx, ConfirmDialog.tsx, src/styles/tokens.css (copy of the tokens).

## Acceptance checks
Each check names the file, the viewport and the value, so it can be run without this spec's context.
- [ ] `screenshot.py designs/run-monitor/final --viewports 1280x800,390x844 --themes light,dark --keyboard 20`: 0 WARN lines for index.html and run.html
- [ ] KEYS line of index.html at 1280 light starts: "Last 24 h" → "Pipelines" → "Schedules" → "Alerts" → "Open log" → "Retry finance_close_daily from failure"
- [ ] fixture arithmetic: every row's start + duration ≤ 14:32; card end times = start + duration; the h1 counts equal the table (36 ok + 3 failed + 1 late + 1 running = 41)
- [ ] `check_design.py designs/run-monitor --final`: 0 FAIL
- [ ] `states.html` shows 5 button states, 2 chip states, 2 search states, 5 card states, 4 table states, 4 Run states (22 frames)
- [ ] index.html at 1280×800: the h1 and all four attention cards are visible without scrolling
- [ ] index.html at 390×844: the first card's two buttons are each ≥ 44px tall and the page has no horizontal scroll
- [ ] with 0 failed and 0 late runs the empty paragraph shows and the h1 reads "All runs on time."
- [ ] every string in the Copy table appears verbatim in index.html, run.html or states.html (placeholders in angle brackets substituted)
- [ ] no colour literal outside tokens.css; both themes render from the same markup (`data-theme="dark"` on `<html>`)

## Out of scope
- Log view, Pipelines, Schedules and Alerts screens; direction C's day grid is the candidate for Schedules.
- User sorting of the table and saved filters (decide after two weeks of use).
