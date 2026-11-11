# Review: physik · jg07 + q2-gk · geschwindigkeit, federpendel
Date: 2026-11-11 22:14 · Skill: darshan-singh-meel-schule-physik-review · Files: unterricht/physik/jg07/geschwindigkeit/{stundenentwurf,arbeitsblatt,loesung,animation}.html · unterricht/physik/q2-gk/federpendel/{test,erwartungshorizont}.html
Verdict: Einsatzbereit nach Must-Korrekturen
Counts: Must 1 · Should 6 · Other 2 · Check script: 0 errors, 0 warnings (check_material.py), 0 lines (check_einheiten.py)

## Must
- **jg07/animation.html · STEPS, steps 5 and 6** - what: the captions `'Mia's speed ...'` and `'Tom's speed ...'` end the JavaScript string at the apostrophe; the script stops: no caption, no controls, no print frames · why: the animation does not run (base area 10); neither check script reports it · fix: escape the apostrophe (`Mia\'s`) or write ’; verify with `node --check` on the script and by stepping through all 6 steps.

## Should
- **jg07/arbeitsblatt.html · Versuch, step 3** - what: `zu wörtlich`: "Stoppt die Zeit von der Startlinie bis zur Ziellinie." / "Stop the time from the starting line to the finishing line." · why: "stop the time" is not English for timing · fix: "Time the walk from the starting line to the finishing line." Same calque in the safety row "Wer": "one stops the time" → "one takes the time".
- **jg07/arbeitsblatt.html · Aufgabe 1, 4; stundenentwurf.html · Transfer, Abschluss, Merksatz** - what: `zu wörtlich`: "form the mean value", "after which time ... which distance", "In this there are 2 min buffer", "By what do you recognise", "it holds:" · why: German word order or calque · fix: "work out the mean value", "after what time ... what distance", "This includes 2 min of buffer.", "How do you recognise", "the following holds:".
- **jg07/arbeitsblatt.html · print** - what: the experiment box (class `kasten`, cannot break) moves to page 2 and leaves page 1 three-quarters empty; Aufgabe 3 splits over two pages · why: base area 9 (no split task) · fix: experiment as a plain section; `break-inside:avoid` on each task.
- **jg07/arbeitsblatt.html · Aufgabe 1, 3, 4** - what: operators "Ermittle" and "Bestimme"; physics `sek1.md` listed them only for Stufe 2, base `operatoren.md` allows the science list from Jg. 7 · why: the two references disagree; the plan places the topic in Stufe 1 · fix: align `sek1.md` with the base (by Jahrgang); introduce both operators with a model answer before graded use.
- **jg07/stundenentwurf.html · Erarbeitung (20 min)** - what: marking 7 tracks, three timed walks, mean, calculation and Aufgabe 2 in 20 min · why: tight for groups of four outside the room · fix: mark start and finish lines before the lesson (note in the plan).
- **q2-gk/test.html · header, 2c; erwartungshorizont.html · key** - what: "formula collection in use" (`zu wörtlich`); "Determine with the help of the law ... the maximum speed" (German word order); key rows other than 5 and 11 Punkte carry the base `check:` · why: bilingual closeness; unverified rows · fix: "formula booklet used in class"; "Determine the maximum speed of the glider with the help of the law of conservation of energy."; verify with OAVO Anlage 9a (Bürgerservice Hessenrecht) before grading.

## Other
- q2-gk/test.html: page 1 holds only header and material; tasks start on page 2.
- q2-gk: the file is one of two Klausur tasks (45 of 90 min); AFB III is 20 % here - the second task decides the share of the whole Klausur.

