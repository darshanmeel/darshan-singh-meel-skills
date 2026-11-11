# Chemie: safety in experiments (RiSU, GBU, GHS)

Facts: RiSU (Richtlinie zur Sicherheit im Unterricht, KMK, Stand 21.09.2023), sections in brackets; status in `sources.md`. GHS classifications of single substances are **not** stored here: they depend on substance, concentration and supplier - look up DEGINTU or the safety data sheet every time.

## Who decides what
- Hessen: the Aufsichtsverordnung makes RiSU Teil I binding (kultus.hessen.de, Arbeitsschutz). check: text of the Aufsichtsverordnung.
- Gefährdungsbeurteilung (GBU): made and documented by the school before the activity; the teacher is responsible in the own lessons and must be fachkundig (RiSU I-0.1, I-0.2, I-3.2). It includes the Substitutionsprüfung, documented (I-3.2.4, TRGS 600).
- This skill writes a **draft safety block** and, on request, a draft GBU table. Print under both: `Entwurf - ersetzt nicht die Gefährdungsbeurteilung der Lehrkraft.` / `Draft - does not replace the teacher's risk assessment.`
- Order of measures: S-T-O-P = Substitution, technische, organisatorische, personenbezogene Maßnahmen (I-0.3).
- Unterweisung: general instruction each half-year, noted in Klassenbuch/Kursheft; before each experiment specific instructions on substances, handling and disposal (I-3.16). A Versuchsblatt with safety block counts as the written part.
- Sources for classifications: DEGINTU (`https://degintu.dguv.de`, free for schools, with ready GBU drafts per experiment) and DGUV Information 213-098 (Stoffliste). Column "Tätigkeitsbeschränkung" there: `ESP` = Ersatzstoffprüfung, replace where possible; `-S` = no student experiment (I-3.2.4).

## Student restrictions (RiSU I-3.6, Tabelle 3b)
Students may work with hazardous substances only if the learning goal needs it, a fachkundige person supervises, they have been instructed, and their development and skill allow it.

| Hazard (category, H statement) | Jg. 5-9 | Jg. 10-13 |
|---|---|---|
| Explosive (instabil explosiv, Expl. 1.1-1.4) | no | no |
| Entzündbare Flüssigkeit Kat. 1 (H224, extrem entzündbar) | no | yes |
| Akute Toxizität Kat. 1 or 2 (H300, H310, H330) | no | no |
| Keimzellmutagen 1A/1B (H340), karzinogen 1A/1B (H350), reproduktionstoxisch 1A/1B (H360) - also when listed so in TRGS 905 | no | no |
| Ozonschicht schädigend (H420) | no | no |
| Druckgasflaschen or -packungen with Wasserstoff | no | not excluded by I-3.6.2 - check the GBU |
| Natrium, Kalium, Chlorate (except activities of low hazard, e.g. striking a match) | no | no |
| Quecksilberthermometer and -manometer | no | no |

- Exceptions for CMR 1A/1B: activities where the substance is not bioavailable (no exposure through skin, air or swallowing), e.g. Bleiacetat- or Cobaltchlorid-Papier, Chromattitration, lead plates in a Bleiakkumulator (I-3.6.1).
- Acutely toxic Kat. 1/2: allowed when dilution lowers the classification, also for by-products formed in such dilution (I-3.6.1; sample calculation in RiSU III-2.12).
- Essigsäureanhydrid: Jg. 10-13 only without exposure, e.g. in the Abzug (Tabelle 3b, note 4).
- Up to Jg. 4: activities of low hazard only, no flammable liquids (I-3.6.2) - not relevant for these skills, named for completeness.
- Everything else is allowed from Jg. 5 under the four conditions above - which does not make it sensible: substitution and small amounts first.
- Pregnant or breastfeeding teachers and students: further restrictions (I-3.7). Material never asks or names anyone; the plan says `Mutterschutz in der GBU geprüft`. Students are told about the restrictions in the general instruction.
- Teachers: bans and restrictions in I-3.5 (e.g. certain CMR substances are banned in schools altogether). check: RiSU I-3.5 and DGUV 213-098 before planning a demonstration with a CMR substance.

