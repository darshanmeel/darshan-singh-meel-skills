# Env vars, secrets, build, deploy

Docs: vite.dev/guide/env-and-mode · vite.dev/guide/static-deploy

## Env vars and secrets
- Only `VITE_`-prefixed vars reach client code, and they are **baked into the bundle at build time**. Everything in the bundle is public.
- So `VITE_*` holds configuration only: API base URL, feature flags, public client IDs. Never API keys, passwords, tokens, or connection strings.
- A call that needs a secret goes through a backend (API, serverless function, Next.js route handler). The secret lives in the host's secret store, never in the repo.
- Files: `.env` (committed defaults, no secrets) · `.env.local` and `.env.*.local` (git-ignored) · `.env.[mode]`. Never open or print env files; record only that they exist.
- Commit `.env.example` with names and `<redacted>` or dummy values.
- Type the vars in `vite-env.d.ts` (`ImportMetaEnv`); values are always strings. Read them in one place (`lib/config.ts`).
- Next.js: same rule; the public prefix is `NEXT_PUBLIC_`, unprefixed vars stay on the server.

## Build
- `npm run build` → `tsc -b && vite build` → static files in `dist/`. Type errors fail the build.
- `vite preview` checks the built bundle locally; it is not a production server.
- Hosted under a sub-path → set `base` in `vite.config.ts`.
- Bundle too big: lazy-load heavy routes and chart/table code first; measure before adding manual chunking.
- Source maps: off in production, or uploaded privately to the error tracker.

## Deploy (static SPA)
- Any static host works: object storage + CDN, a static-web-app service, or the API's own static folder.
- **SPA fallback:** the host must serve `index.html` for unknown paths, or deep links 404. Each host configures this differently.
- Cache: hashed assets long-lived and immutable; `index.html` no-cache.
- API on another origin → CORS limited to the app's origin, or serve both behind one domain with a proxy (simpler; cookies stay first-party).
- Security headers at the host: Content-Security-Policy (no inline scripts), `X-Content-Type-Options`, `Referrer-Policy`, HTTPS only.
- Per-environment config: one build per environment via `--mode`, or one build that loads a small runtime `config.json`. Pick one; say which.
- CI: `npm ci` → lint → test → build → deploy the `dist/` output. Lockfile committed; Node version pinned (`engines` or `.nvmrc`).
- Deploying is the user's call: write the config and commands; don't publish or upload unless asked.

## Dependencies
- Before adding one: is there a platform or library built-in? (`Intl`, `fetch`, `URLSearchParams`, `<dialog>`, CSS.)
- Committed lockfile; `npm audit` on new additions; no abandoned packages.
