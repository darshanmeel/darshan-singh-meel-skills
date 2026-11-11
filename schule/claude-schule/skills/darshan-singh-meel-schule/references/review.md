# Review rubric for teaching material

Used by every school `*-review` skill and by step 6 of the base process (Must items only). The reviewer reviews; it rewrites only when the user asks.

## Process
1. Scope: which files (default: every `.html` in the topic folder). Read the subject skill's reference for the level and the base references the files touch.
2. Run `python <skill dir>/scripts/check_material.py <folder>`. Every `FAIL` line is a Must finding; every `?` line is checked by hand.
3. Solve every task yourself, without looking at the solution; then compare. Recompute every number, sum, percentage, unit, date.
4. Read every DE/EN pair with the 3-step test in `bilingual.md`.
5. Open `animation.html`: step through every step forwards and backwards, play at each speed, toggle English, print preview.
6. Walk the checklist below. Write the report to `reviews/<skill>-<YYYY-MM-DD-HHMM>.md` (add `/reviews/` to `.gitignore` on first use). Reply with verdict, counts, and the report path.

## Checklist
| # | Area | Check | Must when |
|---|---|---|---|
| 1 | Curriculum fit | KC source, Kompetenzbereich, competence, Inhaltsfeld/Themenfeld named and real; fits Jahrgang/Kurs and GK/LK level; Stundenziel is a step towards the competence and visible in the tasks | KC reference missing, invented, or from the wrong level; LK-only content in GK material |
| 2 | Subject correctness | every task solvable with what was taught; every solution right; numbers, units, dates, names, formulas, figures, labels correct; test, Erwartungshorizont, worksheet, Lösung, Erklärung and animation agree | any wrong fact or solution; an unsolvable or ambiguous task; files contradict each other |
| 3 | Operators and AFB | one operator per task, from the subject's list, practised form (du/Sie); AFB label matches what the task really demands; mix as in `bewertung.md`; "ausreichend" reachable with AFB I + easy II | task without operator in graded work; AFB III missing in an Oberstufe Klausur; AFB labels plainly wrong |
| 4 | Time | phase minutes add up; Einstieg short; Sicherung present; worksheet fits its phase; test fits the working time (teacher time × 3) and the legal length | minutes do not add up; test cannot be finished in the time; length breaks the rule for the level |
| 5 | Marking scheme | points per part; parts sum to the total; test = Erwartungshorizont (ids, points, AFB); AFB table sums to 100 %; grade key complete, falling, without gaps, right scale for the level (Noten 1-6 or 0-15 Punkte), source named; Folgefehler and language rule stated | sums differ; grade key wrong or missing; points cannot be awarded from the description |
| 6 | Language level | sentence length and vocabulary fit the age; subject terms introduced; no unexplained abbreviations; instructions unambiguous | students of that age cannot understand a task |
| 7 | Bilingual accuracy | every German line has an English line (except formulas, names, `data-nur-de` blocks); English is the closest natural sentence: same meaning in context, same operator, numbers, units, sentence count, order of ideas; glossary DE \| EN complete and uses established terms; decimal comma/point per language; toggle hides all English; one answer space per task | English line missing; meaning differs (wrong term, wrong operator, wrong number); English given for a text that must stay German (Deutsch analysis text, DaF target text) |
| 8 | Differentiation | three levels differ in help/complexity, not topic; Herausforderung is not just more tasks; DaZ/LRS/Förderbedarf measures asked for are present and concrete; no student named | measures the user asked for are missing |
| 9 | Accessibility and print | contrast, font size, nothing by colour alone, alt texts/aria-labels, keyboard use; A4 print: nothing cut off, no split task, answer space large enough, toolbar hidden | unreadable or cut-off print; answer space clearly too small; missing alt text on a figure a task depends on |
| 10 | Animation | opens offline; Start/Pause, Zurück, Weiter, Tempo and keys work; captions DE/EN per step match the picture; end state equals the solution; reduced-motion fallback; print shows all key frames; animation is needed (motion or steps), not decoration | does not run; shows something false; controls missing |
| 11 | Privacy and copyright | no real student, teacher or school names or data; no task, text or figure copied from a textbook, Abitur paper, Vergleichsarbeit or competition; source texts public domain, user's own or written for the task, and stated | any real personal data; any copied protected content |
| 12 | Files and form | folder and file names as in SKILL.md; pairs complete (Arbeitsblatt + Lösung, Test + Erwartungshorizont); self-contained HTML; no placeholders; relative paths only | external resource; pair incomplete; placeholder left |

Bilingual findings name the kind: `fehlt` (no English line) · `zu frei` (paraphrase, added or dropped content, merged sentences) · `zu wörtlich` (German word order, calque, wrong idiom) · `Fachbegriff` (wrong or non-standard term). Quote the German line, the English line, and the fixed English line.

## Severity
| Level | Meaning |
|---|---|
| Must | wrong, unfair, unlawful, unusable, or breaks a "Must when" above - fix before use in class |
| Should | works but weakens learning, fairness or clarity - fix when time allows |
| Other | optional polish; at most 5, only if worth knowing |

- `check:` lines from the references are reported as Should ("verify with <page>"), never as fact.
- No finding without evidence (file, task id, quoted line). No praise section, no restating of the material.

## Report format
```markdown
# Review: <fach> · <stufe> · <thema>
Date: <YYYY-MM-DD HH:MM> · Skill: <skill> · Files: <relative paths>
Verdict: <Einsatzbereit | Einsatzbereit nach Must-Korrekturen | Überarbeiten>
Counts: Must <n> · Should <n> · Other <n> · Check script: <n> errors, <n> warnings

## Must
- **<file> · <task/line>** - what: <one line> · why: <one line> · fix: <concrete change>

## Should
- ...

## Other
- ...

## Checked without findings
<areas 1-12 that passed, one line>

## Not checked
<what could not be verified and why, e.g. school grade key unknown>
```

## Verdict
| Verdict | When |
|---|---|
| Einsatzbereit | no Must |
| Einsatzbereit nach Must-Korrekturen | 1-3 Must, each fixable in the file without redesign |
| Überarbeiten | more than 3 Must, or a Must in area 1, 2 or 5 that changes the tasks |
