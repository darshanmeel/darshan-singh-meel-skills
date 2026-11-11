# Naturwissenschaft und Technik in Hessen: what exists

Status per line: **read** on the official page named in `sources.md`, or `check:`. Re-read before a report entry or a course description depends on it.

## Findings
| Question | Finding | Status |
|---|---|---|
| Is "Naturwissenschaft und Technik" (NwT) a subject with a Hessen Kerncurriculum at the Gymnasium? | No. The list of Kerncurricula for the Sekundarstufe I names Biologie, Chemie, Physik (each for Hauptschule, Realschule, Gymnasium), Arbeitslehre (Hauptschule, Realschule only) and Informatik (Wahlunterricht, gymnasialer Bildungsgang). No NwT, no "Naturwissenschaften", no "Technik" for the Gymnasium | read |
| Oberstufe? | No. The KCGO list (from 2024/25) has Biologie, Chemie, Physik, Informatik among others; no NwT and no Technik | read |
| Combined science teaching? | The Stundentafel regulation has rows "Lernbereich Naturwissenschaften" for other school forms (read in the amendment of 9 January 2025 for the table with Aufbaustufe / praxisorientierter / mittlerer Bildungsgang). For the Gymnasium, Physik, Chemie and Biologie each have their own KC | read for the row; check: which school forms may teach the Lernbereich, and whether a Gymnasium may combine the subjects in Jg. 5/6 (Verordnung über die Stundentafeln, consolidated text) |
| How does a Gymnasium offer NWT then? | As **Wahlunterricht**. The Stundentafel regulation (§ 2 Abs. 5 as amended 2025): in the gymnasialer Bildungsgang "die dritte Fremdsprache und die weiteren Gegenstandsbereiche" are offered as Wahlunterricht. The ministry's page lists what Wahlunterricht is for: a third foreign language, introduction to the world of work, Informatik, strengthening and supplementing the compulsory lessons, deepening the school's educational mission, social-pedagogical aims, individual inclinations and the school profile | read |
| Hours and years | G9: students "sollen im Laufe der Mittelstufe vier Stunden Wahlunterricht besuchen", intended for Jg. 9 and 10. G8: five hours, placed flexibly in Jg. 5-9. A third foreign language as Wahlunterricht takes 6 hours | read (kultus.hessen.de, Gymnasiale Mittelstufe) |
| Curriculum for the course | The only Wahlunterricht KC is Informatik (4 Jahreswochenstunden from Jg. 7; it cites § 30 VOBGM for Wahlunterricht). An NWT course follows the school's own curriculum; its content relates to the compulsory subjects | read for Informatik; check: § 30 VOBGM wording (Bürgerservice Hessenrecht) |
| Grades | Participation in Wahlunterricht is documented with the Vermerke "teilgenommen", "mit Erfolg teilgenommen", "mit gutem Erfolg teilgenommen" instead of Noten (except foreign languages). VOGSV: Noten are entered for voluntary courses closely tied to a compulsory subject when the performance is befriedigend or better, otherwise "teilgenommen"; for the Gymnasium Sek I this applies "entsprechend" with a proviso for foreign languages | read (ministry page; VOGSV, the paragraph on report entries for Wahlunterricht). check: with the school which of the two a science Wahlunterricht uses |
| Safety | The Aufsichtsverordnung makes Teil I of the KMK RiSU binding; RiSU covers natural-science and technical rooms and activities | read (ministry page; RiSU 2023 for the sections listed in the physics skill) |
| Where does the name NWT/NwT come from? | From other Länder and from school profiles (MINT). Hessen documents use "Wahlunterricht"; schools name their course freely (NaWi, MINT, Forscherkurs, Technik). check: nothing official read on the name | - |

## What follows for material
- Level: Mittelstufe. Default Jg. 9-10 (G9); other years only on the user's word.
- Folder: `unterricht/nawi-technik/jg09/<thema>/`.
- Curriculum reference in the lesson plan (4 rows of the base template):

| Row | Fill with | Example |
|---|---|---|
| Quelle | `Wahlunterricht (schulinternes Curriculum), angebunden an: KC Hessen, Sekundarstufe I - Gymnasium, <Fach>` | Wahlunterricht (schulinternes Curriculum), angebunden an: KC Hessen, Sekundarstufe I - Gymnasium, Physik |
| Kompetenzbereich | Kompetenzbereich - Teilbereich of the carrying subject (identical in Physik, Chemie, Biologie) | Erkenntnisgewinnung - Arbeiten mit Modellen |
| Kompetenz / Bildungsstandard | one standard as printed, `(Ende Jg. 9/10)` | wenden geeignete Modelle zur Erarbeitung und Veranschaulichung von Zusammenhängen an (Ende Jg. 9/10) |
| Inhaltsfeld | Inhaltsfeld - Schwerpunkt (Stufe) of the carrying subject; then the school's module | Technik im Dienst des Menschen - Kraft wandelnde Systeme (Stufe 2); Modul der Schule: Mobilität |

- The four Kompetenzbereiche shared by the three sciences (read in the KC Physik: defined uniformly for Physik, Chemie, Biologie): Erkenntnisgewinnung · Kommunikation · Bewertung · Nutzung fachlicher Konzepte. Teilbereiche and standards: physics skill `sek1.md`.
- Technical competences (plan, construct, test, optimise) have no Hessen Gymnasium standard. Anchor them in Erkenntnisgewinnung ("entwerfen geeignete Modelle ...", "führen ... Untersuchungen durch und protokollieren diese fachgerecht"), Kommunikation ("dokumentieren ihre Arbeit prozess- und ergebnisorientiert, auch als Team") and Bewertung ("bewerten Risiken und Sicherheitsmaßnahmen bei Experimenten, im Alltag und bei modernen Technologien ..."). The Primarstufe standard area "Planen und konstruieren" (Sachunterricht, Jg. 4, shown in the synopsis of the KC Physik) is the earlier step.
- Operators: science list of the base, du-form; construction verbs are in it (`Entwirf`, `Entwickle`, `Plane`, `Prüfe`, `Bewerte`).
- Written checks: `Lernkontrolle` in the base test template; key with the three Vermerke (`technik.md`), printed with "Vorschlag - an den Beschluss der Schule anpassen". A Noten key only when the user confirms that the course is graded.
- Time: the Wahlunterricht is often taught in double lessons - ask; default 90 min for practical work, 45 min otherwise.
