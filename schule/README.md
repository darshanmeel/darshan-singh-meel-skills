# School skills (Hessen)

Skills for teaching material at Grundschule and Gymnasium in Hessen. Material is German with the closest natural English sentence under every line.

## Install
```bash
cp -r schule/claude-schule/skills/. ~/.claude/skills/   # or schule/claude-schule-panini/skills/.
```
Restart Claude Code. Needs Python 3 for `scripts/check_material.py` (standard library only).

## Skills (all prefixed `darshan-singh-meel-`)
| Skill | Job |
|---|---|
| `schule` | Shared base, loaded with every school skill: Hessen framework (KC, KCGO, grading, written-work rules), operators and AFB, German + English line rule, output folder, HTML templates (Stundenentwurf, Arbeitsblatt + Lösung, Test + Erwartungshorizont, Erklärung, Animation), setup questions, review rubric, check script |

| `schule-mathe` | Mathematik, Grundschule + Gymnasium (Sek I, Oberstufe GK/LK) |
| `schule-deutsch` | Deutsch, Grundschule + Gymnasium; material German, English help lines for instructions only |
| `schule-biologie`, `schule-chemie`, `schule-physik` | Gymnasium Sek I + Oberstufe; experiments with safety notes |
| `schule-nwt` | Naturwissenschaft und Technik as Hessen offers it (Mittelstufe) |
| `schule-erdkunde`, `schule-geschichte` | Gymnasium Sek I + Oberstufe; generated maps and climate diagrams, source work |
| `schule-powi` | Politik und Wirtschaft (Hessen's economics subject), Sek I + Oberstufe |
| `schule-psychologie` | Psychologie as Hessen offers it |
| `daf` | German as a foreign/second language A1–C1, allgemein and Beruf; Goethe, telc and DTB formats |
| `kaenguru` | Mathe-Känguru preparation, classes 3–13; original problems, timed mock tests |

Every skill has a `-review` partner (e.g. `schule-mathe-review`): it solves every task, checks facts, sums, level, the English lines and the animation, and writes `reviews/<skill>-<date>.md`.

Two versions: `claude-schule/` (full) and `claude-schule-panini/` (same rules, sūtra style); references, templates and scripts are identical.

## Output
- Material: `unterricht/<fach>/<stufe>/<thema>/` in the current project - self-contained HTML, A4 print, English lines can be switched off.
- Reviews: `reviews/<skill>-<YYYY-MM-DD-HHMM>.md` (git-ignored).

## Facts
Rules and curricula are taken from official pages only; what was read and what still needs checking: `claude-schule/skills/darshan-singh-meel-schule/references/sources.md`.
