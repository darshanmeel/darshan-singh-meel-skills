# Chemie: notation, calculations, experiments, typical errors, animations

Notation follows IUPAC and the KCGO wording; expected observations and typical errors are standard school chemistry (not from an official page) - checked by solving, not by citation. Safety: `sicherheit.md`.

## Three levels of description (KC Sek I; KCGO S 6, S 15)
| Level | Speaks about | Words |
|---|---|---|
| Stoffebene | what is seen and measured | Stoff, Farbe, Belag, Gasentwicklung, Temperatur, Masse, Lösung |
| Teilchenebene | model of what happens | Atom, Ion, Molekül, Elektron, Proton, Bindung, Stoß |
| Symbolebene | formulas and equations | Cu, Cu<sup>2+</sup>, CuSO<sub>4</sub>, →, ⇌ |

- `Beobachtung` uses the Stoffebene only; `Deutung` links it to the Teilchenebene; the equation is the Symbolebene.
- Wrong mixes: "Kupferatome sind rotbraun", "Wassermoleküle sieden", "das Zink löst sich auf" (as interpretation), "Natriumchlorid-Moleküle".
- Salts consist of ions: `Kupfer(II)-Ionen in der Lösung`, not "Kupfersulfat reagiert" on the particle level; spectator ions are named once and left out of the ionic equation.

## Notation
| Item | Rule |
|---|---|
| Formulas | real sub- and superscripts in HTML: `H<sub>2</sub>O`, `SO<sub>4</sub><sup>2−</sup>`, `Fe<sup>3+</sup>`; charge as number then sign (`2+`, not `+2`); minus sign `−` |
| Oxidation numbers | Roman numerals above the symbol or in brackets in names: `Kupfer(II)-sulfat`, `Eisen(III)-oxid`; in text `Oxidationszahl +II` |
| Arrows | `→` reaction · `⇌` equilibrium · `↔` mesomeric structures only |
| State symbols | (s), (l), (g), (aq), from Jg. 9 on in every equation |
| Names | KCGO wording: Oxonium-Ion (H<sub>3</sub>O<sup>+</sup>), Hydroxid-Ion, Alkanole, Alkanale, Alkanone, Alkansäuren/Carbonsäuren, Benzen (Benzol), Ethansäure (Essigsäure), Stoffmengenkonzentration |
| Quantities | symbols italic, units upright: <i>m</i> in g, <i>n</i> in mol, <i>M</i> in g/mol, <i>V</i> in L or mL, <i>c</i> in mol/L, <i>V</i><sub>m</sub> in L/mol, <i>N</i><sub>A</sub>, Δ<sub>r</sub><i>H</i> in kJ/mol, <i>E</i>° and <i>U</i> in V |
| Decimal sign | comma in the German line, point in the English line (base `bilingual.md`) |
| Structural formulas | inline SVG or text with bond lines; all free electron pairs in Lewis formulas; skeleton formulas only from Q1 on |
| Half equations | `Oxidation: Zn → Zn<sup>2+</sup> + 2 e<sup>−</sup>` · `Reduktion: Cu<sup>2+</sup> + 2 e<sup>−</sup> → Cu`; electrons balanced before adding |

## Balance check (every equation, writer and reviewer)
1. Count each element left and right.
2. Add the charges left and right.
3. Redox: electrons given = electrons taken; oxidation numbers change by that amount.
4. Smallest whole-number coefficients; states present; formula of every substance right (ion charges from the group or the Roman numeral).

## Values and constants
- Molar masses: from the periodic table the class uses; this skill rounds atomic masses to one decimal (H 1,0 · C 12,0 · N 14,0 · O 16,0 · Na 23,0 · Mg 24,3 · Al 27,0 · S 32,1 · Cl 35,5 · K 39,1 · Ca 40,1 · Fe 55,8 · Cu 63,5 · Zn 65,4 · Ag 107,9) and prints the values used on the sheet.
- <i>N</i><sub>A</sub> = 6,022 · 10<sup>23</sup> mol<sup>−1</sup>. Molar volume of a gas: 22,4 L/mol (0 °C, 1013 hPa) or about 24 L/mol (room temperature) - print which one the task uses.
- Standard potentials, pK<sub>S</sub> values, enthalpies differ slightly by table: print the values in the task and name "Tafelwerk der Klasse" or "Werte für diese Aufgabe"; never rely on a remembered value in a graded task. Usual school values: <i>E</i>°(Zn<sup>2+</sup>/Zn) = −0,76 V · <i>E</i>°(Fe<sup>2+</sup>/Fe) = −0,44 V (some tables −0,41 V) · <i>E</i>°(Cu<sup>2+</sup>/Cu) = +0,34 V (some tables +0,35 V) · <i>E</i>°(Ag<sup>+</sup>/Ag) = +0,80 V.

