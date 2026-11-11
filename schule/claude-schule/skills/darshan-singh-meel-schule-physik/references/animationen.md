# Physics animations

Format, controls, captions and print rules: base `formate.md` (animation.html) and the base template. This file says what to animate in physics and how to build it with the base engine (step list `STEPS`, numbers inside SVG attributes are tweened).

## Animate or draw?
| Animate (motion or change over time is the content) | Draw a figure instead |
|---|---|
| a body moving while its t-s or t-v diagram grows | a formula, a unit table, a labelled apparatus |
| two motions compared (same time, different distance) | a single force diagram |
| a wave travelling; a standing wave; superposition of two waves | the electromagnetic spectrum |
| charge carriers in a circuit; switch closed/open; series vs. parallel | a circuit diagram to copy |
| a field building up; a charged particle on its path in a field | a field-line picture of one state |
| energy conversion along a process (pendulum, roller coaster) with bar chart | an energy flow chart of one device |
| a technical system working (motor, generator, transformer, gear, pump) | its parts list |
| steps of a construction (ray diagram of a lens, force parallelogram) | the finished construction only when the steps were learned before |
| a sequence in time (photoelectric effect with rising frequency, decay with half-lives) | a single energy-level scheme |

The KCGO names an animation for: Gegenfeldmethode (Q3.2), Doppelspaltversuch bei geringer Intensität (Q4.1), Einstein-Synchronisation (Q4.4), bipolarer Transistor (Q4.5), Sonnensystem (Q4.6).

## Physics rules for every animation
- **True to scale.** Positions follow the law: equal time steps, distances computed from the numbers of the worksheet. State the scales in the picture (`1 Kästchen ≙ 1 m`, `1 Schritt ≙ 2 s`).
- **Time is visible.** A clock label or the step caption gives `t` for each state. For a fixed step sequence the transition time is not physical time - the caption says which instant is shown.
- **Same numbers** as worksheet, solution and explanation; the last step shows the result that the solution states, with unit.
- **Models marked as models.** Charge carriers, field lines, rays, wave fronts, energy bars: the first caption says "Modell".
- **Vectors** as arrows with length proportional to the value; when a value halves, the arrow halves.
- **Not by colour alone**: two bodies differ by shape or letter (A ●, B ■); two graphs by line style (solid, dashed) plus a label at the line.
- **Periodic processes** have no endless loop in the engine: show one period in 5 states (0, T/4, T/2, 3T/4, T) or 9 for a wave; the last state equals the first.
- **No false impressions**: electrons drift slowly although the lamp lights at once - say it when carriers are shown; a wave does not carry the medium along - mark one particle that stays at its x.
- 4-8 steps, one idea per step, caption of at most two short sentences, German + English.

## Recipes for the base engine
| Effect | SVG | Step `set` |
|---|---|---|
| Body moves along a track | `<circle id="a" cx="60" cy="80" r="10">` | `'#a': { cx: 360 }` |
| Group moves or turns | `<g id="rad" transform="translate(0 0)">` or `rotate(0 200 150)` | `'#rad': { transform: 'rotate(360 200 150)' }` - same shape of the value, only numbers change |
| Graph line grows | `<line id="gA" x1="80" y1="330" x2="80" y2="330">` | `'#gA': { x2: 240, y2: 250 }` |
| Curve is drawn | `<path id="k" d="..." pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">` | `'#k': { 'stroke-dashoffset': 0 }` |
| Something appears | `opacity="0"` | `'#label': { opacity: 1 }` |
| Wave moves on | `<path id="w" d="M0 100 Q 30 40 60 100 T 120 100 ...">` | new `d` with the same commands and other numbers (phase shifted) |
| Standing wave swings | `<path id="sw" d="M..Q..">` with control points up | `d` with control points mirrored down; nodes keep their numbers |
| Charge carriers move | dashed path: `stroke-dasharray="4 16" stroke-dashoffset="0"` | `'#strom': { 'stroke-dashoffset': -200 }`; open switch: no change of the offset in that step |
| Lamp brighter or darker | `<circle id="lampe" fill="#fff" fill-opacity="0.2">` plus rays with `opacity` | `fill-opacity` and ray `opacity`; add a text label `hell / bright` |
| Arrow changes length | `<line id="F" x2="...">` with marker | `'#F': { x2: 300 }` |
| Bar chart of energies | `<rect id="ekin" y="200" height="0">` | `y` and `height` together so that the bar grows upwards |
| Clock or value text | one `<text>` per state, `opacity="0"` | switch opacities (text content is not tweened) |

