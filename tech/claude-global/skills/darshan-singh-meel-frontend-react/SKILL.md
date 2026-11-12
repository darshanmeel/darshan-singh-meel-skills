---
name: darshan-singh-meel-frontend-react
description: Build app UIs in React + TypeScript with a component library — scaffold (Vite SPA or Next.js), components, state, forms, data fetching, tables, charts, accessibility, tests, build and deploy — and package a React component as a Streamlit custom component. Use when creating, extending, debugging, or reviewing a React app, or when a Streamlit app needs a custom React widget. Not for visual design decisions (darshan-singh-meel-frontend) or plain Streamlit apps (darshan-singh-meel-streamlit).
---

# Frontend: React

How to build it. **What it looks like** (color, type, layout, UI words, quality floor) comes from `darshan-singh-meel-frontend`: read it first, don't restate it. Code discipline: `darshan-singh-meel-code`.

Read only the reference files (`references/<file>`) the task needs.

| Task | File | Official docs |
|---|---|---|
| New project, stack choice, scaffold, folders, lint | `stack.md` | react.dev · vite.dev · nextjs.org/docs · ui.shadcn.com |
| Components, state, effects, React 19 APIs | `components.md` | react.dev |
| Forms and validation | `forms.md` | react.dev · react-hook-form.com · zod.dev |
| Data fetching, routing, tables, charts | `data.md` | tanstack.com · ui.shadcn.com |
| Accessibility and tests | `quality.md` | vitest.dev · testing-library.com · playwright.dev · radix-ui.com |
| Env vars, secrets, build, deploy | `deploy.md` | vite.dev |
| React component inside a Streamlit app | `streamlit-component.md` | docs.streamlit.io · docs.snowflake.com |

## Default stack (new project)
| Need | Default | Deviate when |
|---|---|---|
| Build | Vite SPA, `react-ts` template | Server rendering, server-side secrets, auth middleware, or per-request data in the same deployable → Next.js (App Router) |
| Language | TypeScript, `strict` | never |
| Components | shadcn/ui (copied-in, Radix primitives) + Tailwind | Project already has a library → use it, never add a second |
| Server data | TanStack Query | One or two calls, no caching needed → `fetch` in an event handler or router loader |
| Routing | none for one screen; else TanStack Router or React Router | Next.js → its own router |
| Forms | `<form action>` + `useActionState` + zod | Many fields, field arrays, live validation → React Hook Form + zod |
| Tables | plain `<table>` | Sort, filter, paginate, select → TanStack Table |
| Charts | shadcn chart (Recharts) | Project already has a chart library |
| Client state | `useState`, lift up, context | Shared state changed from many distant places → a small store (Zustand); ask first |
| Tests | Vitest + Testing Library; Playwright + axe for key flows | — |

## Rules
- **Existing project wins.** Read `package.json` first; use its versions, library, router, and patterns. Never use an API the pinned version lacks.
- **New project:** latest stable, pinned (commit the lockfile). Confirm versions on the official site or npm, not from memory; a major may have changed (see the version flags in the reference files).
- **Smallest thing that works.** Plain function components. No state library, router, form library, or table library until the table above says so. Each new dependency: say why in one line.
- **No secrets in the browser.** Anything in the bundle is public. Keys live behind an API; details in `deploy.md`.
- **Data:** the UI calls an API, never a database. Mock data is synthetic and shaped by the schema; no real rows, no PII in fixtures, tests, or screenshots. Checking real data → `darshan-singh-meel-notebook`.
- **Every data view** has loading, empty, and error states.
- **Accessible by default:** semantic HTML first, library primitives for anything interactive, keyboard and focus checked.
- **Output:** local files in the project. No hosted previews, published pages, or shared links unless asked.
- **Streamlit:** a custom React component is the last resort; order of options in `streamlit-component.md`.
- **Streamlit in Snowflake:** a React widget for a SiS app, or an existing React app hosted inside SiS with its API (warehouse-runtime mount, self-contained build, fetch bridge, artifacts, deploy), is not covered here: see `darshan-singh-meel-streamlit-snowflake-react`.

## Before finishing
- `npm run build` (type check + bundle) and the tests for the changed code pass; then ask once about the full suite.
- Check the screen at desktop and mobile width, and with keyboard only; then run the self-critique in `darshan-singh-meel-frontend`.
- State any version or API taken from memory rather than checked.
