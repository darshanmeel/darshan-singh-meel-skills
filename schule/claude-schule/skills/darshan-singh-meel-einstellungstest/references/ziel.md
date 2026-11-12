# Target: practice for one Ausbildung, sector or employer

Only when the user names a target. The target decides areas, weights and formats; the items stay original and generic.

## 1 Search and read
Web search for the target's test: structure, areas, timing, provider, published sample questions. Order of trust:

| Rank | Page | Use |
|---|---|---|
| 1 | the employer's own careers pages (Ausbildung, Bewerbung, Auswahlverfahren, Online-Test) | facts |
| 2 | the provider's own candidate or practice pages (table below) | facts, format of sample questions |
| 3 | other public prep pages (training sites, guides) | structure only, always `check: <page>`; never their items |

- Search with the target words only (employer, occupation, "Einstellungstest", "Online-Test", "Auswahlverfahren"); never send file contents, code, project or person names. A pasted invitation gives only the employer and the occupation.
- Take: areas and their order · task formats · time per part · aids (calculator) · pause rule · device hints · whether a personality, SJT or game part exists · the look of published sample questions.
- Sample questions: read for type, length and difficulty; never copy, translate or renumber them, never store them. Write originals in the same style.
- Each fact goes into `profil.json` with its page in `sources`. A fact only on a rank-3 page, or inferred, goes into `unverified` as `check: <page>` and is named in the reply.
- No page found: say so in the reply, use the general mix of `bereiche.md` shifted by occupation, mark every section `unverified`.

## 2 Profile
- `profil.json` (`formate.md`): target, sections with module, topics, weight, how the task looks, pages read, `unverified`.
- Weights: stated minutes or task counts → percent; else equal shares of the parts named, shifted by occupation (`bereiche.md`, Mix) and marked `unverified`.
- Branchenwissen only as basics an applicant can know before the Ausbildung (`bereiche.md`), from the sector's official pages.

## 3 Reuse, then write
- Inventory by script: per section, the topics, ids and counts already in `unterricht/einstellungstest/`.
- Reuse items that fit the section's topic and level; copy them into the mock test with new ids (one prefix per file) and the same content.
- Write only what is missing (process A): one chapter + 8 items per missing topic, in the format the pages describe (e.g. statements about a table instead of a bare calculation).
- Mock test (process B) in the profile's order and weights; hand over the profile table, pages read, what is `check:`.

## Verified provider facts (read on the providers' own pages, 2026-11-11; `sources.md`)
Re-read before relying on a detail; the target's own page wins.

| Provider | Read | `check:` |
|---|---|---|
| Cyquest (cyquest.net) | procedure families: berufsbezogene Leistungsverfahren, Kenntnis- und Wissensverfahren, Persönlichkeits-, Interessen-, Simulations-/SJT-, Cultural-Fit-Verfahren · Leistungs modules named: Fortführen von Jahreszahlen, Rechentextaufgaben, Rechenzeichen, Artikel überarbeiten, Textanalyse, Passiver Wortschatz, Analyse von Diagrammen, Matrizentest, Überprüfung Soll-Ist-Zahlen, Datenbankvergleich, E-Mail-Adressenvergleich, Adressenvergleich, Zahlen erfassen, Culture-Fair-Test · tests are time-limited · practice reduces the effect of nervousness; cheating is advised against | task mechanics, items and seconds per module; pause and device rules |
| Aon, formerly cut-e (aon.com, "Prepare for your online assessment") | performance tests, knowledge tests, personality questionnaires; named tests incl. Numerical, Verbal, Inductive, Deductive (switchChallenge), Working Memory (gridChallenge), Mechanical, Language Skills, gamified SJT, ADEPT-15 · mostly no more than five tests · untimed walkthrough before each test · a started test cannot be interrupted; several days to finish · PC or laptop recommended · a calculator or pen and paper is useful for some tests · normal not to finish; points for each correct answer · personality questionnaires: no right or wrong answers, no time limit · someone else taking the test is not tolerated; retests happen · practice screencasts and PDF tasks | deduction for wrong answers; adaptive testing; minutes and items per test |
| SHL (shl.com/shldirect, practice tests) | practice tests: Verbal, Numerical, Deductive, Inductive, General Ability, Checking Information, Calculation, Reading Comprehension, Working with Information, Mechanical, Situational Judgement, Personality, Behaviour-Based, simulations · interactive (drag and drop) and standard multiple-choice versions · Numerical: tables of data; Verbal: written information and arguments; Inductive: patterns; Deductive: logical conclusions; Checking: accuracy with written detail | minutes and items per test; German versions |
| u-form Testsysteme (testsysteme.de) | Leistungs-, Persönlichkeits- and Intelligenztests, online or printed; target groups incl. kaufmännische, gewerbliche and IT-Ausbildungsberufe · sample areas: Rechnen, Englisch, Logik, technisches Verständnis, Textverständnis Deutsch, Konzentration · "Azubi-Box" e-Postkorb for kaufmännische occupations · employers can change questions and order; new editions yearly | Allgemeinwissen part; durations and content per occupation test |

- Practice items in a provider's format are this skill's own working model (`sources.md`), e.g. Aon/SHL numerical: statements about a table; Cyquest: continue a year series, compare two columns.
- Bundesagentur für Arbeit Check-U (arbeitsagentur.de) is a free career orientation test from age 13, about 80 minutes, pausable - recommend it when the user does not yet know the occupation; it is not practice for an employer's test.