## Standard measures (RiSU I-2, I-3.4, I-3.11, I-3.13, Teil II)
- Schutzbrille whenever substances are handled or heated; gloves only where the GBU demands them (wrong gloves are worse than none).
- Smallest amounts (mL and g range); closed vessels; Abzug for gases, vapours and dusts that harm, and for work with Chlor and Brom.
- No eating or drinking; no mouth pipetting; taste tests forbidden; smell only by fanning.
- Long hair tied back; no loose scarves near the burner; flammable liquids never near open flames; heat test tubes at the upper liquid level, opening away from people, with boiling stone or shaking.
- Students do not work alone; the teacher stays in the room.
- Disposal is settled before the experiment: collect by waste type in labelled containers (I-3.13; school's Entsorgungskonzept, RiSU III-2.6). Typical containers: Schwermetallsalz-Lösungen · organische Lösemittel halogenfrei / halogenhaltig · Säuren und Laugen (neutralise, then as the concept says) · Feststoffabfälle. Which residue goes where: check: the school's concept.

## GHS pictograms (CLP regulation; codes for the safety block)
| Code | Symbol | Meaning | Deutsch |
|---|---|---|---|
| GHS01 | exploding bomb | explosive | explosiv |
| GHS02 | flame | flammable | entzündbar |
| GHS03 | flame over circle | oxidising | brandfördernd (oxidierend) |
| GHS04 | gas cylinder | gas under pressure | Gase unter Druck |
| GHS05 | corrosion | corrosive to skin, eyes, metals | ätzend / korrosiv |
| GHS06 | skull and crossbones | acutely toxic | akut giftig |
| GHS07 | exclamation mark | irritant, harmful, sensitising (skin) | reizend, gesundheitsschädlich |
| GHS08 | health hazard | CMR, organ damage, respiratory sensitiser, aspiration hazard | Gesundheitsgefahr |
| GHS09 | environment | hazardous to the aquatic environment | umweltgefährlich |

- Signal words: `Gefahr` (danger) for the severe categories, `Achtung` (warning) for the lower ones.
- H-Sätze = hazard statements, P-Sätze = precautionary statements; quote the numbers from the source, not from memory.
- Pictograms in material: write code + German name (`GHS05 ätzend`). A drawn symbol only as a simple inline SVG diamond with the code inside; never an external image.

## Safety block on every experiment sheet
Student sheet: the lines marked S. Lesson plan (or Lösung, when no plan is written): all lines. Example: `examples/redoxreihe-e/`.

| Line | Content |
|---|---|
| Versuchsart (S) | Schülerversuch (EA/PA/GA) or Lehrerdemonstration; Jahrgang |
| Stoffe (S) | name, formula, concentration, amount |
| Einstufung (S) | GHS code(s) + signal word, with source (`DEGINTU, abgerufen <Datum>` or `Sicherheitsdatenblatt`) · or `kein Gefahrstoff` · or `Einstufung prüfen` |
| Gefahren (S) | what can happen in this experiment (splash, burn, gas, fire) - not a copy of all H statements |
| Schutz (S) | Schutzbrille; further measures (Abzug, Handschuhe, Wasserbad statt Flamme) |
| Schülerversuch erlaubt? | result of the table above for the Jahrgang |
| Substitution | what was replaced, or why nothing less hazardous fits |
| Entsorgung (S) | container per residue; name of the container: school concept |
| Hinweis (S) | the draft sentence |

- A classification that was not looked up in this session is written `Einstufung prüfen (DEGINTU / Sicherheitsdatenblatt)` / `check classification (DEGINTU / safety data sheet)`, never as a pictogram from memory. The hand-over reply lists every such line.
- Concentration matters: a dilute solution often has a lower classification than the pure substance; the block names the concentration actually used.
- Reaction products count: gases and solids formed (chlorine, hydrogen, nitrogen oxides, sulfur dioxide) get their own line.

## Draft GBU table (only when asked)
`Tätigkeit` · `Stoff, Menge, Konzentration` · `Einstufung (Quelle)` · `Gefährdung (Einatmen, Haut, Brand/Explosion, sonstige)` · `Substitution geprüft` · `technische / organisatorische / persönliche Maßnahmen` · `Schülerversuch ab Jg.` · `Entsorgung` · `Datum, Unterschrift (blank)`. Same draft sentence below.

## Experiments to keep off student sheets
| Activity | Why | Instead |
|---|---|---|
| Work with Brom, Chlor (generation, bromination of alkanes/alkenes) | toxic gases and vapours; Abzug or closed apparatus (RiSU II) | Lehrerdemonstration in the Abzug, video, or given observations; check: DEGINTU for a bromine-free variant |
| Alkali metals in water, chlorates | Tabelle 3b note 2 | Lehrerdemonstration behind a Schutzscheibe |
| Concentrated acids and alkalis, dilution of concentrated sulfuric acid | corrosive, heat | teacher prepares dilute solutions |
| Hydrogen from a gas cylinder in Jg. 5-9 | I-3.6.2 | small amounts generated in the test tube, Knallgasprobe as demonstration |
| Nitrating mixture, benzene, chromium(VI) compounds | CMR / bans: check: RiSU I-3.5 | models, data, video |
| Thermite, flash powders, anything "spectacular" from the internet | uncontrolled energy release | not in this skill's material |
