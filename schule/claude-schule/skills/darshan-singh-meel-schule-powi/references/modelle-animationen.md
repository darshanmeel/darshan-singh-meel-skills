# Models, diagrams, animations

Each model: what it shows, assumptions, what must be right in the drawing, a limit to name in a task, and - where motion helps - the animation step plan (base engine: `STEPS` with `de`, `en`, `set`; 4-8 steps; see base `references/formate.md`).

## Conventions
- Price-quantity diagram: **Preis p on the y-axis, Menge x (or q) on the x-axis**; axes labelled with unit; Nachfrage falling, Angebot rising; curves labelled `N` and `A` (English line: `D` and `S` only in a full-English file; in bilingual files label `N / D`, `A / S`).
- Curves distinguished by line style and label, not by colour alone (N solid, A dashed).
- Numbers in the animation equal the worksheet table and the solution.
- Arrowheads: draw each as its own small `<path>`; `marker-end` heads did not show in the print key frames (tested in Chrome). Direction of an arrow is content - check it in the print view.
- Labels never cross a curve, an arrow or another label in any step; a label sits next to the element it names; step through all steps before finishing.
- Print: one key frame per row. In-picture text `font-size` at least viewBox width ÷ 51 (720 → 15, 880 → 18), or it prints below 10 pt on A4.
- Flows in cycle diagrams: Güterstrom and Geldstrom run in opposite directions; draw them with different line styles and arrowheads; every arrow labelled.

## Marktmodell (Angebot und Nachfrage) - Sek I Jg. 8-10, E2.1, WiWi E1.7
| Item | Content |
|---|---|
| Shows | how price and quantity settle where planned supply equals planned demand |
| Assumptions | many buyers and sellers, one homogeneous good, full information, no one sets the price alone (vollständige Konkurrenz); ceteris paribus |
| Must be right | Gleichgewicht = intersection; below it Nachfrageüberhang (demand > supply, price rises), above it Angebotsüberhang (price falls); a price change moves along the curves; income, tastes, prices of other goods, number of buyers shift N; costs, technology, number of sellers shift A |
| Check | every table row satisfies the curves; with linear curves compute the intersection: `N(p) = A(p)` |
| Limit | real markets: market power, incomplete information, external effects, habits; Höchst- and Mindestpreise prevent the adjustment |
| Animation | 1 axes and table · 2 draw N · 3 draw A · 4 price below equilibrium: gap = Nachfrageüberhang, arrow up · 5 price above: gap = Angebotsüberhang, arrow down · 6 Gleichgewichtspreis and -menge. Extension: 7 shift of N to the right → new equilibrium |

Linear model data that give whole numbers: `N = a − b·p`, `A = c·p − d` with `p* = (a + d) / (b + c)` whole; e.g. `N = 140 − 20p`, `A = 20p − 20` → `p* = 4`, `x* = 60`.

## Einfacher und erweiterter Wirtschaftskreislauf - Sek I Jg. 8-10, E2.1
| Item | Content |
|---|---|
| Shows | exchange between sectors as closed flows |
| Einfach | Haushalte ↔ Unternehmen: Arbeit (and other Produktionsfaktoren) → Unternehmen; Einkommen (Lohn, Gewinn, Zins, Pacht) → Haushalte; Konsumausgaben → Unternehmen; Konsumgüter → Haushalte |
| Erweitert | + Staat (Steuern, Abgaben ← both; Transferzahlungen, Gehälter → Haushalte; Subventionen, Staatsaufträge → Unternehmen) · + Banken / Vermögensbildung (Sparen ← Haushalte; Kredite für Investitionen → Unternehmen) · + Ausland (Exporte, Importe and their payments) |
| Must be right | each Geldstrom has an opposite Güter- or Leistungsstrom, or is a transfer; in a closed model inflows = outflows for each sector |
| Check | in a numbered example: sum of flows into each sector = sum of flows out |
| Limit | no stocks (wealth, debt), no prices, no environment (resources in, waste out), sectors treated as uniform |
| Animation | 1 two sectors · 2 Arbeit flows → Unternehmen · 3 Einkommen back (Geld) · 4 Konsumausgaben · 5 Güter · 6 Staat added with Steuern and Transfers · 7 Banken: Sparen and Kredite · 8 Ausland |

