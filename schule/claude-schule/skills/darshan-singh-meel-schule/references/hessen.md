# Hessen: school levels and Kerncurricula

Sources and verification status: `sources.md`. `check:` = not verified against the official text.

## Levels
| Stufe | Jahrgänge | Notes |
|---|---|---|
| Grundschule (Primarstufe) | 1-4 | Bildungsstandards describe the end of Jg. 4 |
| Gymnasium Sek I (Mittelstufe) | 5-10 (G9) · 5-9 (G8) | default here: G9 |
| Oberstufe Einführungsphase | E1, E2 (Jg. 11 in G9, Jg. 10 in G8) | one year |
| Oberstufe Qualifikationsphase | Q1-Q4 (Jg. 12-13 in G9) | two years; Q4 = Prüfungshalbjahr |

- Qualifikationsphase: two Leistungskurse (LK) plus Grundkurse (GK). First LK is Mathematik, a continued foreign language or a natural science.
- Abitur: five exam subjects - three written (both LK among them), the fourth oral, the fifth oral, a Präsentation or a besondere Lernleistung; Deutsch and Mathematik are among them. check: OAVO (exam subjects) for the exact conditions.
- "Mittelstufe" in these skills = Sek I Jg. 5-10; "Oberstufe" = E-Phase + Q1-Q4.
- Weekly hours per subject and year: check: Verordnung über die Stundentafeln (link in `sources.md`); schools shift hours within the Kontingentstundentafel.

## Kerncurriculum Primarstufe and Sek I (in force since 2011/12)
One format for all subjects, Jg. 1-10. Each subject PDF ("Bildungsstandards und Inhaltsfelder") has:

| Part | Content | Use in material |
|---|---|---|
| Überfachliche Kompetenzen | personal, social, learning, language competence | name one only if the lesson targets it |
| Kompetenzbereiche des Faches | the subject's competence areas (process side) | **cite one per learning goal** |
| Bildungsstandards | what students can do at the end: Jg. 4 (Primarstufe), Jg. 9/10 (Gymnasium, for the move into Sek II) | cite the standard the lesson works towards |
| Lernzeitbezogene Kompetenzerwartungen | Gymnasium: end of Jg. 6 and Jg. 8; Primarstufe: end of Jg. 2 | cite the one for the class's stage |
| Inhaltsfelder | binding content areas, paired with the Kompetenzerwartungen | **cite one per lesson** |
| Synopsen | competence growth Jg. 4 → 9/10 | check prior knowledge |

- The KC sets standards for stages (4, 6, 8, 9/10), not for single years. Which topic sits in which year is fixed by the school's Schulcurriculum / Fachcurriculum - ask the user when the year matters; otherwise place the topic by the KC stage and state it in the Stundenentwurf as a fact (`Einordnung nach KC-Stufe 6; Jahrgang laut Schulcurriculum`).
- Each KC has a Leitfaden (planning guide) on the same page.

## Kerncurriculum gymnasiale Oberstufe (KCGO; revised version phased in from the Einführungsphase, second half of 2024/25)
| Part | Content |
|---|---|
| 1.3 Überfachliche Kompetenzen | as above |
| 2.3 Kompetenzbereiche | subject competence areas (e.g. Physik: Sachkompetenz, Erkenntnisgewinnung, Kommunikation, Bewertung) |
| 3.2 Bildungsstandards | per competence area |
| 3.3 Kurshalbjahre und Themenfelder | E-Phase (one Jahresthema), Q1, Q2, Q3, Q4 - each with numbered Themenfelder and binding content points |

- Binding Themenfelder are listed per Kurshalbjahr in each subject KCGO (pattern in Physik: E: 1-3 · Q1: 1-2 · Q2 and Q3: 1-3 · Q4: 1); the numbers differ by subject - read the subject file.
- Content is split into grundlegendes Niveau (GK and LK) and erhöhtes Niveau (LK only). GK material never needs LK-only content.
- "zum Beispiel" items are suggestions; "am Beispiel" items are binding.
- The Abiturerlass of the exam year can set priorities inside Themenfelder: check: Abiturerlass for the year the course sits the exam.
- Anforderungsbereiche are a property of tasks, not of the KC (OAVO § 25 Abs. 4).

## How to cite the KC in a lesson plan
Fill the four rows of the "Bezug zum Kerncurriculum" table in `stundenentwurf.html`:

| Row | Sek I / Primarstufe | Oberstufe |
|---|---|---|
| Quelle | `KC Hessen, Sek I Gymnasium, <Fach>` (or `Primarstufe, <Fach>`) | `KCGO Hessen, <Fach>` |
| Kompetenzbereich | name as printed in the KC | name as printed in the KCGO |
| Kompetenz / Bildungsstandard | the Kompetenzerwartung for the stage, with the stage: `(Ende Jg. 6)` | the Bildungsstandard with its code as printed |
| Inhaltsfeld / Themenfeld | Inhaltsfeld name | `<Kurshalbjahr>.<Nr> <Themenfeld name>`, `GK` or `LK` |

- One or two competences per lesson; the Stundenziel must be a step towards them, visible in the tasks.
- Wording comes from the KC PDF (via the subject skill's reference). Paraphrase is allowed only when marked `sinngemäß`.
- Tests: the Erwartungshorizont header names the same KC reference.
- KC wording stays German as printed; the English line under it is our own translation, not an official text (`bilingual.md`).
- Grundschule subjects with a KC: Deutsch, Mathematik, Sachunterricht and others; these skills cover Deutsch and Mathematik in Jg. 1-4.
