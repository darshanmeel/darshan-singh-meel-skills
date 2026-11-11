# Persönlichkeit, Situational Judgement, Interessen, Cultural Fit

These parts have no right or wrong answer (provider statement for personality questionnaires: `ziel.md`, Aon). The skill therefore never writes a key for them and never trains a "best profile". It teaches what the part measures, how it is answered, and what an employer reads from it.

## Honesty rule (not negotiable)
- Never tell a learner which answers make a "good" profile, how to look more extraverted or conscientious than they are, or how to beat a questionnaire.
- Allowed and wanted: explain the format, the scale, why similar statements return, what the occupation demands, and how to answer truthfully and quickly.
- Reasons to give the learner:
  - the employer compares the profile with the job; a faked profile leads to an Ausbildung that does not fit the person;
  - interview and probation period show the real behaviour;
  - questionnaires ask the same trait several times in different words; answers that contradict each other stand out. `check:` the provider's page for whether a given questionnaire scores consistency.
- A learner who asks "what should I tick?" gets: what the statement measures, what the occupation needs, and the question "Wie verhältst du dich wirklich - in der Schule, im Praktikum, im Verein?".

## Item form in the JSON
| Kind | `module` | `question` | `options` (exactly 4) | `answer` | `time_seconds` |
|---|---|---|---|---|---|
| Statement | `persoenlichkeit` | one statement in the first person: "Ich plane meine Aufgaben, bevor ich anfange." | the scale: `trifft gar nicht zu` · `trifft eher nicht zu` · `trifft eher zu` · `trifft voll zu` | `-1` | 20 (questionnaires are usually untimed) |
| Situation | `sjt` | 2-4 sentences: a situation an Azubi can meet (customer complains, mistake noticed, colleague asks for help while you are busy, unclear instruction), then "Was tust du am ehesten?" | four reactions that all sound possible, one sentence each, same length | `-1` | 45-90 |
| Interests / Cultural Fit | `persoenlichkeit` | preference statement: "Ich arbeite lieber nach festen Abläufen als jeden Tag anders." | scale as above | `-1` | 20 |

- No `check`. `difficulty`: 1 for statements; SJT 1-3 by how close the reactions are.
- Statements: one idea each, no double negation, no "immer"/"nie", nothing private (health, family, religion, politics, origin). Half of the statements of a trait are worded the other way round ("Ich schiebe unangenehme Aufgaben oft auf.").
- Situations: from school, internship, part-time job, first weeks of an Ausbildung. No situation that needs occupation knowledge; no reaction that is plainly rude or illegal - weak reactions are passive, hasty or shift the problem.

## Explanation (replaces way · mistake · trick)
Statement:
1. **Misst:** the trait in plain words (e.g. Gewissenhaftigkeit: planning, care, keeping promises).
2. **Arbeitgeber achten auf:** where the trait matters in an Ausbildung, with one example; that both ends of the scale have a meaning (very high planning can mean little flexibility).
3. **So antwortest du:** the first honest impulse; think of real situations; no middle-hunting, no pattern.

Situation:
1. **Darum geht es:** the competence in the situation (Kundenorientierung, Verantwortung, Teamarbeit, Umgang mit Fehlern, Regeln und Sicherheit).
2. **Was jede Reaktion zeigt:** one clause per reaction, named by its content ("Abwarten …"), not by its letter - what it shows and what it costs (solves it now but skips the trainer; honest but late; friendly but passes the problem on).
3. **Arbeitgeber achten auf:** the behaviours most postings for Azubis name - asks when unsure, reports own mistakes early, stays polite under pressure, keeps safety and data rules, finishes what was promised. Then: "Wähle, was du wirklich tun würdest."

- The explanation never says "richtig ist …" or ranks the options 1-4. It may say which reactions fit the named competence better and why, in the words "passt eher / passt weniger zu".
- Some real SJTs score against an employer's key and ask for "best" and "worst" reaction: `check:` the provider's page. Practice still explains instead of keying, because the key of one employer is not the key of another.

## Traits to cover (own working list)
| Trait | Azubi example | Reverse-worded statement |
|---|---|---|
| Gewissenhaftigkeit | checks a delivery note before signing | "Details überfliege ich meistens." |
| Teamfähigkeit / Verträglichkeit | helps a colleague, accepts feedback | "Ich arbeite am liebsten ganz für mich." |
| Extraversion / Kontaktfreude | speaks to customers first | "Vor fremden Menschen sage ich lieber wenig." |
| Belastbarkeit / emotionale Stabilität | stays calm when three things come at once | "Unter Zeitdruck verliere ich schnell den Überblick." |
| Offenheit / Lernbereitschaft | tries a new program without being told | "Ich bleibe am liebsten bei dem, was ich kenne." |
| Leistungsmotivation | sets own goals in Berufsschule | "Mir reicht es, wenn es gerade so genügt." |
| Kundenorientierung, Regelbewusstsein | occupation-dependent | - |

Trait names are general psychology terms; a provider's own scale names are not copied (`check:` its page).

## Chapter for these modules
- `concept`: what the part is, that there is no right or wrong, that it is usually untimed, how the scale works, why similar statements return.
- `example`: one statement and one situation, each with the explanation above.
- `tips`: read each statement once and answer; picture real situations; same honesty in every block; do not choose the middle to stay safe; take the part rested, not last at night.
- `traps`: "Ein Persönlichkeitstest ist ein Vergleich mit dem Beruf, nicht eine Prüfung mit richtigen Antworten." · "Ein ehrliches Profil ist ein Vorteil für dich, nicht ein Risiko."

## On sheets and in mock tests
- Own block at the end, heading "Fragebogen (ohne Punkte) / Questionnaire (not scored)", untimed, no `data-punkte`.
- Key file: `data-loesung="-"`, the explanation, and a reflection line: "Welche zwei Aussagen beschreiben dich am besten? Nenne für jede ein Beispiel aus Schule oder Praktikum."
- Mock tests never score these answers and never call a profile good or bad.
