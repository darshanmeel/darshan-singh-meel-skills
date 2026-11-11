# Erdkunde: material, maps, climate diagrams, animations

Subject practice for writing and checking tasks. School conventions, not KC wording, unless a KC code is given.

## Material types: what the sheet must show, how students work on it
Every material: number (`M1`), title, source line with year, legend/units. Steps are the order of sub-tasks (AFB I → III).

| Material | Must show | Steps |
|---|---|---|
| Thematische Karte / Kartenskizze | title, legend, scale bar or "nicht maßstabsgetreu", north, year of the data, source | Thema und Raum nennen → Legende lesen → Verbreitung/Lage beschreiben (Regel, Ausnahmen) → erklären → Aussagekraft beurteilen |
| Klimadiagramm | station, height, annual mean, annual sum, period, source | Lage → Temperatur (Jahresmittel, wärmster/kältester Monat, Amplitude) → Niederschlag (Summe, Verteilung, humide/aride Monate) → Klimazone zuordnen → erklären |
| Statistik / Tabelle | title, unit in the header, year(s), area, source | Thema, Einheit, Zeitraum → Höchst-/Tiefstwerte, Entwicklung (mit Zahlen) → Zusammenhänge → erklären → Grenzen der Daten |
| Diagramm (Säulen, Linien, Kreis) | axes with quantity and unit, zero line or marked break, legend | as Statistik; name the diagram type; check the axis for cut-offs (Manipulation, Sek I Methodenkompetenz) |
| Bevölkerungspyramide | area, year, unit (Tsd. or %), men left / women right, age groups of 5 years | Form beschreiben → Geburtenentwicklung, Lebenserwartung, Einschnitte ablesen → erklären → Folgen beurteilen |
| Profil / Blockbild | horizontal and vertical scale, Überhöhung named, direction (W-E) | Verlauf beschreiben → Höhenstufen/Schichten zuordnen → erklären |
| Wirkungsgefüge / Fließdiagramm | boxes with nouns, arrows with direction, `+`/`−` or verbs on arrows | Elemente nennen → Wirkungen lesen → Rückkopplungen erklären → Eingriffe beurteilen |
| Text (Zeitungsartikel, Stellungnahme) | author role, medium, date; written for the task or with source | Position wiedergeben → Interessen herausarbeiten → mit Daten vergleichen → beurteilen |
| Karikatur | own drawing or exact description in words; year and context | beschreiben → Elemente deuten → Aussage formulieren → Stellung nehmen |
| Foto | only as a described scene or own SVG sketch (no stock or press photos) | beschreiben (Vorder-, Mittel-, Hintergrund) → verorten → erklären |

- Raumanalyse (Oberstufe, MA5, BB1): Lage → naturräumliche Ausstattung → humangeographische Strukturen → Verflechtungen und Prozesse → Problem/Leitfrage → Beurteilung → Bewertung with stated norms.
- Data in a test: at most 2 pages of material in Sek I, 3-4 materials; Oberstufe 4-6 materials. Each material is used by at least one task; no decoration.

## Maps as own SVG
- Allowed: schematic sketch (generalised outlines drawn by hand as paths), Lageskizze with graticule lines, profile, block diagram, model. State "Kartenskizze, stark vereinfacht / map sketch, strongly simplified".
- Not allowed: scans, screenshots, traced or redrawn textbook/atlas maps with their design, copied thematic layers.
- Exact outlines only from data that may be reused: check: licence of the data set before use (e.g. Natural Earth - naturalearthdata.com terms; Bundesamt für Kartographie und Geodäsie open data - gdz.bkg.bund.de). Name data set and licence in the source line.
- Form: `viewBox`, `role="img"`, `aria-label` DE / EN; labels at least 16 units; areas distinguished by pattern or label, not colour alone; legend inside the SVG; scale bar computed from the drawing (state km per unit) or the words "nicht maßstabsgetreu"; north arrow or two labelled graticule lines.
- Orientation tasks need real coordinates: take latitude/longitude from an official station or gazetteer list and give them to 1 decimal degree at most in Sek I.
- Disputed borders dashed and labelled; names as used by Auswärtiges Amt / UN.

## Climate diagrams
- Always `scripts/klimadiagramm.py`: `python klimadiagramm.py "Frankfurt am Main" 100 2.3,3.1,... 44,39,... --out m1.svg`. `--sued` for southern-hemisphere stations (months run July to June).
- Form (Walter/Lieth school form): temperature line, precipitation columns, **10 °C = 20 mm**; above 100 mm the precipitation axis is compressed 1:10, the columns are filled dark and the °C labels end at 50; head line: station, height, annual mean, annual sum.
- School rule printed in the info box: a month is **arid** when the column ends below the line (N < 2 · T), **humid** when it rises above it. It is a rule of thumb for comparing, not a measurement of evaporation - say so from Jg. 9.
- The script prints: Jahresmittel, Jahressumme (whole mm, as in the diagram head), wärmster/kältester Monat, Jahresamplitude, aride Monate (by name). Copy these into the solution; do not recompute by eye.
- Jahresamplitude is a difference: unit K; accept °C in Sek I and say so in the solution.
- Annual mean computed from 12 rounded monthly means may differ by 0.1 from the official annual value: print which one is used.
- Negative monthly means: the script extends the axis below 0; frost months are read from the line, not from the columns.
- Data: official multi-year means with station, height and reference period (currently 1991-2020). Sources below. Invented stations are allowed for practice and are labelled "erfundene Station / invented station".

