# Stack, scaffold, structure

## Vite SPA or Next.js
| Choose | When |
|---|---|
| **Vite SPA** (default) | Internal tool or data app · separate API · static hosting · no SEO or server rendering needed |
| **Next.js** (App Router) | Server rendering · secrets or a backend-for-frontend on the same deployable (route handlers, server actions) · auth middleware · per-request server data |

- React's docs recommend a framework for most apps and Vite for client-only SPAs: react.dev/learn/build-a-react-app-from-scratch.
- A Vite SPA has no Server Components and no Server Actions. Don't write `"use server"` there.
- Next.js static export (`output: 'export'`) gives an SPA but drops the server features; if that is all you need, use Vite.

## Scaffold (versions checked 2026-11; re-check before pinning)
| Step | Command / setting | Docs |
|---|---|---|
| Node | 22.12+ (covers Vite and Vitest) | vite.dev/guide |
| App | `npm create vite@latest my-app -- --template react-ts` | vite.dev/guide |
| Tailwind v4 | `npm install tailwindcss @tailwindcss/vite` · add `tailwindcss()` to Vite plugins · CSS: `@import "tailwindcss";` · no config file | tailwindcss.com/docs/installation/using-vite |
| shadcn/ui | `npx shadcn@latest init -t vite` · then `npx shadcn@latest add button` per component | ui.shadcn.com/docs/installation/vite |
| Next.js instead | `npx create-next-app@latest my-app --yes` (TS, Tailwind, ESLint, App Router) | nextjs.org/docs/app/getting-started/installation |

- Checked versions: React 19.3 · Vite 8 · TypeScript 7.0 · Tailwind 4.3 · Zod 4 · Vitest 5.
- shadcn/ui is copied-in source, not a dependency: the components are yours to edit. Add only the ones used.
- `@/*` path alias: set in `tsconfig.json`, `tsconfig.app.json`, and `vite.config.ts` (the shadcn init does it).
- React Compiler: optional. Add only if the project wants automatic memoization; setup differs by `@vitejs/plugin-react` version: react.dev/learn/react-compiler/installation.

## Component library
- **Default: shadcn/ui** — accessible Radix primitives, Tailwind styling, tokens as CSS variables that map straight onto the design plan from `darshan-singh-meel-frontend`.
- **Another library** (Mantine, MUI, Chakra, React Aria…) when the project or organisation already uses it, or it ships a complex widget you need (date range picker, tree, rich data grid). One library per app.
- Put the design tokens (color, type, radius, spacing) in the theme once; never hard-code hex values in components.
- Restyle through the theme and variants, not one-off overrides.

## Folders (flat until it hurts)
```
src/
  main.tsx          providers, router
  App.tsx
  components/ui/    library components (shadcn)
  components/       shared app components
  features/<name>/  screen + its components, hooks, api calls, tests
  lib/              api client, formatters, schemas
```
- Small app: `App.tsx` + `components/` is enough. Add `features/` at about three screens.
- Tests sit next to the file: `Thing.tsx`, `Thing.test.tsx`.
- No barrel `index.ts` files, no `utils/` dumping ground, no `types/` folder (types live with their code).

## Lint and format
- Keep what the template ships (ESLint flat config) or use Biome; one tool set, not both.
- `eslint-plugin-react-hooks` on; `@tanstack/eslint-plugin-query` when using TanStack Query.
- `package.json` scripts: `dev`, `build` (`tsc -b && vite build`), `preview`, `test`, `lint`.
