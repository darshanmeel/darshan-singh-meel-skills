# Models, figures, animations

Each model: what it explains, what must be right, a limit for a task, and - where a process is the point - the animation step plan (base engine: `STEPS` with `de`, `en`, `set`; 4-8 steps; base `references/formate.md`). Figures written from subject knowledge; publications in `studien.md`.

## Conventions
- Boxes = stores or instances; arrows = processes, each labelled with a noun (`Aufmerksamkeit`, `Abruf`). Labels inside the picture `DE / EN` or German with the caption carrying the English.
- Capacity and duration figures as approximate (`etwa`, `about`), with the study they come from in the solution.
- Distinguish by label and line style, not by colour alone.
- Numbers and labels in the animation equal worksheet and solution.
- Arrowheads: draw each as its own small `<path>`; `marker-end` heads did not show in the print key frames (tested in Chrome). Direction of an arrow is content - check it in the print view.
- Labels never cross a curve, an arrow or another label in any step; a label sits next to the element it names; step through all steps before finishing.
- Print: one key frame per row. In-picture text `font-size` at least viewBox width ÷ 51 (720 → 15, 880 → 18), or it prints below 10 pt on A4.
- One paradigm per figure; a second view goes in a second figure.

## Mehrspeichermodell (Atkinson & Shiffrin 1968) - E2.1
| Item | Content |
|---|---|
| Explains | how information passes from the senses into lasting memory, and where it is lost |
| Stores | sensorisches Register (Ultrakurzzeitgedächtnis): large capacity, visual under 1 s, auditory a few seconds · Kurzzeitgedächtnis: about 7 ± 2 units (Miller 1956; newer: about 4 chunks), about 20-30 s without rehearsal (Peterson & Peterson 1959: under 10 % after 18 s) · Langzeitgedächtnis: capacity and duration practically unlimited |
| Processes (arrows) | Reiz → sensorisches Register · Aufmerksamkeit → Kurzzeitgedächtnis · Wiederholen (Rehearsal) keeps it there (loop) · Enkodierung → Langzeitgedächtnis · Abruf → back into the Kurzzeitgedächtnis · Vergessen: Zerfall (Register), Zerfall and Verdrängung durch neue Einheiten (displacement) (Kurzzeit), Interferenz and Abrufversagen (Langzeit) |
| Must be right | order of the stores; attention is the filter between register and short-term store; retrieval runs back into the short-term store; "7 ± 2" are units (chunks), not letters |
| Limit | short-term store is not one unit (Arbeitsgedächtnis, Baddeley & Hitch 1974); repetition alone explains little - depth of processing matters (Craik & Lockhart 1972); long-term memory has several systems |
| Animation | 1 stimulus arrives, three empty stores · 2 sensory register: many items, fades in under 1 s · 3 attention: few items pass · 4 short-term store: about 7 units, rehearsal loop · 5 without rehearsal: lost after about 20-30 s · 6 encoding into long-term store · 7 retrieval back |

## Arbeitsgedächtnis (Baddeley & Hitch 1974; Baddeley 2000) - E2.1
- Zentrale Exekutive (directs attention, no storage) controls: phonologische Schleife (speech-based, about 2 s of speech), visuell-räumlicher Notizblock, episodischer Puffer (added 2000; links to long-term memory).
- Evidence type: dual tasks - two verbal tasks disturb each other, a verbal and a spatial task much less.
- Figure; animation only for a dual-task demonstration (two streams competing for one subsystem vs. using two).

## Langzeitgedächtnis: systems - E2.1
- deklarativ (explizit): episodisch (events), semantisch (facts) · nicht-deklarativ (implizit): prozedural (skills), Priming, konditionierte Reaktionen.
- Static tree figure.

## Vergessenskurve (Ebbinghaus 1885) - E2.1
- Axes: x = time since learning (not linear: 20 min, 1 h, 9 h, 1 d, 2 d, 6 d, 31 d), y = Ersparnis in %. Values: `studien.md`.
- Limit: n = 1, nonsense syllables. Animation: points appear in time order, curve drawn through them; last step: repetition raises the curve (spaced repetition as principle, without invented numbers unless labelled).

## Klassische Konditionierung (Pavlov) - E1.3, Q2.1
| Phase | Picture | Terms |
|---|---|---|
| Vor der Konditionierung | Futter → Speichelfluss; Glocke → no salivation (Orientierungsreaktion) | UCS (unkonditionierter Reiz) → UCR; NS (neutraler Reiz) |
| Während | Glocke shortly before Futter → Speichelfluss, several times | NS + UCS → UCR |
| Nach | Glocke alone → Speichelfluss | CS (konditionierter Reiz) → CR |
| Löschung | Glocke repeatedly without Futter → reaction fades; Spontanerholung after a pause | Extinktion |

