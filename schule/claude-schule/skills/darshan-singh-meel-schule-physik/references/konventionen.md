# Physics conventions: units, digits, notation, solutions

Applies to every file. Checked in step 5 and by `scripts/check_einheiten.py`. Constants: values of the SI (2019) and CODATA, written from knowledge, not re-read for this skill - check: the school's Formelsammlung; in tests use its values.

## Quantities and units
| Rule | Right | Wrong |
|---|---|---|
| Quantity = number × unit, always both | `v = 8,0 m/s` | `v = 8,0` |
| Space between number and unit (HTML: `&nbsp;`) | `12 V`, `20 °C`, `25 %` | `12V`, `20°C` |
| No space before ° (angle) | `30°` | `30 °` |
| Symbols of quantities italic (`<i>v</i>`), units and numbers upright | <i>v</i> = 8,0 m/s | *m/s* italic |
| SI unit symbols, case-exact | `s`, `h`, `kg`, `km/h`, `kWh`, `Hz`, `K` | `sec`, `Std.`, `Kg`, `kmh`, `KWh`, `hz`, `°K` |
| Powers with `<sup>`, indices with `<sub>` | m/s<sup>2</sup>, <i>E</i><sub>kin</sub> | `m/s2`, `Ekin` |
| Units in the calculation line, not only at the end | `v = 120 m / 15 s = 8,0 m/s` | `v = 120 / 15 = 8 m/s` |
| Multiplication: `·`; division: fraction or `/` with brackets | `N·m`, `J/(kg·K)` | `Nm` in running text, `J/kg·K` |
| Powers of ten | `3,0·10⁸ m/s` (EN: `3.0·10⁸ m/s`) | `3,0E8`, `3,0*10^8` |
| Decimal sign | German line: comma · English line: point | mixed |
| Thousands | thin space or none (`12 500 m`) | point or comma as separator |
| Table header and axis label | `t in s`, `s in m` | `t [s]`, `t (sec)` |
| Temperature differences | in K (`ΔT = 15 K`) | in °C in formulas with c |

Units allowed besides SI base and derived units: min, h, d, a · km/h · °C · L, mL · t · bar, hPa (weather) · kWh · eV · u · ° (angle).

Conversions used often (exact unless ≈): 1 m/s = 3,6 km/h · 1 h = 3600 s · 1 kWh = 3,6 MJ · 1 bar = 10⁵ Pa · 1 L = 1 dm³ · 0 °C = 273,15 K · 1 eV ≈ 1,602·10⁻¹⁹ J · 1 u ≈ 1,661·10⁻²⁷ kg.

## Significant figures (geltende Ziffern)
- Data in a task are written with the digits that are meant: `0,200 kg` (3), `4,0 cm` (2), `15 s` (2). Avoid data whose digit count is unclear (`100 m`, `2000 N`): write `100,0 m`, `2,0 kN` or `2,0·10³ N`, or in Sek I choose other numbers.
- Multiplication, division, roots, powers: result has as many significant digits as the input with the fewest.
- Addition, subtraction: result has as many decimal places as the input with the fewest.
- Counted numbers and defined factors (2 in ½·m·v², 2π, 3,6, 44 Zähne) are exact: they do not limit the digits.
- Constants: use at least one digit more than the data (`g = 9,81 m/s²` for 2-3 digit data).
- Intermediate results: note with one or two extra digits, calculate on with the unrounded value, round the final result once. A solution states the unrounded value where it matters (`f = 0,7958 Hz ≈ 0,796 Hz`).
- Sek I Stufe 1: "Runde sinnvoll" - not more digits than the data; do not teach the rule, follow it.
- Erwartungshorizont: accept ±1 in the last digit and results from sensible intermediate rounding; say so in "Hinweise zur Korrektur". A missing or wrong unit costs part of the result point, once per task (Folgefehler rule of the base).
- `g`: Oberstufe `9,81 m/s²`. Sek I: `9,81 N/kg`, or `10 N/kg` when the info box says "g ≈ 10 N/kg" - one value per file set.

