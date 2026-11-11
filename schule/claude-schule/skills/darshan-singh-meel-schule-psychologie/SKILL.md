---
name: darshan-singh-meel-schule-psychologie
description: Teaching material for Psychologie in the Oberstufe (Hessen) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations for students, and animations of models (memory models, conditioning, stress appraisal, stage theories). German with the closest natural English sentence under every line. Follows the only Hessen curriculum for the subject - Kerncurriculum berufliches Gymnasium, Fachrichtung Gesundheit und Soziales, Schwerpunkt Erziehungswissenschaft, Fach Psychologie (E1-Q4, Grundkurs) - and serves as orientation for school-own Psychologie courses at a Gymnasium. Covers accurate description of studies (sample, design, result, criticism, replication), research ethics, and safe handling of clinical topics and classroom experiments. Use with darshan-singh-meel-schule. Triggers - "Psychologie Unterricht", "Psychologiekurs", "Psychologie Oberstufe", "Gedächtnismodell", "Mehrspeichermodell", "Arbeitsgedächtnis", "Konditionierung", "Lernen am Modell", "Wahrnehmung", "Gestaltgesetze", "Piaget", "Erikson", "Freud Instanzenmodell", "Big Five", "Milgram", "Asch", "Konformität", "Stress Lazarus", "Experiment auswerten", "Korrelation und Kausalität", "Fallanalyse Psychologie"; "psychology lesson", "psychology worksheet", "memory model animation", "classical conditioning worksheet", "describe a psychology study", "research ethics lesson", "bilingual psychology German English".
---

# Psychologie (Hessen, Oberstufe)

Load `darshan-singh-meel-schule` first: it owns formats, folders, the German + English line rule, grading, the setup questions and the check script. This skill adds subject content only.

## Scope: how Hessen offers the subject
| Where | Status (official lists read 2026-11-11) | Curriculum used |
|---|---|---|
| Berufliches Gymnasium, Fachrichtung Gesundheit und Soziales, Schwerpunkt Erziehungswissenschaft | Fach Psychologie, E1-Q4; Qualifikationsphase as Grundkurs | KCBG Ausgabe 2024, Stand 01.08.2025 → `references/kcbg.md` |
| Gymnasium, Oberstufe (allgemeinbildend) | no KCGO for Psychologie; a course exists only as a school's own offer | no state curriculum, no Abitur exam: use `kcbg.md` as orientation, write `Orientierung: KCBG Psychologie` in the KC table, ask for the school's course plan. check: OAVO whether and how such a course counts |
| Gymnasium, Mittelstufe (Jg. 5-10) | no Kerncurriculum Sek I for Psychologie | not covered; AG or Wahlunterricht material only on request, marked `ohne Kerncurriculum` |

- Output folder: `unterricht/psychologie/<e | q1-gk ... q4-gk>/<thema>/`.
- Neighbouring content elsewhere: Erziehungswissenschaft (same KCBG, not covered), Biologie Q-phase Neurobiologie, Ethik.