## Nachgerechnet
| Task | Given | Own result (way 1) | Check (way 2 or estimate) | Material says | Match |
|---|---|---|---|---|---|
| jg07 · 1 (example) | s = 10,0 m; t = 7,2 s, 7,0 s, 7,1 s | mean 7,1 s; v = 1,408 → 1,4 m/s | 1,4 m/s · 7,1 s = 9,9 m; walking ≈ 1,4 m/s | 1,4 m/s | yes |
| jg07 · 2 | s = 45 m, t = 7,5 s | v = 6,0 m/s | 6,0 m/s · 7,5 s = 45 m; 21,6 km/h | 6,0 m/s; about 22 km/h | yes |
| jg07 · 3 | (2,5 s; 10,2 m), (5,0 s; 19,8 m), (7,5 s; 30,1 m) | least-squares slope through the origin 4,003 → 4,0 m/s | 30,1 m / 7,5 s = 4,01 m/s | 4,0 m/s (3,9-4,1 accepted) | yes |
| jg07 · 4 | 6,0 m/s; 4,0 m/s; 20 m lead | 6,0·t = 20 + 4,0·t → t = 10 s; s = 60 m | closing speed 2,0 m/s; Tom at 20 m + 40 m = 60 m | 10 s; 60 m | yes |
| jg07 · Hausaufgabe | 195 m, 15 s | 13 m/s = 46,8 → 47 km/h | 13 · 3,6 | 13 m/s = 47 km/h | yes |
| jg07 · animation | 6,0 m/s, 4,0 m/s; t = 2,5 s, 5,0 s, 7,5 s | A: 15, 30, 45 m · B: 10, 20, 30 m | positions recomputed: track 12 px/m, graph 40 px/s and 4 px/m | same | yes |
| q2 · 1b | m = 0,300 kg, D = 12,0 N/m | T = 0,99346 → 0,993 s; f = 1,0066 → 1,01 Hz | ω = √(D/m) = 6,3246 1/s → T = 2π/ω | 0,993 s; 1,01 Hz | yes |
| q2 · 2a | ŝ = 5,00 cm | s(t) = 5,00 cm · sin(6,32 1/s · t) | s(0) = 0, rising | same | yes |
| q2 · 2b | s = 2,50 cm | ω·t = π/6 → t = 0,08279 → 0,0828 s | T/12 = 0,08279 s | 0,0828 s | yes |
| q2 · 2c | D, ŝ, m | E = 0,0150 J; v = 0,31623 → 0,316 m/s | v = ŝ·ω = 0,0500 m · 6,3246 1/s | 0,0150 J; 0,316 m/s | yes |
| q2 · 3a | 10·T = 5,8 s; 8,1 s; 10,0 s; 11,4 s | T/√m = 1,834; 1,811; 1,826; 1,802 s/√kg; mean 1,818 | theory 2π/√D = 1,814; largest deviation 0,9 % | 1,83; 1,81; 1,83; 1,80; mean 1,82; below 2 % | yes |
| q2 · 3b | statement on the amplitude | false: T has no ŝ; F and v scale with ŝ; limit: linear force law | v_max = ŝ·ω doubles | same key points | yes |
| q2 · points | 4+4+3+4+5+4+6 | 30 BE; AFB 8/16/6 = 26,7/53,3/20 % | key 30 · percent (28,5 ... 9,9; 8,1; 6) | 30; 27/53/20 %; same key | yes |

## Checked without findings
1 Curriculum fit (KC wording as in `sek1.md` / `oberstufe.md`; all Q2.1 content is grundlegendes Niveau) · 2 Subject correctness · 5 Marking scheme · 6 Language level · 8 Differentiation · 11 Privacy and copyright · 12 Files and form · P4 units · P5 digits · P6 plausibility · P7 models · P8 figures · P9 experiment safety (walking track; no electrical or optical hazard).

## Not checked
School grade key and the year of the topic in the Fachcurriculum (unknown) · OAVO Anlage 9a rows (base `check:`) · play at each speed in a live browser (all key frames were rendered headless instead).

## Nach Korrektur
Must 0 · Should 1 open (OAVO Anlage 9a rows: verify before grading). Apostrophes escaped, English lines replaced, print breaks fixed, plan note added, `sek1.md` aligned with the base. Both scripts: 0 errors, 0 lines; `node --check` passes; no number changed. Verdict: Einsatzbereit.