## Konjunkturzyklus - Sek I Jg. 9/10, Q2.1
| Item | Content |
|---|---|
| Shows | fluctuation of capacity use around the growth trend |
| Phases | Aufschwung (Expansion) · Hochkonjunktur (Boom) · Abschwung (Rezession) · Tiefstand (Depression); terms vary - use the course's set |
| Must be right | y-axis: reales BIP or its growth rate - say which; trend line; idealised wave, real cycles are irregular |
| Indicators | Frühindikatoren (Auftragseingänge, Geschäftsklima) · Präsenzindikatoren (BIP, Produktion) · Spätindikatoren (Arbeitslosigkeit, Preise) |
| Limit | regular wave is a model; shocks and structural change are not in it |
| Animation | 1 trend · 2 Aufschwung · 3 Boom · 4 Abschwung · 5 Tiefstand · 6 indicators appear in their order |

## Multiplikator (Q2.1, GK)
- Rounds of spending: initial state spending ΔG, each round the share c (marginale Konsumquote) is spent again: `ΔY = ΔG · 1 / (1 − c)`. Example `ΔG = 100`, `c = 0,8` → rounds 100, 80, 64, 51,2 ... → total 500.
- Limits (controversy): crowding-out, imports, taxes, time lags, expectations, debt. Present Keynesian and critical view side by side.
- Animation: bars per round adding up to the total; 5-6 steps.

## Magisches Viereck (Sek I Jg. 10, Q2)
- Goals of § 1 Stabilitäts- und Wachstumsgesetz (1967): Stabilität des Preisniveaus, hoher Beschäftigungsstand, außenwirtschaftliches Gleichgewicht, stetiges und angemessenes Wirtschaftswachstum. check: wording at gesetze-im-internet.de (StabG § 1).
- "Magisch": goals conflict (Zielkonflikte) or support each other (Zielharmonie). Extensions (Sechseck: Umwelt, gerechte Verteilung) are political proposals - label them so.
- Static figure, no animation.

## Gesetzgebung des Bundes (Sek I Jg. 8-10, Q1.1)
- Steps: Gesetzesinitiative (Bundesregierung, Bundesrat, aus der Mitte des Bundestages - Art. 76 GG) → three readings and committee work in the Bundestag → Bundesrat (Einspruchs- or Zustimmungsgesetz; Vermittlungsausschuss - Art. 77 GG) → Gegenzeichnung, Ausfertigung by the Bundespräsident, Verkündung im Bundesgesetzblatt (Art. 82 GG).
- check: articles at gesetze-im-internet.de before printing; state the version date.
- Animation: a bill moving through the stations; branch at the Bundesrat; 6-8 steps. Roles, no names of office holders.

## Gewaltenteilung, Verfassungsorgane (Sek I, Q1)
- Static organigram in `erklaerung.html`: who elects whom, who controls whom; arrows labelled with verb (`wählt`, `kontrolliert`, `ernennt`). Animation only for "election → government formation" as a sequence.

## Sitzverteilung (Q1.2)
- Divisor method step by step can be animated with invented parties A-D and invented votes. The method and thresholds in force: check: Bundeswahlgesetz at gesetze-im-internet.de and bundeswahlleiterin.de.

## Further models (figure; animation only if a shift is shown)
| Model | Level | Must be right |
|---|---|---|
| Bedürfnispyramide (Maslow) | Jg. 5-7 | a psychological model, empirically contested; order is not strict |
| Ökonomisches Prinzip (Minimal-, Maximalprinzip) | Jg. 7-9 | never "minimal input and maximal output" at once |
| Externe Effekte, Internalisierung | E2.2, E2.3 | social costs = private + external; tax or certificate shifts the private cost curve |
| Güterarten (Rivalität × Ausschließbarkeit) | E2.2 | 2×2 table: private Güter, Allmendegüter, Klubgüter (Kollektivgüter), öffentliche Güter |
| Phillips-Kurve, Laffer-Kurve | Q2 LK | present as contested hypotheses with their critics |
| Komparative Kostenvorteile (Ricardo) | Q3.2 LK, WiWi Q3.1 | opportunity costs decide, not absolute costs; number example with two countries, two goods; check both countries gain |
| Politikzyklus (Problem → Agenda → Formulierung → Entscheidung → Implementierung → Evaluation) | Q1 | an analysis tool, not a description of every real process |
| Mehrebenensystem EU | Q1.3, Q4 | Europäischer Rat ≠ Rat der EU ≠ Europarat; ordinary legislative procedure: Kommission proposes, Parlament and Rat decide - check: european-union.europa.eu |