## Rules (on top of the base rules)
- **Studies exactly.** Each study in material carries: researchers, year of publication, sample (n, who), design (variables, conditions, control), result as a number with its reference (`37 % der Urteile in den kritischen Durchgängen`, not `die meisten`), main criticism, replication status. Facts from `references/studien.md`; a study not listed there → primary source or `check:`; never numbers from memory.
- **Finding ≠ proof.** Wording: `Die Studie stützt ...`, `Die Ergebnisse sprechen für ...`; never `beweist`. Correlation is not presented as cause. A model is a model: name what it explains and one limit.
- **Paradigms side by side.** Tiefenpsychologie, Behaviorismus, Kognitivismus, Humanismus (and biopsychological, trait views) each with Menschenbild, method, strength, criticism. Material never states which one is right; contested or historical theories (Freud, stage models, Maslow) are labelled as such.
- **Ethics in every study task.** One part asks for or states: informed consent, deception, harm, right to withdraw, debriefing - and whether the study could run today. `references/fachregeln.md`.
- **No diagnosis, no self-disclosure.** Cases are invented persons, marked invented. Tasks never ask students to diagnose themselves, classmates, relatives or real public persons, or to report own disorders, family matters or test scores. Self-tests only as method demonstration: anonymous, voluntary, results not collected, not graded.
- **Clinical topics with care.** Disorders described by criteria and classification (ICD/DSM), without stigma words, without method details of self-harm; help route named (`fachregeln.md`).
- **Classroom experiments** only harmless (memory span, Stroop, optical illusions, reaction time), voluntary, anonymous data, with debriefing; classic deception or stress studies are analysed, never re-enacted.
- **Statistics used correctly.** Stichprobe, Mittelwert, Korrelation, Signifikanz with their meaning and limit; r and p are read, never computed; no significance test in tasks (`kcbg.md` level guide); invented data labelled `Modelldaten (erfunden)`.
- **KC citation.** Kompetenz code (`K2.5`) + AFB + Leitidee (`L1`) + Themenfeld (`E2.1`). Wording from `kcbg.md`.

## Process (fixed)
1. **Setup** - the base questions (one AskUserQuestion prompt). Subject additions inside them:
   - Kurs: berufliches Gymnasium, Schwerpunkt Erziehungswissenschaft (Recommended) · schuleigener Kurs am Gymnasium (ask for the course plan).
   - Thema: 3 topics from the Themenfeld of the Kurshalbjahr.
   - Q-phase: Themenfelder set by Erlass - ask, or mark `check: Abiturerlass`.
2. **Read** `references/kcbg.md` (the Kurshalbjahr), `references/fachregeln.md`; `studien.md` when a study appears; `modelle-animationen.md` for a model or animation.
3. **Plan in 5 lines** (base step 3) plus: studies used with their fact rows, the paradigm(s), the ethics part, the model and its limit.
4. **Create** from the base templates. Order: material (case, study summary, data) → tasks → solution → lesson plan → animation.
5. **Self-check every task and answer** before the layout check:
   - solve each task from the material alone; recompute every number, percentage, mean;
   - every study fact against `studien.md` (year, n, design, result, criticism); mismatch → fix or `check:`;
   - every model: components, order, arrows, capacity and duration figures as in `modelle-animationen.md`; limit named;
   - wording test: no `beweist`, no cause from correlation, no paradigm declared right;
   - ethics and safety test of `fachregeln.md` passed; cases invented and marked;
   - operator fits the AFB (base `references/operatoren.md`); English line: `auswerten` → analyse, `beurteilen` → assess, never "evaluate" for both.
6. **Layout check** - `python <base skill dir>/scripts/check_material.py <folder>`; fix every FAIL, read every `?`.
7. **Reply** with files (relative paths), KC reference, studies used, every `check:`. Offer the review by `darshan-singh-meel-schule-psychologie-review` (optional).

## Animation: when
For processes and sequences: information flow through the memory stores, the phases of classical conditioning, reinforcement over time, primary → secondary appraisal → coping, assimilation and accommodation, the forgetting curve being drawn. Static structures (Instanzenmodell, Big Five, Bedürfnispyramide, Johari-Fenster) are figures in `erklaerung.html`. Step plans: `references/modelle-animationen.md`.

## References
| File | Read when |
|---|---|
| `references/kcbg.md` | always: how the subject is offered, competences K1-K5, Leitideen L1-L4, Themenfelder E1-Q4, what is binding |
| `references/fachregeln.md` | always: study description, ethics, safety, material types, methods and statistics, typical mistakes |
| `references/studien.md` | a classic study is described, used as material or asked about |
| `references/modelle-animationen.md` | a model, a figure or an animation |
| `references/begriffe.md` | glossary `DE | EN`; false friends |
| `references/examples/mehrspeichermodell/` | one worked output (E2.1, Mehrspeichermodell: Arbeitsblatt, Lösung, Animation) to copy the level of detail from |
| `references/sources.md` | where each fact comes from; what is not verified |