## Calculation form
`Gegeben` → `Gesucht` → `Formel` → `Einsetzen mit Einheiten` → `Ergebnis` (unit, digits of the weakest input) → `Antwortsatz`.

| Type | Core relations |
|---|---|
| Stoffmenge | <i>n</i> = <i>m</i> / <i>M</i> · <i>n</i> = <i>V</i> / <i>V</i><sub>m</sub> · <i>N</i> = <i>n</i> · <i>N</i><sub>A</sub> |
| Konzentration | <i>c</i> = <i>n</i> / <i>V</i> (V in L) · dilution: <i>c</i><sub>1</sub><i>V</i><sub>1</sub> = <i>c</i><sub>2</sub><i>V</i><sub>2</sub> |
| Stöchiometrie | mole ratio from the balanced equation; never a mass ratio straight from coefficients |
| pH (strong acid/base) | pH = −lg <i>c</i>(H<sub>3</sub>O<sup>+</sup>) · pOH = −lg <i>c</i>(OH<sup>−</sup>) · pH + pOH = 14 (25 °C) |
| Titration | <i>n</i>(acid) · protons = <i>n</i>(base) · hydroxide ions at the equivalence point; mL → L |
| Zellspannung | <i>U</i> = <i>E</i>°(Kathode / Akzeptorhalbzelle) − <i>E</i>°(Anode / Donatorhalbzelle) |
| Enthalpie | Δ<sub>r</sub><i>H</i>° = Σ Δ<sub>f</sub><i>H</i>°(Produkte) − Σ Δ<sub>f</sub><i>H</i>°(Edukte), each times its coefficient |
| MWG | <i>K</i><sub>c</sub> = product of product concentrations / product of reactant concentrations, each to the power of its coefficient; pure solids and the solvent left out |

- Keep full precision to the end; round once. A second way or an estimate confirms each result (mass balance, charge balance, pH within plausible bounds).
- Data are chosen so that results are sensible: burette volumes 5-25 mL, concentrations 0,01-1 mol/L, masses weighable on a school balance (0,01 g).

## Protocol form (Versuchsprotokoll)
`Fragestellung` → `Hypothese` → `Geräte und Chemikalien` → `Sicherheit` (block from `sicherheit.md`) → `Aufbau` (sketch) → `Durchführung` (numbered, amounts) → `Beobachtung` (Stoffebene; table) → `Deutung` (Teilchenebene; equation) → `Fehlerbetrachtung` → `Entsorgung`.
English labels: question · hypothesis · apparatus and chemicals · safety · set-up · procedure · observation · interpretation · sources of error · disposal.

## Standard experiments and expected observations
Classification and student permission: look up per substance and concentration (`sicherheit.md`). SV = usual as student experiment, LD = teacher demonstration - both subject to the GBU.

