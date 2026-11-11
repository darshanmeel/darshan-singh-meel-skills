# Review file format

File: `reviews/prototype-review-<YYYY-MM-DD-HHMM>.md` in the project root; name taken → `...-<HHMM>-<name>.md`, never overwrite. Paths relative to the project root. Omit empty sections except "Runs" and "Question".

```markdown
# Review: prototype <name>
Date: <YYYY-MM-DD HH:MM> · Skill: darshan-singh-meel-prototype-review · Folder: prototypes/<name>
Branch: <Logic | UI | Data | Pipeline> · Status in NOTES.md: <open | done>
Verdict: <Usable | Usable after Must fixes | Redo>
Counts: Must <n> · Should <n> · Other <n> · Script: <n> FAIL

## Question
- Asked: "<the question from NOTES.md>"
- Deciding case: <the case that separates the possible answers> · reachable: <yes | no>
- What the run shows: <one or two sentences, written before reading "Answer">
- Answer in NOTES.md: <agrees | differs: how | not filled>

## Must
- **[<area>] <file>:<line> / key / variant / task** - what: <one line, quoted> · why: <one line> · fix: <the change, or the lines to delete>

## Should
- ...

## Other
- ...

## Runs
| What | Command | Versions | Exit | Result |
|---|---|---|---|---|
| start | `python prototypes/order-dedup/run.py` | Python 3.14.3, duckdb 1.5.1 | 0 | prints input and 3 candidates |
| second run | same | same | 0 | output equal to the first |
| check script | `python <prototype skill dir>/scripts/check_prototype.py prototypes/order-dedup --done` | - | 0 | 0 FAIL |

## Variants
<!-- UI only -->
| Key | Layout | Hierarchy | Primary action | Navigation | Differs from the others in |
|---|---|---|---|---|---|
| A | table | filter bar, then rows | "New order", top right | one page | - |
| B | master-detail | list left, detail right | "Approve", in the detail pane | drill-down | layout, primary action, navigation |

## Containment
- `.gitignore`: <`/prototypes/` present | missing>
- Outside `prototypes/`: <none | listed files, each found and named `*prototype*` | unlisted: paths>
- Real code importing the prototype: <none | paths>
- Dependencies or lock files changed: <none | paths>

## Checked without findings
<areas 1-12 that passed, one line>

## Not checked
<what could not be verified and why: not run because the command reaches a real system, runtime not installed (with the command for the user), variants not rendered, no git>
```

## Rules for the sections
- **Runs:** one row per run, including each piped key sequence (Logic), each variant requested (UI), each logical date (Pipeline). Result `not run: <reason>` when step 3 was refused.
- **Question:** "What the run shows" is the reviewer's own reading of the output; a difference from "Answer" is a Must (area 2), with the output lines that show it.
- **Variants:** a pair with fewer than two differing columns → Must (area 7).
- Area tags: Runs, Question, Scope, Branch, State, Core, Variants, Data, Stubs, Notes, Contained, Secrets (areas 1-12 of the checklist, in that order).
- Secret-looking values are never quoted: path, line, rule name, `<redacted>`.
- Rows of data are quoted only when synthetic and written in the prototype.

## After fixes (only when the user asked for them)
Append:
```markdown
## Fixed <YYYY-MM-DD HH:MM>
- Must 1 - <what changed> · rerun: <command> exit 0
- Should 2 - not changed: <reason>
Verdict after fixes: <...>
```
