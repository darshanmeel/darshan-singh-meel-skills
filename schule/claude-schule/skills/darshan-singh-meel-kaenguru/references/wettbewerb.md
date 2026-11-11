# The competition: rules and scoring

Source and status of every line: `sources.md`. Read on the organiser's pages on 2026-11-11 for the 2027 round. Rules and dates change: re-read `mathe-kaenguru.de` → Wettbewerb before telling a class a rule. `check:` = not found on the pages read.

## Facts
| Topic | Rule |
|---|---|
| Organiser (Germany) | Mathematikwettbewerb Känguru e.V., seated at Humboldt-Universität zu Berlin; prepared and scored centrally, held at the schools |
| International | association Kangourou sans Frontières; over 100 countries; problems essentially the same everywhere, a country may change up to five per age group |
| Who | Klassen 3-13, all school types, voluntary; registration only through a teacher of the school; at least 15 participants per school; start fee 2,50 Euro (2027) |
| Date | normally the 3rd Thursday in March; 2027 by exception 8 April 2027 (registration 1 Dec 2026 - 31 Jan 2027) |
| Papers | five: Klassenstufen 3/4, 5/6, 7/8, 9/10, 11-13; a student sits the paper of the own school year |
| Form | multiple choice, written at school under supervision |
| Time | 75 minutes, every level |
| Number of problems | 24 in Klassenstufen 3-6; 30 in Klassenstufen 7-13 |
| Points per problem | first third 3, second third 4, last third 5 (8 or 10 problems each) |
| Start points | 24 (Klassen 3-6) or 30 (Klassen 7-13) |
| Correct / no answer / wrong | + points of the problem / 0 / minus a quarter of its points: −0,75, −1, −1,25 |
| Range | 0 (all wrong) to 120 (Klassen 3-6) or 150 (Klassen 7-13) |
| Aids allowed | pen, scratch paper, drawing tools, Formelsammlung, coloured pens, scissors and similar |
| Aids not allowed | electronic aids: calculator, CAS, smartphone, internet |
| Answer sheet | paper sheet (letters entered online by the school afterwards) or digital sheet; the problem sheet stays with the student |
| Results | certificate with the score for everyone; no comparison between schools or states |
| Prizes | about the best 5 % in Germany get a 1st, 2nd or 3rd prize, numbers about 1 : 2 : 3, set per Klassenstufe; a small prize for every participant |
| Prize thresholds | set per Klasse and year, published on the Wettbewerb page under "Preise"; 2026, Klasse 3: 91,75 / 82,25 / 75,00 (1st / 2nd / 3rd). Never quote a past threshold as a target for the coming round |
| Grades | FAQ: "Der Wettbewerb sollte grundsätzlich nicht benotet werden." Only especially good results may earn an extra mark where the school does that |
| Weitester Känguru-Sprung | per school: the largest number of consecutive correct answers wins a T-shirt; ties: position of the run, then score; runs of Klassen 3-6 are multiplied by 1,25 (= 30/24) when compared with Klassen 7-13 |
| Support needs | LRS: no special rule, the school's usual support is fine, problems may be read out neutrally; blind students: the teacher may grant extra time; Braille, large-print and sign-language versions exist for some levels |
| Past papers | all years as PDF under "Aufgaben" (German; English from 2016), solution letters as PDF; worked solutions in the organiser's brochures |

- check: how several marks for one problem are scored (not on the pages read). Training material here scores them as wrong and says "hier".
- Copyright: the site's texts and pictures are protected; use is limited to the offered functions and personal use (Impressum). Consequence for this skill: link to the past papers, never reproduce them.

## Numbers that follow from the rules
| Quantity | Klassen 3-6 | Klassen 7-13 |
|---|---|---|
| Time per problem on average | 75 : 24 ≈ 3,1 min | 75 : 30 = 2,5 min |
| Points to win (without start points) | 8 · (3 + 4 + 5) = 96 | 10 · (3 + 4 + 5) = 120 |
| All wrong | 24 − 8 · (0,75 + 1 + 1,25) = 0 | 30 − 10 · 3 = 0 |
| Start points | = number of problems | = number of problems |

- Blind guess among five options: expected gain = 1/5 · p − 4/5 · p/4 = 0. One option ruled out for certain: 1/4 · p − 3/4 · p/4 = p/16 > 0. Two ruled out: p/6. Rule for students: guess only after ruling out at least one option.
- Score of an answer string: `scripts/kaenguru_check.py score`.

## Scaling a mock test
- Start points = number of problems (keeps "all wrong = 0"); equal thirds of 3, 4 and 5 points; time at competition pace, rounded up to 5 min. Table of sizes: `formate.md`.
- Print the rules the students will meet on the day: one letter per problem, quarter deduction, empty = 0, no calculator.