- Steps are cumulative: a step lists only what changes. Going back restores the earlier state.
- Ids used in `STEPS` must exist in the SVG; the engine ignores unknown selectors silently - step through every step after writing.
- Captions are JavaScript strings in single quotes: an apostrophe (`Mia's`) ends the string and stops the whole player (no caption, no controls, no print frames), and neither check script reports it. Write `'` or ’. Test: copy the last `<script>` block into a file and run `node --check <file>`; without Node, open the page - an empty caption box means a script error.
- Labels inside the stage stay clear of everything that moves: place them where no body, pointer or crank rests in any step, and keep every text inside the viewBox (width ≈ 0.55 × font size × characters). No script checks this: screenshot every step (the last one too) and look at each label; the print view (`#bilder`) shows all steps on one page.
- Text inside the stage at least 16 units high; symbols and numbers, or `DE / EN` for single words.

## Topic catalogue
| Topic (KC) | Stage shows | Steps |
|---|---|---|
| Weg, Zeit, Geschwindigkeit (Sek I) | two bodies on a scaled track + t-s diagram | start · t₁ · t₂ · speed of A · speed of B · steeper line = faster |
| Schatten, Mondphasen (Sek I) | sun, earth, moon from above + view from earth | 8 positions of the moon |
| Brechung, Linse (Sek I) | ray construction | object · parallel ray · centre ray · focal ray · image |
| Stromkreis (Sek I) | circuit with moving carriers, switch, lamp | open · closed · second lamp in series (slower, darker) · parallel (two paths) |
| Hebel, Flaschenzug (Sek I) | load rises, hand pulls further | start · half way · end · force × distance equal |
| Teilchenmodell (Sek I) | particles in solid, liquid, gas | heating in steps; spacing and motion grow |
| Gleichmäßig beschleunigte Bewegung, freier Fall (E.1) | stroboscopic positions + t-s and t-v diagrams | equal time steps, distances 1 : 4 : 9 : 16 |
| Waagerechter Wurf (E.3) | superposition: uniform in x, accelerated in y | 5 time steps with both components |
| Kreisbewegung (E.3) | velocity and centripetal force arrows | quarter turns |
| Plattenkondensator, Teilchenbahn (Q1.1) | field lines, particle path | entry · deflection · exit · comparison with the throw (LK) |
| Lorentzkraft, Fadenstrahlrohr (Q1.2) | circular path, F ⟂ v | entry · quarter turns · larger B → smaller radius |
| Federpendel (Q2.1) | oscillator + t-s diagram + energy bars | 0 · T/4 · T/2 · 3T/4 · T |
| Induktion (Q2.2) | magnet moves into coil, meter deflects | in · rest · out · faster |
| Welle, stehende Welle, Interferenz (Q2.3, Q3.1) | chain of particles; two sources | phase steps; path difference 0, λ/2, λ |
| Fotoeffekt, Gegenfeldmethode (Q3.2) | photons, electrons, counter-voltage | frequency below limit · above · counter-voltage rises · current zero |
| Energieniveaus, Emission/Absorption (Q3.3) | level scheme with electron and photon | absorption · excited · emission · line in the spectrum |
| Doppelspalt mit Einzelobjekten (Q4.1) | screen filling with single hits | 10 · 100 · 1000 hits → pattern |
| Zerfall (Sek I, Q4.3) | 64 nuclei, half decay per half-life | 64 · 32 · 16 · 8 · 4 |
