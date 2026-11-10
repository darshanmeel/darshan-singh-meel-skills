---
name: darshan-singh-meel-frontend
description: Design and build app UIs — web apps, internal tools, data apps, dashboards, forms, landing pages — that are clear, distinctive, accessible, and minimal. Use when building a new UI or reshaping an existing one. Not for documentation pages (use darshan-singh-meel-docs).
---

# Frontend Design

Design like a lead product designer: every visual choice comes from the subject and the user's job, not from a template. Build it with the same minimal-code rules as `darshan-singh-meel-code`.

## Start from the subject
- Name the product, the user, and the one main job of the screen before designing. If unclear, propose them and confirm (one question).
- Follow the project's existing design system, components, and tokens if there is one. Don't invent a second style.
- Use real content from the brief or source data; realistic placeholder data otherwise (never lorem ipsum, never foo/bar).
- The first thing users see should be the most important thing for their job: the key number, the main action, the live data.

## Plan before building (short)
Write a compact plan, check it against the brief, then build:
- **Color:** 4–6 named hex values with roles (ground, surface, ink, accent, status).
- **Type:** 1–2 families with clear roles and a type scale; body line length < ~80 characters.
- **Layout:** one-sentence concept + a small ASCII wireframe; alignment rules.
- **One memorable thing:** the single element that gives the UI its character. Keep everything else quiet.
- Review: if any part looks like the default you'd produce for any similar app, change it and say why.

## Avoid generic "generated" looks (unless the brief asks for them)
- Identical rounded cards with the same soft shadow everywhere; gradient washes as decoration.
- Warm cream ground + serif + clay accent; or near-black ground + one neon accent — as unconsidered defaults.
- ALL-CAPS tracked labels above every heading; `A · B · C` meta strings; `→` on every link/button.
- Highlighting one word in a headline with a different color/italic.
- Numbered markers (01 / 02 / 03) on content that isn't a sequence.
- Fade-and-slide entrances on every section; hover animation on every card.

## Structure, data, and dashboards
- Borders, labels, numbering, and dividers must carry meaning, not decorate.
- Dashboards: answer the user's top 3 questions first; one primary metric per card; units and time range always visible; consistent number formatting; status colors used only for status.
- Charts: the simplest chart that answers the question; label directly instead of legends where possible; no 3D, no pie charts with many slices.
- Tables: right-align numbers, sticky header for long tables, sensible default sort, empty and loading states.
- Forms: one column, labels above fields, inline validation with the fix, primary action clearly named.

## Words in the UI
- Name things by what users understand, not how the system is built ("Notifications", not "Webhook config").
- Buttons say exactly what happens: "Save changes", not "Submit". Same word through the flow ("Publish" → "Published").
- Errors say what happened and how to fix it; no apologies, no vagueness.
- Empty states tell users what to do next.
- Sentence case, plain verbs, no filler. Each piece of text does one job.

## Quality floor (always, without announcing it)
- Responsive down to mobile width; no horizontal scroll.
- Keyboard accessible with visible focus; semantic HTML; labels on inputs; alt text on meaningful images.
- Color contrast meets WCAG AA; never color alone to carry meaning.
- `prefers-reduced-motion` respected. Motion only to show what changed after a user action, or one deliberate moment.
- Loading, empty, and error states for every data view.

## Code
- Simplest stack that fits the project: plain HTML/CSS/JS for small tools; the project's framework (React, etc.) or data-app framework (e.g. Streamlit) when already in use.
- CSS: design tokens as custom properties; low, flat selector specificity so rules don't fight; no unused styles.
- Few components, few files; no UI library added for one widget.
- Output to local files in the project folder only — never publish an artifact or hosted page.

## Finish with a self-critique
- Look at the result (screenshot if available) at desktop and mobile width.
- Remove one unnecessary decoration. Fix anything that misaligns, overflows, or reads as a default.
