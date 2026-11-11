# Repo rules: creating and changing skills

Claude Code skills, prefixed `darshan-singh-meel-`, installed into `~/.claude/`. Public repo: everything here stays generic.

## Layout
| Folder | Holds |
|---|---|
| `tech/claude-global/` | Dev setup, full: `CLAUDE.md` (global rules), `hooks/`, `skills/` |
| `tech/claude-global-panini/` | Same rules in sūtra style |
| `schule/claude-schule/skills/` | Hessen school skills, full |
| `schule/claude-schule-panini/skills/` | Same rules in sūtra style |
| `tools/check_repo.py` | Pre-commit checks |
| `context-prompt.md` | Preferences and skill list, to paste into a new chat |

New topic area → new top folder with the same full + panini pair (e.g. `music/claude-music/skills/`).

## A new skill
- **Name:** `darshan-singh-meel-<job>`. One skill, one job. Folder name = frontmatter `name`.
- **`SKILL.md`:**
  - Frontmatter `name` and `description`: what it does, when to use it, trigger phrases (German and English for school skills). Keep the description ≤ 1024 characters; Claude Code cuts it at 1536.
  - Body ≤ ~120 lines: when to use, setup questions, a fixed process, rules. Detail goes in `references/`, read only when needed.
- **Folders:**
  - `references/` (one file per level or topic, plus `sources.md` naming the official pages used);
  - `references/templates/`, `references/examples/` (one small real example);
  - `scripts/` or `tests/run.py` only when they check something. Python stdlib, plain functions.
- **Reviewer partner:** a skill that produces material gets `<name>-review`. It solves or re-runs everything independently and writes `reviews/<skill>-<YYYY-MM-DD-HHMM>.md` with a verdict and Must / Should / Other (what · why · fix).
- **Shared base:** several skills with common rules → one base skill (like `darshan-singh-meel-schule`) that the others load alongside. Never copy its text into them.
- **Facts** (curricula, exam formats, versions, product names): from official sites only. Mark anything unverified `check: <page>` in the skill.
- **Never copy copyrighted tasks verbatim** (textbooks, exams, competitions). Write originals in the same style.
- **Style:**
  - Every word carries a fact or an instruction; no word-count targets, cut only filler.
  - Bullets; tables only to compare.
  - Diagrams only where they explain.
- **Global rules that skills inherit**, so don't contradict them:
  - local files only, never artifacts or published pages;
  - paths relative to the repo root;
  - never open secret files, never read data rows, no real student or personal data;
  - questions via AskUserQuestion (max 4, recommended option first);
  - replies end with `Skills: …`.

## Process
1. **Plan:** ask the user (AskUserQuestion) for the decisions only they can make: scope, levels, curriculum, outputs, location. Push back first if the plan has a flaw (e.g. a subject that doesn't exist at that level).
2. **Create:** Fable, or Opus if Fable is limited.
3. **Review by trial:** Opus.
   - Use the skill on a new request and produce the output.
   - Solve or check every item; open every HTML.
   - Plant 3 errors (a wrong answer, a sum error, an off-level item) and check that the reviewer catches them.
4. **Fix:** fix every High and Medium finding.
5. **Panini twin:** Sonnet.
   - Rewrite `SKILL.md` (and prose `.md` if useful) in sūtra style: the heading sets the scope, `→` = then, `·` = list, "rec" = recommended.
   - Scripts, templates, examples and tests stay byte-identical. See `tech/claude-global-panini/skills/darshan-singh-meel-review/SKILL.md` for the style.
6. **Register:**
   - a row in the Skills table of both `tech/*/CLAUDE.md`, for tech skills;
   - `README.md`, or the folder README such as `schule/README.md`;
   - `context-prompt.md`.
7. **Check, then commit and push** (see below).
8. **Install into `~/.claude` only when the user asks:**
   - Back up first to `~/.claude/backups/pre-install-<date>/`.
   - `cp -r tech/claude-global/. ~/.claude/`, `cp -r schule/claude-schule/skills/. ~/.claude/skills/`, then `python ~/.claude/hooks/install-skill-log.py`.
   - Restart Claude Code.

- Every change goes to both versions. Existing skills keep their behaviour unless the user asks for a change. Never remove a feature on a guess about what the user meant: ask.
- Big jobs (many skills) run as a workflow: per group, create → review → fix → panini. Base skills come first; edits to a shared base happen in one agent at a time.

## Before every commit
- `python tools/check_repo.py` must print `0 ERROR`. It checks:
  - machine paths (`C:\Users\…`, `/Users/…`);
  - the private names listed in `.private-names`;
  - full/panini twins;
  - frontmatter;
  - `__pycache__`.
- **`.private-names`** (git-ignored) lists your user name and the private projects used as test fixtures. Create it on each new machine.
- **Run the tests of every skill you changed:**
  - `tests/run.py` for architecture, docs-v2 and review-v2;
  - the skill's `scripts/` checks on its examples, e.g. `python schule/claude-schule/skills/darshan-singh-meel-schule/scripts/check_material.py <folder>`.
- **Commit message** ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Commit and push only when the user asks.

## Machine notes
- **Windows:**
  - `git mv` fails with "Permission denied" if a shell's working directory is inside the folder: move from the repo root.
  - Set `PYTHONIOENCODING=utf-8` for scripts that print umlauts or arrows.
  - CRLF warnings are harmless.
- **Fable limit:** a 429 with `rateLimitType: seven_day` means the weekly limit. Test with a one-word Fable call before reporting it, because limits can reset early.
