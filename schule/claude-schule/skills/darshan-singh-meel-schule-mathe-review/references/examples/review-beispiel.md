# Review: mathematik · jg03, jg06, q1-gk · schriftliche-addition, brueche-addieren, integralrechnung
Date: 2026-11-11 22:12 · Skill: darshan-singh-meel-schule-mathe-review · Files: `unterricht/mathematik/jg03/schriftliche-addition/` (arbeitsblatt, loesung) · `unterricht/mathematik/jg06/brueche-addieren/` (stundenentwurf, arbeitsblatt, loesung, animation) · `unterricht/mathematik/q1-gk/integralrechnung/` (test, erwartungshorizont)
Verdict: Einsatzbereit nach Must-Korrekturen
Counts: Must 1 · Should 12 · Other 5 · Check script: 0 errors, 0 warnings (`check_material.py`); 0 failed checks, 0 tasks without check (`check_rechnung.py`)

## Must
- **jg03 · arbeitsblatt.html, loesung.html** - what: no KC reference anywhere in the folder (no Stundenentwurf; neither file names source, Kompetenzbereich, Inhaltsfeld) · why: base rule "every piece of material names its KC source" (area 1, M1) · fix: add under the title of `loesung.html`: `KC Hessen, Primarstufe, Mathematik · Inhaltsfeld Zahl und Operation (Grundrechenarten: schriftliches Rechenverfahren Addition) · Kompetenzbereiche Umgehen mit symbolischen, formalen und technischen Elementen; Argumentieren · Bildungsstandards Ende Jg. 4`.

## Should
- **q1-gk · test.html 3d** - what: "Beurteilen Sie die Aussage: 'Nach vier Stunden ist genau die Hälfte ... zugeflossen.'" is labelled AFB III, but it is solved by repeating the integral of 3b with the limit 4 · why: real demand is AFB II; the AFB III share falls from 20 % to 10 % (M7) · fix: general statement that needs an argument: "Für jede Zahl a mit 0 < a ≤ 4 fließt im Zeitraum von 4 − a bis 4 + a Stunden nach Regenbeginn genau doppelt so viel Wasser zu wie im Zeitraum von 4 − a bis 4 Stunden nach Regenbeginn."; Erwartungshorizont: symmetry of r about t = 4 (2 BE), conclusion for the integrals (1 BE), judgement (1 BE); one numerical example at most 2 BE.
- **q1-gk · erwartungshorizont.html, print** - what: the row "Summe 40" is printed at the bottom of every page of the table (pages 1-3) · why: `<tfoot>` repeats in print; on pages 1 and 2 the sum stands under partial lists (M13) · fix: `<tfoot style="display:table-row-group">`.
- **q1-gk · erwartungshorizont.html, print** - what: the points key breaks after the rows 15 and 14 · why: key not readable in one piece (M13) · fix: `style="break-inside:avoid"` on the section.
- **q1-gk · test.html tasks 1 and 2 (lead-in)** - zu wörtlich · DE: "Gegeben ist die in ℝ definierte Funktion f mit f(x) = 3x² − 4x + 5." · EN: "Given is the function f, defined on ℝ, with f(x) = 3x² − 4x + 5." · fix: "The function f defined on ℝ with f(x) = 3x² − 4x + 5 is given."
- **q1-gk · erwartungshorizont.html 2c, 2e** - Fachbegriff · DE: "Schnittstellen 2 BE", "Schnittstelle 4 − m" · EN: "Points of intersection", "Point of intersection 4 − m" · why: a Stelle is an x-value, not a point (`begriffe.md`) · fix: "Intersection x-values 2 marks", "Intersection x-value 4 − m 1 mark".
- **jg06 · arbeitsblatt.html task 3** - zu wörtlich · DE: "Begründe mit einer Rechnung, ob die Schorle in eine 1-Liter-Flasche passt." · EN: "Give reasons, with a calculation, whether the spritzer fits into a 1-litre bottle." · fix: "Justify with a calculation whether the spritzer fits into a 1-litre bottle."
- **jg06 · arbeitsblatt.html task 3, loesung.html task 3** - Fachbegriff/grammar · EN: "3/4 litres of apple juice and 2/5 litres of water", "3/20 litres too much" · why: singular after a fraction below one (M12) · fix: "3/4 litre of apple juice and 2/5 litre of water", "3/4 litre + 2/5 litre = 1 3/20 litres", "3/20 litre too much".
- **jg06 · arbeitsblatt.html info box, animation.html step 1 and Leitfrage, loesung.html task 4; jg03 · loesung.html task 3** - zu wörtlich · EN: "One can only add them once ...", "so one cannot simply add them up", "How does one add ...", "One stops after ...", "One only tries and does not give reasons ..." · why: impersonal "one" is not the register of English school material for Jg. 3 and 6 (base `bilingual.md`: "You" in lower years; passive stays passive) · fix: "You can only add them once ...", "so you cannot simply add them up", "How do you add ...", "The work is stopped after the first solution found.", "The numbers are only tried out, and no reasons are given why no smaller sum is possible."
- **jg03 · arbeitsblatt.html task 1** - zu wörtlich · DE: "Rechne schriftlich." · EN: "Calculate in writing." · fix: "Calculate using the written method."
- **jg06 · stundenentwurf.html Hausaufgabe** - what: "Wer Aufgabe 2 fertig hat, bearbeitet Aufgabe 3." · why: ★★ learners work on tasks 2 and 3 in the Transfer phase and ★★★ on task 4; for them the homework is empty or a step back · fix: "... bearbeitet Aufgabe 3 oder 4." / "... works on task 3 or 4."
- **jg03 · arbeitsblatt.html, print** - what: 4 printed pages for 3 tasks; the glossary breaks across pages 3 and 4 · why: Grundschule sheet should be one sheet front and back plus at most one page; split table (M13) · fix: glossary reduced to the terms the tasks use (Einer/Zehner/Hunderter, Summe, Übertrag, Ziffer), `break-inside:avoid` on the glossary section; info box and example side by side → 3 pages (info box · tasks 1-2 · task 3 + glossary).
- **jg03 · arbeitsblatt.html glossary** - what: "der Summand" is explained but does not occur on the sheet · why: glossary lists the terms of the material (base `formate.md`) · fix: remove the row.