## Data sources (official; name source, period and retrieval year under the material)
| Data | Source |
|---|---|
| Climate normals Germany (temperature, precipitation, sunshine per station) | Deutscher Wetterdienst, Climate Data Center, open data: vieljährige Mittelwerte (read for the example) |
| Climate normals worldwide | check: WMO Climatological Normals (wmo.int) or the national weather service |
| Population, area, economy Germany and Hessen | check: Statistisches Bundesamt (destatis.de), Hessisches Statistisches Landesamt (statistik.hessen.de) |
| Europe | check: Eurostat (ec.europa.eu/eurostat) |
| World: population, HDI, development | check: UN DESA World Population Prospects (population.un.org), UNDP Human Development Reports (hdr.undp.org), World Bank Open Data (data.worldbank.org) |
| Earthquakes, volcanoes | check: GFZ Potsdam (gfz.de), USGS (usgs.gov) |
| Climate change | check: IPCC reports (ipcc.ch), Umweltbundesamt (umweltbundesamt.de), DWD Klimaatlas |

- Each provider has terms of use: read them before reuse; a source line is always required. No values from memory, blogs or travel sites.
- Rounding is stated ("auf ganze Millimeter gerundet"). Sums and means in the solution are computed from the printed values.

## Calculations that must be recomputed in every solution
| Quantity | Rule |
|---|---|
| Maßstab | 1 : 50 000 → 1 cm on the map = 500 m in reality; distance = map length × scale number |
| Jahresamplitude | warmest minus coldest monthly mean (K) |
| Jahresmitteltemperatur · Jahresniederschlag | mean of 12 values · sum of 12 values |
| Bevölkerungsdichte | Einwohner ÷ Fläche (Einw./km²) |
| Natürliche Wachstumsrate | Geburtenrate − Sterberate (‰ per year); growth incl. migration = + Wanderungssaldo |
| Wanderungssaldo | Zuzüge − Fortzüge |
| Anteil / Veränderung | part ÷ whole × 100 % · (new − old) ÷ old × 100 %; percentage points ≠ per cent |
| Zeitzonen | 360° ÷ 24 h = 15° per hour; east is ahead |
| Überhöhung (Profil) | horizontal scale number ÷ vertical scale number |

## Typical student errors (use for "Typischer Fehler" lines and distractors)
- Temperature read from the precipitation axis; columns and line mixed up.
- "Humid" = "much rain", "arid" = "hot"; warm = dry.
- Description already explains; explanation only repeats the description.
- Weather and climate confused; one hot summer taken as climate change, one cold week as its refutation.
- Seasons explained by distance to the sun instead of the tilt of the axis.
- Plates "swim on liquid magma"; the mantle is solid and flows very slowly (plastic).
- Scale: "large scale" taken as large area (1 : 10 000 is a larger scale than 1 : 1 000 000).
- Absolute numbers compared where shares or densities are needed; per cent and percentage points confused.
- Push and pull factors listed without reference to the case; migration reduced to one cause.
- Judgement without criteria; Sachurteil and Werturteil mixed.
- Whole continents treated as one country.

## Animations: when and what
Use the base template; one idea per step; every number equals the worksheet.

| Process | Steps (4-8) | Model limit to name |
|---|---|---|
| Plattentektonik (divergent, konvergent, Transform) | plates at rest → mantle flow → plates move (arrows, cm per year) → ridge/trench forms → quakes and volcanoes marked | time compressed by millions of years; mantle drawn as flowing, it is solid |
| Jahreszeiten | Earth at four positions, axis tilt constant → sun angle at one latitude → day length | sizes and distances not to scale |
| Passatkreislauf / Monsun | heating at the ITC → rising, rain → flow aloft → sinking → trade winds; monsoon: shift of the ITC, wind reversal | mean state; real weather varies |
| Wasserkreislauf, Föhn, Land-See-Wind | one arrow per step | simplified to two dimensions |
| Migration (push and pull) | region of origin → factors appear → routes drawn in order → destination → effects on both | one case, one year; flows simplified |
| Stadtentwicklung (Sub-, Reurbanisierung, Gentrifizierung phases) | one phase per step | model, no real city |
| Demographischer Übergang | birth and death rate lines drawn phase by phase, gap shaded | model derived from European history |
| Klimadiagramm lesen | line → columns → comparison → arid/humid marked | - |

Not an animation: a single map, a table, a finished diagram - use a figure in `erklaerung.html`.

## Bili Erdkunde (teaching language English)
- Default of these skills stays: German first, English line under it. For a class taught in English the user chooses "zusätzlich ganz englische Fassung" (`.en.html`); terms from `begriffe.md`.
- Operators: official DE ↔ EN pairs of the Hessen list for bilingual subjects (base `operatoren.md`).
- Rules for bilingual classes (language of tests, share of German): check: Hessen regulations on bilingual teaching (kultus.hessen.de) and the school's concept.