- Must be right: NS before UCS (short interval); CR is usually weaker than UCR; German abbreviations vary (US/UR/CS/CR or UCS/UCR) - use the course's set, one set per file.
- Animation: 1 before: food → saliva · 2 before: bell → none · 3 pairing · 4 repeated pairing · 5 after: bell → saliva, labels switch NS → CS · 6 extinction.

## Operante Konditionierung (Skinner) - Q2.1
| | Reiz kommt hinzu | Reiz fällt weg |
|---|---|---|
| angenehmer Reiz | positive Verstärkung → Verhalten häufiger | negative Bestrafung (Entzug) → seltener |
| unangenehmer Reiz | positive Bestrafung → seltener | negative Verstärkung → häufiger |

- "positiv / negativ" = added / removed, not good / bad. Static 2 × 2 table; animation only for reinforcement schedules (response rate over time).

## Lernen am Modell (Bandura) - E2.4
- Four processes: Aufmerksamkeit → Behalten (Gedächtnis) → Reproduktion (motorische) → Motivation (Verstärkung: direkt, stellvertretend, Selbstverstärkung). Aneignung ≠ Ausführung. Step figure; animation optional (4 steps).

## Transaktionales Stressmodell (Lazarus & Folkman 1984) - Q4.1, E2.3
- Reiz (Stressor) → primäre Bewertung (irrelevant · positiv · stressend: Schaden/Verlust, Bedrohung, Herausforderung) → sekundäre Bewertung (reichen die Ressourcen?) → Stress when demands exceed resources → Coping (problemorientiert · emotionsorientiert) → Neubewertung.
- Must be right: stress arises from the appraisal, not from the stimulus alone; "primary / secondary" is no fixed time order.
- Animation: 1 stressor · 2 primary appraisal, three outcomes · 3 secondary appraisal · 4 stress · 5 coping, two paths · 6 reappraisal arrow back.

## Piaget: Assimilation, Akkommodation - Q1.2
- Schema meets experience → fits: Assimilation · does not fit: Ungleichgewicht → Akkommodation (schema changed or new) → Äquilibration. Example with an invented child ("Hund" schema meets a cat).
- Stages (approximate ages): sensumotorisch 0-2 · präoperational 2-7 · konkret-operational 7-11 · formal-operational from about 11/12.
- Animation: the schema example in 5 steps. Stage table static.

## Static figures (no animation)
| Model | Level | Must be right |
|---|---|---|
| Drei-Instanzen-Modell (Freud) | E1.3, Q2.1 | Es (Lustprinzip), Ich (Realitätsprinzip, mediates), Über-Ich (Moralprinzip); topographic model separate: bewusst, vorbewusst, unbewusst; label as historical, hard to test |
| Erikson, 8 Stufen | Q1.1 | each stage a crisis pair (Urvertrauen vs. Urmisstrauen ... Ich-Integrität vs. Verzweiflung); ages approximate |
| Kohlberg | Q1.1 | präkonventionell, konventionell, postkonventionell; two stages each; reasoning counts |
| Big Five | Q2.1, Q2.4 | Neurotizismus, Extraversion, Offenheit für Erfahrungen, Verträglichkeit, Gewissenhaftigkeit; dimensions, not types |
| Bedürfnishierarchie (Maslow) | E2.2 | physiologische Bedürfnisse, Sicherheit, soziale Bedürfnisse, Wertschätzung, Selbstverwirklichung; order not strict; pyramid not Maslow's |
| Risiko-Wahl-Modell (Atkinson) | E2.2 | success-motivated persons prefer medium difficulty, failure-avoiding persons very easy or very hard tasks |
| Weiner | E2.2 | 2 × 2 (internal/external × stabil/variabel): Fähigkeit, Anstrengung, Aufgabenschwierigkeit, Zufall; plus Kontrollierbarkeit |
| Johari-Fenster | Q3.4 | öffentlich, blinder Fleck, verborgen, unbekannt; a communication tool, not an empirical model |
| Gestaltgesetze | E1.4 | Nähe, Ähnlichkeit, Geschlossenheit, gute Fortsetzung, Prägnanz - own simple SVG figures; never copy published illusion artwork |
