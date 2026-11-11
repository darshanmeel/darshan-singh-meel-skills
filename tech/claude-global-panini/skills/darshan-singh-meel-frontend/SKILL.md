---
name: darshan-singh-meel-frontend
description: Design rules for app UIs — web apps, internal tools, data apps, dashboards, forms, landing pages — clear, distinctive, accessible, minimal: layout, type, color, states. Use when building a new UI or reshaping/restyling one — it sets how the UI looks and behaves; the building is done with darshan-singh-meel-frontend-react or darshan-singh-meel-streamlit (load both). Skip only for non-visual React/Streamlit work (bug fix, deploy, tests, caching). Not for documentation pages (use darshan-singh-meel-docs).
---

# Frontend
Lead product designer: every choice from the subject and the user's job, not a template. Code per `darshan-singh-meel-code`.
**Build with:** React → `darshan-singh-meel-frontend-react` · Streamlit → `darshan-singh-meel-streamlit` (+ `-streamlit-snowflake` if hosted in Snowflake). This skill = design rules only.

## Start
- Name product · user · the screen's one main job. Unclear → propose, confirm (one question).
- Project design system/tokens exist → follow; never a second style.
- Content from the brief; else realistic synthetic data shaped by the schema (never lorem ipsum, foo/bar).
- First thing seen = most important for the job (key number, main action, live data).

## Plan (short → check vs brief → build)
Show the plan in a few lines, then build without waiting. Existing design system → skip Colour and Type; plan Layout only.
- Colour: 4–6 named hex with roles (ground, surface, ink, accent, status).
- Type: 1–2 families with roles, a scale; body lines < ~80 chars.
- Layout: one-line concept + small ASCII wireframe; alignment rules.
- One memorable element; the rest quiet. Any part looks like a default → change it, say why.

## Avoid generic looks (unless asked)
Same rounded card + soft shadow everywhere · decorative gradients · cream + serif + clay, or black + one neon, as unconsidered defaults · ALL-CAPS labels over every heading · `A · B · C` meta strings · `→` on every link/button · one coloured/italic word in headlines · 01/02/03 on non-sequences · fade/slide-in on every section, hover animation on every card.

## Data, dashboards, forms
- Borders, labels, numbering, dividers carry meaning, never decoration.
- Dashboards: top 3 user questions first · one main metric per card · units and time range visible · consistent number format · status colours only for status.
- Charts: simplest that answers; direct labels over legends; no 3D, no many-slice pies.
- Tables: numbers right-aligned, sticky header if long, sensible default sort, empty/loading states.
- Forms: one column, labels above, inline validation with the fix, clearly named primary action.

## Words
User's words, not system's ("Notifications", not "Webhook config") · buttons say what happens ("Save changes"), same word through the flow · errors: what happened + how to fix, no apology, no vagueness · empty states say what to do next · sentence case, plain verbs, no filler, each text one job.

## Quality floor (always, silently)
Responsive to mobile, no horizontal scroll · keyboard + visible focus, semantic HTML, input labels, alt text on meaningful images · WCAG AA contrast, never colour alone · reduced motion respected; motion only to show what changed after a user action, or one deliberate moment · loading, empty, error states for every data view.

## Code
- Simplest stack that fits: plain HTML/CSS/JS for small tools; project's framework (React, Streamlit, …) if already used.
- CSS tokens as custom properties; flat specificity; no unused styles. Few components and files; no UI library for one widget.

## Finish
Check at desktop + mobile width (screenshot if available) · remove any decoration that carries no meaning · fix misalignment, overflow, anything that reads as default.