| Topic (level) | Experiment | Expected observation | Notes |
|---|---|---|---|
| Trennverfahren (1. Lernjahr) | Salz-Sand-Gemisch trennen: lösen, filtrieren, eindampfen | Sand bleibt im Filter; klares Filtrat; nach dem Eindampfen weißer Feststoff | SV; Schutzbrille beim Eindampfen (Spritzer) |
| Chemische Reaktion (1. Lernjahr) | Eisenwolle verbrennen, vorher und nachher wiegen | Aufglühen; grauschwarzer, spröder Feststoff; Masse nimmt zu | SV or LD; feuerfeste Unterlage |
| Chemische Reaktion | Kupferblech im Schwefeldampf | Aufglühen; blauschwarzer, spröder Stoff | LD, Abzug (Schwefeldioxid möglich) |
| Affinitätsreihe (Sek I) | Kupfer(II)-oxid + Eisenpulver erhitzen | Aufglühen; rotbraunes Kupfer sichtbar | LD |
| Säuren, Laugen (Jg. 9-10, E.2) | Indikatorfarben; Neutralisation Salzsäure + Natronlauge (verdünnt) | Universalindikator rot → grün → blau; Erwärmung nur mit Thermometer und c ≥ 1 mol/L messbar | SV with dilute solutions |
| Titration (E.2, Q3.2) | Salzsäure unbekannter Konzentration mit Natronlauge 0,1 mol/L, Indikator | Farbumschlag durch einen Tropfen; Volumen ablesen | SV; three runs, mean |
| Redoxreihe (E.1) | Metallstreifen (Zn, Fe, Cu) in Lösungen von Zinksulfat, Eisen(II)-sulfat, Kupfer(II)-sulfat | Zn in CuSO<sub>4</sub>: rotbrauner Belag, blaue Lösung wird heller · Fe in CuSO<sub>4</sub>: rotbrauner Belag, Lösung wird heller bis grünlich · Zn in FeSO<sub>4</sub>: dunkler Belag (langsam) · alle anderen Paare: keine Veränderung | SV in Tüpfelplatte or Reagenzgläser; heavy-metal waste |
| Galvanisches Element (E.1, Q3.3) | Daniell-Element: Zn/ZnSO<sub>4</sub> // CuSO<sub>4</sub>/Cu | Spannung etwa 1,1 V; Zink ist der Minuspol | SV; a measured value below the calculated one is normal |
| Elektrolyse (E.1, Q3.3) | Kupfer(II)-chlorid-Lösung, Graphitelektroden | Kathode: rotbrauner Belag; Anode: Gasbläschen, stechender Geruch (Chlor) | chlorine forms: Abzug or micro scale, short duration - as the GBU says |
| Alkane, Alkene (E.3, Q1.1) | Nachweis der Doppelbindung mit Bromwasser | Entfärbung beim Alken, keine schnelle Entfärbung beim Alkan | LD, Abzug; check: DEGINTU for a substitute |
| Verbrennungsprodukte (Q1.1) | Flamme: wasserfreies Kupfer(II)-sulfat, Kalkwasser | weißes Kupfer(II)-sulfat wird blau (Wasser); Kalkwasser trübt sich (Kohlenstoffdioxid) | SV |
| Alkanole (Q1.2) | oxidierte, heiße Kupferspirale in Ethanol oder Propan-1-ol | schwarze Spirale wird wieder kupferrot; stechender Geruch | flammable liquid: no open flame near it; allowed for students from Jg. 5 (only H224 liquids are barred in Jg. 5-9, RiSU Tabelle 3b); check: DEGINTU |
| Alkanale (Q1.2, Q2.1) | Fehling-Probe mit Glucose im Wasserbad | tiefblaue Lösung → ziegelroter Niederschlag | Fehling II is strongly alkaline: as the GBU says |
| Ester (Q1.3, Q3.1) | Ethansäure + Ethanol, Schwefelsäure als Katalysator | fruchtiger Geruch (Klebstoff); zwei Phasen nach Eingießen in Wasser | konzentrierte Schwefelsäure: LD or as the GBU says |
| Proteine, Stärke (Q2.1) | Biuret-Reaktion; Iod-Stärke-Reaktion | violette Färbung; blauschwarze Färbung | SV |
| Gleichgewicht (Q3.1) | Eisen(III)-thiocyanat: Zugabe von Eisen(III)- oder Thiocyanat-Ionen, Verdünnen | Rotfärbung tiefer bei Zugabe eines Edukts, heller beim Verdünnen | SV in small amounts |
| Reaktionsgeschwindigkeit (Q3.5, Q4.1) | Magnesium + Salzsäure verschiedener Konzentration | Gasentwicklung schneller bei höherer Konzentration, höherer Temperatur, feinerer Zerteilung | SV with dilute acid; hydrogen: no flames |
| Kalorimetrie (Q4.1) | Neutralisationswärme im Kunststoffbecher mit Deckel | Temperaturanstieg um wenige Kelvin | SV |

