# Sources and verification status

Status: **read** = read on the page on 2026-11-11 · **check** = not read or not confirmed; verify on the page named. Providers change products and pages: re-read before relying on a detail. Searches carry no file contents, code, project or person names.

## Provider pages used (`ziel.md`, verified table)
| Topic | Page | Status |
|---|---|---|
| Cyquest: procedure families | `https://www.cyquest.net/` | read |
| Cyquest: module names of the berufsbezogene Leistungsverfahren | `https://www.cyquest.net/online-assessment-verfahren/uebersicht-testverfahren/berufsbezogene_leistungsverfahren/` | read: names; mechanics not described |
| Cyquest: preparation - effect of practice, time limits, advice against cheating | `https://www.cyquest.net/online-assessment-verfahren/vorbereitung-online-assessment/` | read; the page advertises the provider's own practice tool - not recommended by this skill |
| Aon: candidate preparation - test kinds and names, walkthrough, no interruption, devices, scoring remark, personality questionnaires, integrity, practice material | `https://www.aon.com/en/capabilities/talent-and-rewards/prepare-for-your-online-assessment` | read |
| SHL: practice tests and what each measures; interactive and multiple-choice versions | `https://www.shl.com/shldirect/en/practice-tests/` | read; durations not on the page |
| u-form Testsysteme: test kinds, online or printed | `https://www.testsysteme.de/` | read |
| u-form Testsysteme: target groups, sample areas, Azubi-Box, yearly update | `https://www.testsysteme.de/online-tests` | read; durations not on the page |
| Bundesagentur für Arbeit: Check-U | `https://www.arbeitsagentur.de/bildung/welche-ausbildung-welches-studium-passt` | read |

## Not verified (`check:`)
- Task mechanics, item counts and seconds per module of every provider; which modules an employer uses.
- Aon: deduction for wrong answers, adaptive testing, minutes per test, browser advice.
- SHL: minutes per test, German versions. u-form: Allgemeinwissen part, durations, content per occupation test.
- Whether a given personality questionnaire scores consistency; whether a given SJT is keyed "best/worst".
- Employers' cut-offs: not published on the pages read.
- Every target fact from a page that is not the employer's or provider's own (rank 3 in `ziel.md`).

## Own working rules (not official)
- Areas, topics, item families, seconds per item, the general mix (`bereiche.md`).
- Difficulty 1-3, distractor families, key balance, explanation form, the `check` field (`aufgabenbau.md`).
- JSON keys, folder names, `profil.json`, sizes and times of mock tests, 1 point per question, percent per area (`formate.md`).
- Mapping difficulty 1/2/3 → AFB I/II/III (needed by the base check script only).
- Practice items in a provider's format (`ziel.md`).
- Trait list, statement scale with 4 steps, explanation form for unkeyed items, the honesty rule (`persoenlichkeit-sjt.md`).

## Not sources for items
- Sample questions on any page, practice PDFs, demo tests, sample-test books, AI-generated sets, memory of past tests: read for the format at most, never copied or stored.
