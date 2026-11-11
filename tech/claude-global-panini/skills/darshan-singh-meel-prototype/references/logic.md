# Logic branch

A terminal app the user drives by hand to push a state model through cases that look fine on paper. Templates: `templates/logic/logic.py` (core), `templates/logic/tui.py` (shell).

## Language
- Python standard library by default.
- Project in another language (TypeScript, Go, Java, …) → that language and its existing runner, so the core can be absorbed without a port. Same two-file split, same frame.
- No new dependency for the shell: no TUI or colour library unless the project already has one.

## Core: pick the shape from the question
| Shape | Use when | Interface |
|---|---|---|
| Reducer | discrete events change one state value | `initial() -> state`, `step(state, action) -> state` |
| State machine | "which actions are legal now?" is part of the question | states, a transition table, `allowed(state) -> actions` |
| Pure functions | no current state, only transformations (pricing, matching, parsing) | functions over plain dicts, lists, tuples |

- No `print`, `input`, file, clock, random or network call in the core. Time and randomness come in as arguments (`step(state, action, now)`).
- `step` returns a new state; it never mutates its argument (the shell may keep history).
- A rejected action is state too: set an `error` field instead of raising, so the frame shows why.
- Plain data: dicts, lists, tuples, enums. A class only when the project's real code will use the same class.

## Shell: one stable frame
- Clear the screen and redraw everything after every key; never append to scrollback.
- Frame, top to bottom:
  1. the full state, one field per line (`json.dumps(state, indent=2, default=str)`); the template adds a bold header with the last action;
  2. the last action and its error, if any;
  3. the keys: `[a] add item  [s] submit  [q] quit`.
- One key = one action. An action that needs a value (an amount, an id) → the shell cycles through 3-4 synthetic values, or reads one line.
- The frame fits one screen. State too large → show the part the question is about, plus counts for the rest.
- Useful extra keys when the question needs them: `[u]` undo (keep a list of states), `[t]` advance the clock, `[r]` reset.
- **Piped input:** when stdin is not a terminal the shell reads one character per key, prints frames one after another without escape codes, and quits at end of input. That is how Claude and the reviewer run it: `echo aasq | python prototypes/<name>/tui.py`.
- Older Windows consoles need ANSI handling switched on once; the template does it.

## Run command
- `python prototypes/<name>/tui.py`. Project has a task runner (`package.json` scripts, `Makefile`, `justfile`) → add nothing to it; a prototype leaves no trace outside its folder.

## What to try (hand-over)
Name the 2-4 key sequences that probe the question: the edge the user worried about, the same action twice, the action in the wrong state, the longest sensible path.

## Not in a Logic prototype
- Tests, a database, a web server, logging, config, argument parsing.
- Core code that imports the shell or checks "am I in a terminal".
- A second question ("while we are here, also the pricing rules").