## Constants
| Quantity | Symbol | Value |
|---|---|---|
| Lichtgeschwindigkeit im Vakuum | c | 299 792 458 m/s (exact) ≈ 3,00·10⁸ m/s |
| Elementarladung | e | 1,602·10⁻¹⁹ C |
| Planck'sches Wirkungsquantum | h | 6,626·10⁻³⁴ J·s = 4,136·10⁻¹⁵ eV·s |
| elektrische Feldkonstante | ε₀ | 8,854·10⁻¹² A·s/(V·m) |
| magnetische Feldkonstante | μ₀ | 1,257·10⁻⁶ V·s/(A·m) |
| Gravitationskonstante | G | 6,674·10⁻¹¹ m³/(kg·s²) |
| Fallbeschleunigung (Normwert) | g | 9,81 m/s² |
| Elektronenmasse | m_e | 9,109·10⁻³¹ kg |
| Protonenmasse | m_p | 1,673·10⁻²⁷ kg |
| Neutronenmasse | m_n | 1,675·10⁻²⁷ kg |
| atomare Masseneinheit | u | 1,661·10⁻²⁷ kg |
| Avogadro-Konstante | N_A | 6,022·10²³ 1/mol |
| Boltzmann-Konstante | k | 1,381·10⁻²³ J/K |
| Rydberg-Konstante | R_∞ | 1,097·10⁷ 1/m |
| Schallgeschwindigkeit in Luft (20 °C) | - | ≈ 343 m/s |
| spezifische Wärmekapazität von Wasser | c_W | 4,18 kJ/(kg·K) |
| Dichte von Wasser (4 °C) | ρ | 1,00 g/cm³ = 1000 kg/m³ |

## Notation
- Diagram names as in the KCGO: time first - `t-s-Diagramm`, `t-v-Diagramm`, `t-y-Diagramm`, `x-y-Diagramm`. English line: `t-s diagram` (distance-time graph in the glossary).
- Amplitude `ŝ` or `s_max`; Periodendauer `T`; Frequenz `f`; Kreisfrequenz `ω`; Wellenlänge `λ`; Ausbreitungsgeschwindigkeit `c`; Federkonstante `D`; Stromstärke `I`; Spannung `U`; Widerstand `R`; Ladung `Q`, `q`; Feldstärke `E`; Flussdichte `B`; Arbeit/Energie `W`, `E`; Leistung `P`; Wirkungsgrad `η`; Impuls `p`.
- Vectors: arrow over the symbol in figures; in running text the magnitude unless direction is the point. Force arrows: start at the point of application, length to scale, scale stated (`1 cm ≙ 1 N`).
- Δ for differences (`Δs`, `Δt`); average vs. instantaneous values named.
- Circuit diagrams: standard symbols (resistor = rectangle, lamp = circle with cross, cell = long and short line, switch, ammeter `A` and voltmeter `V` in circles); lines horizontal/vertical; junction dots; technical current direction + → −, stated once.
- Ray diagrams: rays with arrowheads, optical axis dash-dotted, normal (Lot) dashed, angles measured from the normal.
- Graphs: axes with quantity and unit, zero marked, even scale, measured points as crosses, best-fit line (no dot-to-dot), slope triangle large.

## Solution layout (Lösung, Erwartungshorizont, Beispiel in the Erklärung)
1. `Gegeben / Given`: quantities with symbol, value, unit - converted to SI where needed.
2. `Gesucht / To find`: symbol.
3. `Formel / Formula`: general form, rearranged to the wanted quantity before numbers go in.
4. `Rechnung / Calculation`: numbers with units.
5. `Ergebnis / Result`: rounded, with unit.
6. `Antwortsatz / Answer sentence`: one sentence that answers the question asked.
- Points in tests: Ansatz/Formel · Einsetzen mit Einheiten · Ergebnis mit Einheit und passender Ziffernzahl · Antwort/Deutung.
- Explanations (`Erkläre`, `Begründe`): cause → law or model → consequence; expected key terms listed.
- Drawing tasks: the solution contains the drawing (inline SVG) with scale.