The student sheet never states the expected observation; Lösung and lesson plan do.

## Typical student errors (for "Typischer Fehler" and distractors)
| Field | Error | Right |
|---|---|---|
| Stoff/Teilchen | "die Atome schmelzen / werden beim Erwärmen größer" | particles keep size and nature; distance and movement change |
| Reaktion | "bei der Verbrennung verschwindet Masse" | mass is conserved; gases count |
| Formeln | index and coefficient mixed up; indices changed to balance | only coefficients are changed |
| Ionen | "NaCl-Molekül"; charge forgotten (Cu<sup>+</sup> for Kupfer(II)) | ion lattice, Verhältnisformel; charge from the Roman numeral |
| Redox | "Oxidation = Reaktion mit Sauerstoff" kept in the Oberstufe; "das Oxidationsmittel wird oxidiert" | oxidation = electron release; the oxidising agent takes electrons and is reduced |
| Redoxreihe | "Kupfer ist stärker, weil es sich abscheidet" | the metal that goes into solution is the stronger reducing agent (donor) |
| Galvanisches Element | Anode = Pluspol as in electrolysis | galvanic cell: Anode = Minuspol; electrolysis: Anode = Pluspol; oxidation at the anode in both |
| Säure/Base | strong and concentrated mixed up; "Säure = ätzend" | strength = degree of protolysis; concentration = amount per volume |
| pH | pH of 10<sup>−8</sup> mol/L HCl "= 8" | below about 10<sup>−6</sup> mol/L the autoprotolysis of water counts; avoid such data |
| Stöchiometrie | mass ratio taken from coefficients | convert to moles first |
| Gleichgewicht | "die Reaktion ist zu Ende"; "gleich viel Edukt und Produkt"; "der Katalysator verschiebt das Gleichgewicht" | both reactions run at equal rates; concentrations constant, not equal; a catalyst only speeds up the setting |
| Organik | longest chain counted wrong; "Doppelbindung ist stärker, also reaktionsträger" | name from the longest chain; the π bond is the reactive site |
| Energie | "exotherm = braucht keine Aktivierungsenergie" | every reaction needs activation; exothermic refers to the balance |

## Animations: when and what
Only where steps or motion carry the idea (base rule). One process, 4-8 steps; the first caption names the model, one caption names a limit (from Jg. 9).

| Process | Steps to show | Level |
|---|---|---|
| Aggregatzustände im Teilchenmodell | solid: lattice, vibrating → liquid: particles slide → gas: far apart; particle size and number unchanged | 1. Lernjahr |
| Lösen, Diffusion | particles of two substances mix by their own motion | 1. Lernjahr |
| Ionenbildung, Ionengitter | electron moves from Na to Cl; ions with charges; lattice grows | Jg. 9-10 |
| Metallabscheidung (Redox) | Zn atom gives 2 e<sup>−</sup>, Zn<sup>2+</sup> goes into solution; Cu<sup>2+</sup> takes 2 e<sup>−</sup>, Cu atom on the surface | E.1 |
| Galvanisches Element | oxidation at Zn, electrons through the wire, reduction at Cu, ions through the diaphragm | E.1, Q3.3 |
| Protolyse | proton moves from HCl to H<sub>2</sub>O: H<sub>3</sub>O<sup>+</sup> and Cl<sup>−</sup> | E.2 |
| Titration | drops added, particle counts in the flask, indicator change with label | E.2, Q3.2 |
| Radikalische Substitution | Start, Kettenfortpflanzung (two steps), Abbruch; single electrons as dots | E.3, Q1.1 |
| Elektrophile Addition | π-Komplex, Bromonium-Ion, Rückseitenangriff | Q1.1 |
| Dynamisches Gleichgewicht | forward and backward reaction with particle counts and a c/t diagram drawn in parallel until the counts stay constant | Q3.1 |
| Stoßtheorie | collisions with and without enough energy and fitting orientation | Q3.5, Q4.1 |

- In every step the particle count is right: atoms conserved, charges balanced (the reviewer counts them).
- Nothing by colour alone: element symbol and charge inside or beside each particle.
- Not an animation: periodic table trends, structural formulas, apparatus set-ups - labelled figures.
