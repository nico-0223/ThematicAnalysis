# Conversation Thematic Analysis — Web Frontend

A clean, production-quality React + TypeScript frontend for the existing
`conversation-thematic-analysis` Python + SQL backend. The frontend never
implements analysis logic — it only presents and controls the workflow
through HTTP API calls.

## Stack

React 18, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query,
React Hook Form, Zod, Recharts (where helpful), Vitest.

## Local development

```bash
cp .env.example .env       # adjust VITE_API_BASE_URL if needed
npm install
npm run dev                # http://localhost:5173
```

## Production build

```bash
npm run build
npm run preview            # serves dist/ locally on :4173
```

## Tests

```bash
npm run test
```

## Environment variables

| Name | Default | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000/api` | Base URL of the existing backend |
| `VITE_APP_NAME` | `Conversation Thematic Analysis` | Title shown in the UI |
| `VITE_AUTH_MODE` | `disabled` | Reserved for a future auth layer |

## Deployment

### Static hosting

Run `npm run build` and serve the contents of `dist/` from any static host
(Vercel, Netlify, S3 + CloudFront, GitHub Pages, etc.). Configure the host
to fall back to `index.html` for unknown routes so client-side routing works.

### Docker / Nginx

```bash
docker build -f Dockerfile.web \
  --build-arg VITE_API_BASE_URL=https://your-domain.com/api \
  -t cta-web .
docker run -p 8080:80 cta-web
```

`nginx/default.conf` serves the SPA, falls back to `index.html`, and proxies
`/api/` to the Docker Compose backend service named `api`. For standalone
static hosting, build with `VITE_API_BASE_URL` set to the deployed backend
origin instead of `/api`.

### CORS

If the backend is on a different origin than the frontend, configure CORS on
the backend to allow the frontend origin.

## How the interface connects to the backend

- All HTTP traffic goes through `src/api/client.ts`, which reads
  `VITE_API_BASE_URL` and exposes typed `get / post / put / patch / del /
  upload / download` helpers, plus an `ApiError` class.
- Per-resource API modules in `src/api/*.ts` map to backend endpoints:

| Module | Endpoints (relative to `VITE_API_BASE_URL`) |
|---|---|
| `codebooks.ts` | `/codebooks`, `/codebooks/:id`, `/codebooks/upload`, `/codebooks/validate`, `/codebooks/:id/versions` |
| `conversations.ts` | `/conversations`, `/conversations/:id`, `/conversations/:id/turns`, `/conversations/:id/segments`, `/conversations/import` |
| `preprocessing.ts` | `/preprocessing` |
| `runs.ts` | `/runs`, `/runs/:id`, `/runs/:id/start`, `/runs/:id/cancel` |
| `phases.ts` | `/runs/:id/phases`, `/runs/:id/phases/:n` |
| `annotations.ts` | `/runs/:id/annotations`, `/runs/:id/segments/:segId/suggestions` |
| `themes.ts` | `/runs/:id/candidate-themes`, `/runs/:id/candidate-themes/merge`, `/runs/:id/candidate-themes/:id/split` |
| `memos.ts` | `/memos`, `/memos/:id` |
| `audit.ts` | `/audit` |
| `reliability.ts` | `/runs/:id/reliability`, `/runs/:id/reliability/disagreements/:id` |
| `exports.ts` | `/exports`, `/exports/:id/download` |

If your backend exposes slightly different paths, edit the corresponding
file in `src/api/` — that is the single place where endpoint mappings live.

## Braun & Clarke phases in the UI

The six phases are declared once in `src/types/phase.ts`
(`BRAUN_CLARKE_PHASES`) and rendered as a vertical timeline by
`PhaseTimeline` / `PhaseCard`. The page at `/workflow/:runId` shows status,
notes, and timestamps per phase, with explicit actions to mark phases as
`in_progress` or `completed` and to add phase memos. Phase status comes from
`GET /runs/:id/phases` and updates go through `PATCH /runs/:id/phases/:n`.

## Researcher interpretation vs. software workflow support

The interface is built around a single principle: the software structures the
workflow, the researcher provides the substantive interpretation.

- Auto-generated themes are always labelled "candidate themes" (see
  `CandidateThemeBoard` and `ThemeReviewPanel`) and require explicit
  researcher decisions (rename, flag, reject, merge, split) with a rationale
  field saved through the API.
- Annotations are tagged with their `source` (`human`, `imported`,
  `rule_based`, `ai_assisted`) and visually distinguished, making clear that
  rule-based suggestions do not replace human coding.
- The Reliability page carries a visible note that reliability statistics
  are optional and depend on the analytic orientation; nothing in the UI
  presents Cohen's κ as a pass/fail gate.
- All content is fetched from the backend; the frontend ships no hard-coded
  themes, codes, or analytical conclusions.