## Größenordnungen (plausibility)
| Thing | Size |
|---|---|
| Gehen · Radfahren · Sprint (Spitze) | 1,4 m/s · 4-7 m/s · 10-12 m/s |
| Auto Stadt · Autobahn · ICE | 50 km/h = 13,9 m/s · 130 km/h = 36 m/s · 300 km/h = 83 m/s |
| Schall in Luft · Licht | 343 m/s · 3,00·10⁸ m/s |
| Masse: Apfel · Schulkind (Jg. 7) · Auto | 0,1-0,2 kg · 40-55 kg · 1,0-1,8 t |
| Gewichtskraft: 100 g · 1 kg | ≈ 1 N · ≈ 10 N |
| Leistung: Mensch dauerhaft · kurz · Wasserkocher · Auto | ≈ 100 W · bis ≈ 1 kW · 2 kW · 50-150 kW |
| Netz · Batterie · USB · Schülernetzgerät | 230 V, 50 Hz · 1,5 V · 5 V · ≤ 12 V typical |
| Stromstärke: LED · Glühlampe 6 V · Haushaltssicherung | ≈ 20 mA · 0,1-0,5 A · 16 A |
| Dichte: Luft · Wasser · Aluminium · Eisen | 1,2 kg/m³ · 1,00 g/cm³ · 2,7 g/cm³ · 7,9 g/cm³ |
| Luftdruck (Normaldruck) | 1013 hPa |
| sichtbares Licht | λ = 380-780 nm; Photon ≈ 1,6-3,3 eV |
| Atom · Atomkern | ≈ 10⁻¹⁰ m · ≈ 10⁻¹⁵ m |
| Schulversuch Federpendel | T = 0,5-2 s; D = 3-30 N/m; m = 50-500 g |
| Plattenkondensator Schule | C in pF-nF; U bis einige kV (nur Demonstration) |

A result outside the known size means: wrong data, wrong unit or wrong formula - fix the task, not the table.

## Typical student ideas → "Typischer Fehler" in solutions
| Topic | Idea or slip | Right |
|---|---|---|
| Geschwindigkeit | km/h and m/s mixed; ×3,6 and ÷3,6 swapped | m/s → km/h: ×3,6 |
| t-s-Diagramm | graph read as a picture of the path ("es geht bergauf") | slope = speed; flat = at rest |
| Kraft | "Ohne Kraft keine Bewegung"; force stored in the body | force changes motion; no net force → uniform motion |
| Wechselwirkung | action and reaction cancel | they act on different bodies |
| Masse / Gewichtskraft | kg used for force | m in kg, F_G in N; F_G = m·g |
| Stromkreis | current is used up in the lamp | current is the same before and after; energy is transferred |
| Spannung / Stromstärke | used as one thing | U: per charge, between two points; I: charge per time, through one point |
| Energie | "Energie wird verbraucht" | converted and devalued (Entwertung), total conserved |
| Wärme / Temperatur | used as one thing | temperature = state; heat = energy transferred |
| Optik | seeing as "Sehstrahlen" from the eye; image "on" the mirror | light enters the eye; mirror image behind the mirror |
| Schwingung | amplitude changes the period (Federpendel, small-angle Fadenpendel) | T independent of amplitude |
| Welle | matter travels with the wave | energy travels; particles oscillate in place |
| Taschenrechner | degrees instead of radians in sin(ω·t) | RAD mode; argument without unit |
| Felder | field lines are paths of charges; field only where lines are drawn | lines show direction of the force; density shows strength |
| Fotoeffekt | brighter light → faster electrons | intensity → number; frequency → energy |
| Radioaktivität | irradiated objects become radioactive; after two half-lives nothing is left | irradiation ≠ contamination; a quarter is left |
