# Review: nawi-technik · jg09 · kettengetriebe
Date: 2026-11-11 22:14 · Skill: darshan-singh-meel-schule-nwt-review · Files: unterricht/nawi-technik/jg09/kettengetriebe/{stundenentwurf,arbeitsblatt,loesung,animation}.html
Verdict: Einsatzbereit
Counts: Must 0 · Should 5 · Other 2 · Check script: 0 errors, 0 warnings (check_material.py), 0 lines (check_einheiten.py)

## Must
- none

## Should
- **animation.html · stage** - what: the axis label "Weg / distance in m" runs out of the picture at the right; "U = 2,10 m" and "Kurbel / crank" are covered by the valve mark and the crank in steps 2-4 · why: labels unreadable in the key frames (base area 9, N10) · fix: axis label below the scale at the left; "U = 2,10 m" left of the hub; "Kurbel / crank" outside the circle the crank sweeps.
- **animation.html · intro line** - what: "Maßstab im Bild: 2 Bildeinheiten Radius pro Zahn" · why: students cannot use picture units · fix: "Die Radien von Kettenblatt und Ritzel verhalten sich wie die Zähnezahlen 44 und 22".
- **arbeitsblatt.html · Aufgabe 4** - what: one requirement, not marked Muss/Wunsch; "ganze Zähnezahl" stands only in the solution · why: N5 (requirements explicit and testable) · fix: "Anforderungen (Muss): ganze Zähnezahl; bei 60 Kurbelumdrehungen pro Minute fährt das Fahrrad zwischen 12,0 km/h und 13,0 km/h".
- **arbeitsblatt.html · info box, Aufgabe 2, 3, Versuch step 1; loesung.html · Aufgabe 3, 4** - what: `zu wörtlich`: "it holds:", "Calculate for z1 = 44 ... the number ...", "Count on the stationary bicycle the teeth", "60 turns ... are 1 turn" · why: German word order · fix: "the following holds:", "Calculate the number ... for z1 = 44 ..." (German line reordered the same way), "On the stationary bicycle, count the teeth", "is 1 turn".
- **arbeitsblatt.html · Aufgabe 1 table** - what: columns z1, z2, U are about 8 mm wide in print · why: answer space too small for handwriting (base area 9) · fix: column widths 13 %, 13 %, 16 %.

## Other
- Derailleur bikes: when the bike is pushed backwards the chain can go slack; the stop rule covers it - try the method with one bike before the lesson.
- Aufgabe 1 asks for measuring, entering and one comparison calculation under one operator; acceptable in ungraded work.

## Nachgerechnet
| Task | Given | Own result (way 1) | Check (way 2 or estimate) | Material says | Match |
|---|---|---|---|---|---|
| 1 (example) | z1 = 44, z2 = 22, U = 2,10 m, measured 4,15 m | 4,20 m; deviation 0,05 m = 1,2 % | 2 wheel turns · 2,10 m | 4,20 m; 0,05 m; about 1 % | yes |
| 2 | z1 = 44, z2 = 22, U = 2,10 m | n2 = 2; 4,20 m | 44 links / 22 teeth = 2 turns | 2; 4,20 m | yes |
| 3 · z2 = 11 | 60 turns/min = 1 turn/s | 4; 8,40 m; 30,24 → 30,2 km/h | 8,40 m/s · 3,6 | 4; 8,40; 30,2 | yes |
| 3 · z2 = 16 | | 2,75; 5,775 → 5,78 m; 20,79 → 20,8 km/h | from the rounded value: 5,78 · 3,6 = 20,8 | 2,75; 5,78; 20,8 | yes |
| 3 · z2 = 22 | | 2; 4,20 m; 15,12 → 15,1 km/h | | 2; 4,20; 15,1 | yes |
| 3 · z2 = 32 | | 1,375; 2,8875 → 2,89 m; 10,395 → 10,4 km/h | from the rounded value: 2,89 · 3,6 = 10,4 | 1,375; 2,89; 10,4 | yes |
| 4 | 12,0-13,0 km/h | v = 332,64 km/h / z2 → 25,6 < z2 < 27,7 → 26 (12,79) or 27 (12,32) | 25 → 13,31; 28 → 11,88: both outside | 26 (12,8), 27 (12,3); 25 and 28 excluded | yes |
| Hausaufgabe | 38, 19, 2,10 m | 4,20 m | same ratio as 44/22 | 4,20 m | yes |
| animation | quarter turns | crank 90° · k, wheel 180° · k, chain 11 teeth per step, distance 1,05 m · k; same sense of rotation | chain travel 138,2 px = 11 · 12,57 px | same; step 6: 4 · 2,10 m = 8,40 m | yes |

All valid solutions of the open task 4: 26 and 27 teeth; both are in the model solution, the criterion is named.

## Checked without findings
N1 anchor (Wahlunterricht line, KC Physik standard and Inhaltsfeld as printed, no NWT-Kerncurriculum cited, Mittelstufe) · N2 results · N3 science (no efficiency claim; ratio the right way round) · N4 units, digits, plausibility (44 and 11-32 teeth, 2,10 m, 10-30 km/h at 60 per minute) · N6 buildable and testable (bike, chalk, tape; five steps in a workable order) · N8 safety block complete, no tools, no home hazard · N9 no Noten key, grid referred to as a proposal · base 1-6, 8, 11, 12; phases 8+25+12+22+10+10+3 = 90 min.

## Not checked
The school's NWT curriculum and whether the course is graded (unknown) · per-device tool permissions (not needed: no tools) · play at each speed in a live browser (all key frames were rendered headless instead).

## Nach Korrektur
All five Should items applied; both scripts: 0 errors, 0 lines; `node --check` passes; no number changed. Verdict: Einsatzbereit.
