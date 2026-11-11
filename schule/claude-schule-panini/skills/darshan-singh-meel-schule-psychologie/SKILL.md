---
name: darshan-singh-meel-schule-psychologie
description: Teaching material for Psychologie in the Oberstufe (Hessen) - lesson plans, worksheets with solutions, tests and Klausuren with Erwartungshorizont, explanations for students, and animations of models (memory models, conditioning, stress appraisal, stage theories). German with the closest natural English sentence under every line. Follows the only Hessen curriculum for the subject - Kerncurriculum berufliches Gymnasium, Fachrichtung Gesundheit und Soziales, Schwerpunkt Erziehungswissenschaft, Fach Psychologie (E1-Q4, Grundkurs) - and serves as orientation for school-own Psychologie courses at a Gymnasium. Covers accurate description of studies (sample, design, result, criticism, replication), research ethics, and safe handling of clinical topics and classroom experiments. Use with darshan-singh-meel-schule. Triggers - "Psychologie Unterricht", "Psychologiekurs", "Psychologie Oberstufe", "Gedächtnismodell", "Mehrspeichermodell", "Arbeitsgedächtnis", "Konditionierung", "Lernen am Modell", "Wahrnehmung", "Gestaltgesetze", "Piaget", "Erikson", "Freud Instanzenmodell", "Big Five", "Milgram", "Asch", "Konformität", "Stress Lazarus", "Experiment auswerten", "Korrelation und Kausalität", "Fallanalyse Psychologie"; "psychology lesson", "psychology worksheet", "memory model animation", "classical conditioning worksheet", "describe a psychology study", "research ethics lesson", "bilingual psychology German English".
---

# Psychologie (Hessen, Oberstufe)
Load `darshan-singh-meel-schule` first (formats, folders, DE + EN rule, grading, setup, `check_material.py`) → this file adds the subject.

## Scope: how Hessen offers the subject
- Berufliches Gymnasium · Gesundheit und Soziales · Schwerpunkt Erziehungswissenschaft · Fach Psychologie E1-Q4, Q-phase Grundkurs · KCBG Ausgabe 2024, Stand 01.08.2025 (official lists read 2026-11-11) · `references/kcbg.md`
- Gymnasium Oberstufe (allgemeinbildend) · no KCGO · only school-own course · no state curriculum, no Abitur → use `kcbg.md` as orientation · write `Orientierung: KCBG Psychologie` in KC table · ask for school's course plan · `check: OAVO` whether/how such a course counts.
- Gymnasium Jg. 5-10 · no KC Sek I · not covered → AG/Wahlunterricht only on request, marked `ohne Kerncurriculum`.
- Output `unterricht/psychologie/<e | q1-gk … q4-gk>/<thema>/` · neighbours elsewhere: Erziehungswissenschaft (same KCBG, not covered) · Biologie Q Neurobiologie · Ethik.

## Rules
- Studies exactly → researchers · year · sample (n, who) · design (variables, conditions, control) · result as number with reference (`37 % der Urteile in den kritischen Durchgängen`, not `die meisten`) · main criticism · replication status · facts from `references/studien.md` · study not listed → primary source or `check:` · never numbers from memory.
- Finding ≠ proof → `Die Studie stützt …`, `sprechen für …`, never `beweist` · correlation never cause · a model is a model → name what it explains + one limit.
- Paradigms side by side → Tiefenpsychologie · Behaviorismus · Kognitivismus · Humanismus (+ biopsychological, trait) each with Menschenbild · method · strength · criticism · never say which is right · contested/historical theories (Freud, stage models, Maslow) labelled.
- Ethics in every study task → one part asks/states informed consent · deception · harm · right to withdraw · debriefing · could it run today (`fachregeln.md`).
- No diagnosis, no self-disclosure → cases = invented persons, marked · never diagnose self, classmates, relatives, real public persons · never ask for own disorders, family matters, test scores · self-test only as method demo: anonymous · voluntary · uncollected · ungraded.
- Clinical topics → criteria + classification (ICD/DSM) · no stigma words · no self-harm method details · help route named (`fachregeln.md`).
- Classroom experiments → harmless only (memory span, Stroop, optical illusions, reaction time) · voluntary · anonymous · debriefing · classic deception/stress studies analysed, never re-enacted.
- Statistics → Stichprobe · Mittelwert · Korrelation · Signifikanz with meaning + limit · r, p read, never computed · no significance test in tasks (`kcbg.md` level guide) · invented data `Modelldaten (erfunden)`.
- KC cite → Kompetenz code (`K2.5`) + AFB + Leitidee (`L1`) + Themenfeld (`E2.1`) · wording from `kcbg.md`.

## Process
1. Setup → base questions, one AskUserQuestion + subject options:
   - Kurs · berufliches Gymnasium, Schwerpunkt Erziehungswissenschaft (rec) · schuleigener Kurs (ask course plan)
   - Thema · 3 topics from the Themenfeld of the Kurshalbjahr
   - Q-phase → Themenfelder per Erlass: ask, or `check: Abiturerlass`
2. Read `kcbg.md` (Kurshalbjahr) · `fachregeln.md` · `studien.md` (study) · `modelle-animationen.md` (model/animation).
3. Plan in 5 lines (base step 3) + studies with fact rows · paradigm(s) · ethics part · model + limit.
4. Create from base templates → material (case, study summary, data) → tasks → solution → lesson plan → animation.
5. Self-check → solve each task from material alone · recompute numbers, %, means · every study fact vs `studien.md` (year, n, design, result, criticism), mismatch → fix or `check:` · every model: components, order, arrows, capacity/duration as in `modelle-animationen.md`, limit named · wording: no `beweist`, no cause from correlation, no paradigm declared right · ethics + safety test passed, cases invented + marked · operator fits AFB (base `operatoren.md`) · EN: `auswerten` → analyse, `beurteilen` → assess, never "evaluate" for both.
6. Layout → `python <base skill dir>/scripts/check_material.py <folder>` → fix every FAIL, read every `?`.
7. Hand over → files (relative) · KC ref · studies used · every `check:` · offer `darshan-singh-meel-schule-psychologie-review` (optional).

## Animation
- Use for processes/sequences: information flow through memory stores · classical conditioning phases · reinforcement over time · primary → secondary appraisal → coping · assimilation/accommodation · forgetting curve drawn · static structures (Instanzenmodell, Big Five, Bedürfnispyramide, Johari-Fenster) → figures in `erklaerung.html` · step plans `modelle-animationen.md`.

## References
- `references/kcbg.md` · always: how offered, competences K1-K5, Leitideen L1-L4, Themenfelder E1-Q4, what is binding
- `references/fachregeln.md` · always: study description, ethics, safety, material types, methods + statistics, typical mistakes
- `references/studien.md` · classic study described, used, asked
- `references/modelle-animationen.md` · model, figure, animation
- `references/begriffe.md` · glossary DE | EN, false friends
- `references/examples/mehrspeichermodell/` · finished E2.1 worksheet + solution + animation
- `references/sources.md` · where each fact comes from, what is unverified
