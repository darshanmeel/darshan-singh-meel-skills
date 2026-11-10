---
name: darshan-singh-meel-frontend
description: Design and build app UIs — web apps, internal tools, data apps, dashboards, forms, landing pages — that are clear, distinctive, accessible, and minimal. Use when building a new UI or reshaping an existing one. Not for documentation pages (use darshan-singh-meel-docs).
---

# Frontend
Lead product designer: every choice from the subject and the user's job, not a template. Code per `darshan-singh-meel-code`. CLAUDE.md applies.

## Start
- Name product · user · the screen's one main job. Unclear → propose, confirm (one question).
- Project design system/tokens exist → follow; never a second style.
- Real content; else realistic data (never lorem ipsum, foo/bar).
- First thing seen = most important for the job (key number, main action, live data).

## Plan (short, then build)
- Colour: 4–6 named hex with roles (ground, surface, ink, accent, status).
- Type: 1–2 families, a scale; body lines < ~80 chars.
- Layout: one-line concept + small ASCII wireframe; alignment rules.
- One memorable element; the rest quiet. Any part looks like a default → change it, say why.

## Avoid generic looks (unless asked)
Same rounded card + soft shadow everywhere · decorative gradients · cream + serif + clay, or black + one neon, as unconsidered defaults · ALL-CAPS labels over every heading · `A · B · C` meta strings · `→` on every button · one coloured word in headlines · 01/02/03 on non-sequences · fade-in on every section, hover on every card.

## Data, dashboards, forms
- Borders, labels, numbers, dividers carry meaning, never decoration.
- Dashboards: top 3 user questions first · one main metric per card · units and time range visible · consistent number format · status colours only for status.
- Charts: simplest that answers; direct labels over legends; no 3D, no many-slice pies.
- Tables: numbers right-aligned, sticky header, sensible default sort, empty/loading states.
- Forms: one column, labels above, inline validation with the fix, clearly named primary action.

## Words
User's words, not system's ("Notifications", not "Webhook config") · buttons say what happens ("Save changes"), same word through the flow · errors: what happened + how to fix, no apology · empty states say what to do next · sentence case, plain verbs, no filler.

## Quality floor (always, silently)
Responsive to mobile, no horizontal scroll · keyboard + visible focus, semantic HTML, input labels, alt text · WCAG AA contrast, never colour alone · reduced motion respected; motion only to show change · loading, empty, error states for every data view.

## Code
- Simplest stack that fits: plain HTML/CSS/JS for small tools; project's framework (React, Streamlit, …) if already used.
- CSS tokens as custom properties; flat specificity; no unused styles. Few components and files; no UI library for one widget.
- Local files only; never publish.

## Finish
Screenshot desktop + mobile · remove one decoration · fix misalignment, overflow, anything that reads as default.