## Other
- **q1-gk · erwartungshorizont.html points key** - thresholds 13,2 BE (3 Punkte) and 10,8 BE (2 Punkte) cannot be hit with whole BE; the note under the key covers it ("erreicht, wenn die Schwelle erreicht ist") - a column "ganze BE: 14 / 11" would save a calculation.
- **jg06 · arbeitsblatt.html, print** - 4 pages; the glossary stands alone on page 4. Acceptable as two sheets front and back.
- **jg06 · stundenentwurf.html** - Teilziel 3 names Modellieren; the KC table lists only "Umgehen mit ..." and "Darstellen". Add Modellieren or drop it from the Teilziel.
- **jg06 · animation.html** - fraction labels are 22 units high; in the two-per-row print they come out small. 26-28 units would read better on paper.
- **jg03 · arbeitsblatt.html** - page 1 carries only the info box (task 1 does not fit below it at 14 pt). A shorter box (two rules + example) would bring task 1 onto page 1.

## Nachgerechnet
Own calculation with exact fractions and integer enumeration, not taken from the `data-check` expressions.

| Task | Own way | Own result | Second way / estimate | Material says | Match |
|---|---|---|---|---|---|
| jg03 1a-c | column addition | 539 · 685 · 634 | 300+200, 400+250, 300+350 ≈ 500, 650, 650 | 539 · 685 · 634 | yes |
| jg03 2 | 467 + 285; digit sums without carry | 752; without carries 642 | 470 + 285 = 755 | 752; "beide Überträge vergessen" | yes |
| jg03 3 | all 720 arrangements of the digits 1-6 enumerated | minimum 381; pairs 135+246, 136+245, 145+236, 146+235 | 100+200+30+40+5+6 | 381, the same four pairs | yes, complete |
| jg06 1a-c | exact fractions | 3/4 · 5/6 · 7/10 | 0,25+0,5; 0,67+0,17; 0,3+0,4 | 3/4 · 5/6 · 7/10 | yes |
| jg06 2a-c | exact fractions, kgV 12, 12, 30 | 7/12 · 1 7/12 · 5/6 | 0,58 · 1,58 · 0,83 | 7/12 · 1 7/12 · 5/6 | yes |
| jg06 3 | 15/20 + 8/20 | 23/20 = 1 3/20 > 1, passt nicht, 3/20 l zu viel | 0,75 + 0,4 = 1,15 | the same | yes |
| jg06 4 | all a, b from 1 to 11 with a/4 + b/6 = 11/12 | (a, b) = (1, 4), (3, 1) | 3a + 2b = 11, a odd, a ≤ 3 | two solutions; one with gekürzten Brüchen only | yes, complete |
| jg06 animation | 1/2 = 3/6, 1/3 = 2/6 | 5/6; rectangles 180 × 120 units, sixths 60 × 60 | 3 + 2 of 6 cells in the last still | 5/6 | yes |
| q1 1a | coefficient-wise antiderivative | x³ − 2x² + 5x | derivative back | the same | yes |
| q1 1b | F(2) − F(0) | 10 | - | 10 | yes |
| q1 1c | product rule; numerical derivative at 5 points | K′ = x · eˣ | - | the same | yes |
| q1 2a | integer search, factorised | 0 and 4 | - | 0, 4 | yes |
| q1 2b | exact integral | 32/3 ≈ 10,67 | ⅔ · 4 · 4 (parabola segment) | 32/3 ≈ 10,67 | yes |
| q1 2c | intersections 0 and 3; integral of 3x − x² | 9/2 | g ≥ x on [0; 3] checked | 4,5 | yes |
| q1 2d | −b³/3 + 2b² = 0 | b = 6 | areas [0; 4] and [4; 6]: +32/3, −32/3 | 6 | yes |
| q1 2e | A(m) = (4 − m)³/6 | m = 2 | scan m in steps of 0,01 | 2 | yes, unique in ]0; 4[ |
| q1 3a | r(2) | 3,6 m³/h | - | 3,6 m³ pro Stunde | yes |
| q1 3b | exact integral 0 to 8 | 25,6 m³ | ⅔ · 8 · 4,8 | 25,6 m³ | yes |
| q1 3c | 25,6 / 8 | 3,2 m³/h | - | 3,2 m³ pro Stunde | yes |
| q1 3d (old) | integral 0 to 4 | 12,8 = half of 25,6 | symmetry about t = 4 | "richtig" | yes (AFB see Should) |
| q1 points | sums | 8 + 19 + 13 = 40; AFB 13 / 19 / 8 = 32,5 / 47,5 / 20 % | - | the same | yes |
| q1 key | percentage × 40 | 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 13,2, 10,8, 8 | - | the same | yes |
| jg06 plan | phase minutes | 4 + 17 + 7 + 15 + 2 = 45 | - | 45 | yes |

## Checked without findings
1 curriculum fit (jg06: Kompetenzerwartungen Ende Jg. 6 and Inhaltsfeld as printed; q1: Q1.1-Q1.3 GK, no LK-only content, parameter task covered by Q1.2) · 2 subject correctness · 4 time (plan 45 min; Klausur 90 min for 12 parts) · 5 marking scheme sums, AFB table, key scale 0-15 with source note and `check:` remark · 6 language level · 8 differentiation (three levels differ in help and complexity; task 4 is a reversed question) · 10 animation content (six print stills: equal parts, pieces keep their size, end state 5/6 = solution; needed: refining and joining parts) · 11 privacy and copyright (invented first names, original tasks) · 12 files and form.

## Not checked
- OAVO Anlage 9a rows other than 5 and 11 Punkte (`check:` in base `bewertung.md`); the Erwartungshorizont says so.
- School decisions: grade key of the Fachkonferenz, calculator model (WTR assumed), Formelsammlung in use, written addition notation of the class.

## Nach Korrektur
Date: 2026-11-11 22:12 · all Must and Should findings applied; Other left as noted.
- Both scripts re-run on the three folders: 0 errors, 0 warnings; 0 failed checks, 0 tasks without check.
- q1 3d re-solved: r(4 + u) = 4,8 − 0,3u² = r(4 − u); with R(t) = −0,1t³ + 1,2t² exactly R(4 + a) − R(4 − a) = 2 · (R(4) − R(4 − a)) for a = 1/2, 3/2, 33/10, 4 (values 191/40, 549/40, 122463/5000, 128/5) - the statement is true; points 2 + 1 + 1 = 4 BE, total stays 40 BE, AFB shares stay 32,5 / 47,5 / 20 %.
- Print: jg03 worksheet 3 pages (was 4), glossary in one piece; Erwartungshorizont sum row once, key in one piece.
- Animation playback, headless Chrome (Playwright): Next 1 → 2, Back 2 → 1, arrow key 1 → 2, Play at 2× reaches step 4 after 1,5 s, Pause holds it, reduced-motion note shown, English toggle hides every English line; no external request, no JS error.
- Verdict after fixes: Einsatzbereit.
