---
name: darshan-singh-meel-frontend-react
description: Build app UIs in React + TypeScript with a component library — scaffold (Vite SPA or Next.js), components, state, forms, data fetching, tables, charts, accessibility, tests, build and deploy — and package a React component as a Streamlit custom component. Use when creating, extending, debugging, or reviewing a React app, or when a Streamlit app needs a custom React widget. Not for visual design decisions (darshan-singh-meel-frontend) or plain Streamlit apps (darshan-singh-meel-streamlit).
---

# Frontend: React
How to build. Look (colour, type, layout, UI words, quality floor) → `darshan-singh-meel-frontend`: read first, don't restate. Code per `darshan-singh-meel-code`.

Read only the refs (`references/<file>`) the task needs.

| Task | Ref | Official docs |
|---|---|---|
| New project, stack choice, scaffold, folders, lint | `stack.md` | react.dev · vite.dev · nextjs.org/docs · ui.shadcn.com |
| Components, state, effects, React 19 APIs | `components.md` | react.dev |
| Forms, validation | `forms.md` | react.dev · react-hook-form.com · zod.dev |
| Data fetching, routing, tables, charts | `data.md` | tanstack.com · ui.shadcn.com |
| Accessibility, tests | `quality.md` | vitest.dev · testing-library.com · playwright.dev · radix-ui.com |
| Env vars, secrets, build, deploy | `deploy.md` | vite.dev |
| React component inside a Streamlit app | `streamlit-component.md` | docs.streamlit.io · docs.snowflake.com |

## Default stack (new project)
| Need | Default | Deviate when |
|---|---|---|
| Build | Vite SPA, `react-ts` template | Server rendering, server-side secrets, auth middleware, or per-request data in the same deployable → Next.js (App Router) |
| Language | TypeScript, `strict` | never |
| Components | shadcn/ui (copied-in, Radix primitives) + Tailwind | Project has a library → use it, never a second |
| Server data | TanStack Query | 1–2 calls, no caching → `fetch` in an event handler or router loader |
| Routing | none for one screen; else TanStack Router or React Router | Next.js → its own router |
| Forms | `<form action>` + `useActionState` + zod | Many fields, field arrays, live validation → React Hook Form + zod |
| Tables | plain `<table>` | Sort, filter, paginate, select → TanStack Table |
| Charts | shadcn chart (Recharts) | Project has a chart library |
| Client state | `useState`, lift up, context | Shared state changed from many distant places → small store (Zustand); ask first |
| Tests | Vitest + Testing Library; Playwright + axe for key flows | — |

## Rules
- Existing project wins: read `package.json` first → its versions, library, router, patterns. Never an API the pinned version lacks.
- New project: latest stable, pinned (commit the lockfile). Confirm versions on the official site or npm, not memory; a major may have changed (version flags in the refs).
- Smallest that works: plain function components. No state, router, form, or table library until the table above says so. Each new dependency → why, one line.
- No secrets in the browser: the bundle is public; keys behind an API → `deploy.md`.
- Data: UI calls an API, never a database. Mock data synthetic, shaped by the schema; no real rows, no PII in fixtures, tests, screenshots. Checking real data → `darshan-singh-meel-notebook`.
- Every data view: loading, empty, error states.
- Accessible by default: semantic HTML first · library primitives for anything interactive · keyboard and focus checked.
- Output: local files in the project. No hosted previews, published pages, shared links unless asked.
- Streamlit: custom React component = last resort; order of options → `streamlit-component.md`.

## Before finishing
- `npm run build` (type check + bundle) + tests for the changed code pass → ask once about the full suite.
- Check the screen at desktop + mobile width, and keyboard only → self-critique in `darshan-singh-meel-frontend`.
- State any version or API taken from memory, not checked.
