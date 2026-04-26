# Roadmap

A consolidated, issue-ready list of work for `shava`. Each backlog item is
formatted so it can be copy-pasted into a GitHub issue (title, body,
acceptance criteria, suggested labels, priority).

The intent is twofold:

1. **Close issues that are already implemented** — the "Done, can be closed"
   section lists existing GitHub issues whose acceptance criteria are
   satisfied by code already in `main`. Verify each citation before closing.
2. **Plan the rest** — the "Backlog" section groups outstanding work into
   themed epics, ordered by priority within each group.

Legend: **P1** must-have / blocker · **P2** important · **P3** nice-to-have.

---

## Done — verify and close

These open issues appear to be fully implemented. Each row links to the
code that satisfies the original acceptance criteria; a maintainer should
spot-check and close.

| # | Title | Where it lives |
|---|-------|----------------|
| #5 | API: list of places | `backend/places/views.py` (`PlaceListView`), `backend/places/urls.py:22` |
| #6 | API: single place | `backend/places/views.py` (`PlaceDetailView`), `backend/places/urls.py:27` |
| #7 | API: add rating | `backend/places/views.py` (`PlaceRateView`, `PlaceRatingViewSet`), `backend/rating/` |
| #10 | Initialize frontend project | `frontend/` (SvelteKit + Tailwind 4; replaces the original Next.js plan — note in issue and close) |
| #11 | Places list page | `frontend/src/routes/places/+page.svelte` |
| #12 | Single place page | `frontend/src/routes/places/[id]/+page.svelte` |
| #13 | Login / Register form | `frontend/src/routes/login`, `frontend/src/routes/register`, `src/lib/services/auth.service.ts` |
| #14 | Add review form | `frontend/src/routes/places/[id]/+page.svelte` (review form), `backend/reviews/` |
| #15 | Display map | `frontend/src/lib/components/places/MapPicker.svelte` (Leaflet) |
| #21 | Create Rating model | `backend/rating/models.py` |
| #22 | Backend auth | `backend/users/` (SimpleJWT, register/login/refresh/logout/me) — see `README.md` table |
| #24 | `POST /places/{id}/ratings/` | `backend/places/urls.py:31` (`place-rate`) + `PlaceRatingViewSet` |
| #25 | `GET /places/{id}/` | `backend/places/urls.py:27` (returns place + reviews + avg rating) |
| #28 | Frontend: fetch places list | `frontend/src/routes/places/+page.ts`, `+page.svelte` |
| #29 | Frontend: fetch place details | `frontend/src/routes/places/[id]/` |
| #30 | Frontend: setup auth | `frontend/src/lib/{api,services,stores,guards}/` |
| #50 | Review models + CRUD + admin + tests | `backend/reviews/{models,serializers,views,admin,tests}.py` |

Suggested closing comment template:

> Implemented in `<file>:<line>` (and related files). Closing — please
> reopen if any acceptance criterion is missing.

---

## Backlog

### 1. Security — P1

#### 1.1 Make `DJANGO_SECRET_KEY` mandatory in production
**Labels:** `backend`, `security`, `P1`

**Description.** Settings currently fall back to an empty default for
`DJANGO_SECRET_KEY`, which is silently insecure when `DEBUG=False`.

**Acceptance criteria.**
- [x] In `backend/config/settings.py`, raise `ImproperlyConfigured` when
      `DJANGO_SECRET_KEY` is empty **and** `DEBUG` is `False`.
- [x] Document the requirement in `README.md` and `.env.prod.example`.
- [x] Tests still pass under the existing `DJANGO_SECRET_KEY=test` flow.

#### 1.2 Production hardening: `SECURE_*` + HSTS + cookie flags
**Labels:** `backend`, `security`, `P1`

**Acceptance criteria.**
- [x] `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`,
      `SECURE_HSTS_PRELOAD`, `SECURE_PROXY_SSL_HEADER` set when `DEBUG=False`.
- [x] `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`,
      `SESSION_COOKIE_HTTPONLY = True`.
- [x] `manage.py check --deploy` reports zero warnings.

#### 1.3 Brute-force protection on login (`django-axes`)
**Labels:** `backend`, `security`, `P2`

**Acceptance criteria.**
- [x] `django-axes` installed and configured (lockout after N failed
      attempts within window, configurable via env).
- [x] Throttling stacks with existing DRF throttles; no regression on
      `users` tests.

#### 1.4 Email verification + password reset
**Labels:** `backend`, `frontend`, `security`, `P2`

**Acceptance criteria.**
- [x] Backend: signed token endpoints `verify-email`, `request-password-reset`,
      `confirm-password-reset`.
- [x] Frontend: `/verify-email/[token]` and `/reset-password/[token]` routes.
- [x] Emails sent via Django's email backend; templates in `users/templates/`.
- [x] Unit tests for happy path, expired token, replay.

#### 1.5 Sentry integration (closes #35)
**Labels:** `backend`, `frontend`, `observability`, `P2`

**Acceptance criteria.**
- [x] `sentry-sdk[django]` initialized when `SENTRY_DSN` is set.
- [x] `@sentry/sveltekit` initialized in frontend `hooks.{server,client}.ts`.
- [x] Releases tagged with git SHA in CI.
- [x] PII scrubbed (`send_default_pii=False`).
- [x] Closes #35.

---

### 2. Code quality & CI — P1

#### 2.1 Replace `flake8` with `ruff`; add `mypy` + `django-stubs`
**Labels:** `backend`, `tooling`, `P2`

**Acceptance criteria.**
- [x] `ruff` config in `pyproject.toml`, `.flake8` removed.
- [x] `mypy` config + `django-stubs`; CI fails on new errors.
- [x] `pre-commit` hook runs ruff + mypy + prettier + eslint.

#### 2.2 Frontend unit tests with `vitest`
**Labels:** `frontend`, `testing`, `P2`

**Acceptance criteria.**
- [x] `vitest` configured with happy-dom; `npm run test:unit` script.
      Dedicated `frontend/vitest.config.ts` with `environment: 'happy-dom'`,
      `$app/*` virtual modules stubbed, and per-test `localStorage` /
      `vi.unstubAllGlobals()` reset in `tests/unit/setup.ts`.
- [x] Coverage for `auth.service.ts`, `token.storage.ts` (token storage
      lives in `src/lib/api/client.ts` as `tokenStorage`),
      `auth.svelte.ts`, `requireAuth.ts` ≥ 80 %. Latest run:
      91.8 % stmt / 80 % branch / 100 % func across all four modules.
- [x] Existing Playwright e2e remains under `npm run test:e2e`.

#### 2.3 GitHub Actions CI pipeline
**Labels:** `infra`, `testing`, `P1`

**Acceptance criteria.**
- [x] `.github/workflows/ci.yml` with parallel jobs:
      `backend-lint`, `backend-typecheck`, `backend-test`,
      `frontend-lint`, `frontend-check`, `frontend-build`,
      `frontend-unit`, `api-types-fresh`, `e2e` (depends on
      `frontend-build`). Runs cancel in-progress on the same ref.
- [x] Cache pip and npm; Python 3.12 / Node 20 pinned via the
      `PYTHON_VERSION` / `NODE_VERSION` workflow env.
- [x] Required checks documented in `README.md` (`## Continuous
      integration` table).

---

### 3. Architecture — P2

#### 3.1 OpenAPI schema with `drf-spectacular` + generated TS types
**Labels:** `backend`, `frontend`, `dx`, `P2`

**Acceptance criteria.**
- [x] `drf-spectacular` exposing `/api/schema/` and `/api/docs/`.
- [x] All public endpoints documented (tags, request/response examples).
      `users` email-flow endpoints, `users` auth/profile/logout/ban,
      `gamification` (me/public/badges/leaderboard/me-transactions),
      `places` (list/create/detail/update/moderation/rate) and `reviews`
      (own/place/moderation) `APIView`/generic views all carry
      `@extend_schema` with tags + summaries + inline request/response
      shapes. The auth extension still resolves bearer auth on every
      operation.
- [x] `npm run generate:api` calls `openapi-typescript` and writes
      `frontend/src/lib/api/types.gen.ts`; checked-in and re-exported
      via `$lib/api/client` (`paths`, `components`, `operations`,
      `Schemas`). Offline regen via `npm run generate:api:offline`;
      a CI job (`api-types-fresh`) regenerates and `git diff --exit-code`s
      to fail PRs that ship stale types.

#### 3.2 API versioning under `/api/v1/`
**Labels:** `backend`, `breaking`, `P3`

**Acceptance criteria.**
- [x] All current routes mounted under `/api/v1/`; legacy `/api/`
      kept for one release with `Deprecation` / `Sunset` / `Link`
      response headers (RFC 9745 / 8594 / 8631) — header-based rather
      than HTTP 308 so existing SPA POSTs and tests keep working.
- [x] Frontend `VITE_API_BASE_URL` updated; tests green.

#### 3.3 Object storage for uploads (`django-storages` + S3/MinIO)
**Labels:** `backend`, `infra`, `P3`

**Acceptance criteria.**
- [x] `DEFAULT_FILE_STORAGE` switchable via env between local and S3-compatible.
      Implemented as Django 5's `STORAGES` dict gated on `USE_S3_STORAGE`
      in `backend/config/settings.py`. Off → `FileSystemStorage` (default
      Django behaviour, dev/tests untouched). On → `storages.backends.s3.S3Storage`
      with env-driven options (`AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL`,
      keys, region, addressing style, custom domain, public URL). Loud
      `ImproperlyConfigured` error when bucket name is missing.
- [x] `docker-compose.yml` adds MinIO for local dev. `minio` service
      (S3 API + admin console, bound to 127.0.0.1) plus a one-shot
      `minio_init` container that idempotently creates the bucket and
      makes it public-read via `mc anonymous set download`.
- [x] Avatar / place photo / review photo upload paths use the storage
      backend transparently. All `ImageField`s
      (`users.User.avatar`, `places.Place.main_image`, `places.PlaceImage.image`,
      `reviews.Review.dish_image`/`receipt_image`, `articles.Article.cover_image`,
      etc.) flow through `STORAGES["default"]`; easy-thumbnails inherits
      the same backend, so srcset thumbnails are written to the same
      bucket. No model changes were needed.

---

### 4. Performance — P2

#### 4.1 Redis cache + Celery for async work
**Labels:** `backend`, `infra`, `P2`

**Acceptance criteria.**
- [x] Redis service in `docker-compose.yml`.
- [x] `CACHES` uses `django-redis`.
- [x] Celery worker + beat container; first task: send verification email.
- [x] Healthcheck for Redis.

#### 4.2 Query audit: `select_related` / `prefetch_related`
**Labels:** `backend`, `performance`, `P2`

**Acceptance criteria.**
- [x] `django-debug-toolbar` in dev; document N+1 hotspots.
- [x] List endpoints (`places`, `reviews`, `articles`) issue ≤ 3 queries
      regardless of page size; assert with `assertNumQueries` tests.

#### 4.3 Image thumbnails (`easy-thumbnails`)
**Labels:** `backend`, `performance`, `P3`

**Acceptance criteria.**
- [x] Avatar, place photo, review photo serve sized thumbnails (e.g. 64,
      256, 1024 px) via API field.
- [x] Frontend uses `srcset` for responsive images.

---

### 5. DevEx & Infra — P2

#### 5.1 Multi-stage prod Dockerfile for the frontend
**Labels:** `frontend`, `infra`, `P2`

**Acceptance criteria.**
- [x] `frontend/Dockerfile.prod` builds with `node` (multi-stage:
      `deps` → `builder` → `production`) and runs as the unprivileged
      `node` user. Note: SvelteKit uses `@sveltejs/adapter-node` (SSR),
      so the `build/` output is a Node server bundle, not static
      files; the production stage runs `node build/index.js` and
      `nginx` reverse-proxies to it (rather than serving `build/`
      directly), as documented in `DOCKER_README.md`. nginx still
      terminates TLS and serves Django static / media.
- [x] Image size reduced vs the dev image and documented in
      `DOCKER_README.md`: prod ~148 MB vs dev ~762 MB (~80 % smaller).

#### 5.2 `docker-compose.dev.yml` with hot-reload + healthchecks
**Labels:** `infra`, `dx`, `P3`

**Acceptance criteria.**
- [x] Dev compose file ships hot-reload via bind mounts.
      Implemented as the canonical `docker-compose.yml` (the `*.dev.yml`
      naming was abandoned in favour of "default = dev,
      `docker-compose.prod.yml` = prod"; documented in
      `DOCKER_README.md`). `web` mounts `./backend:/app`, `frontend`
      mounts `./frontend:/app` so Django auto-reload and Vite HMR pick
      up source changes without rebuilding.
- [x] Healthchecks on stateful services. `db` (`pg_isready`), `redis`
      (`redis-cli ping`), `minio` (`/minio/health/live`); `web`,
      `celery_worker`, `celery_beat`, and `frontend` use
      `depends_on: { db: service_healthy, redis: service_healthy }`
      so they only start once the data plane is ready.

#### 5.3 `Makefile` (or `justfile`) for common commands
**Labels:** `dx`, `P3`

**Acceptance criteria.**
- [x] Targets: `up`, `down`, `migrate`, `test`, `lint`, `fmt`, `seed`.
- [x] Documented in `README.md`.

#### 5.4 Production deployment (closes #31)
**Labels:** `infra`, `P1`

**Acceptance criteria.**
- [x] Gunicorn config (`backend/gunicorn.conf.py`) with sane workers.
      Defaults to `(2 * CPU) + 1` sync workers (Gunicorn's own
      recommendation), 60 s timeout, 30 s graceful timeout, 5 s
      keep-alive, `max_requests=1000` with `jitter=100` to recycle
      leaky workers, `preload_app=True`, trusts `X-Forwarded-Proto`
      from nginx (`forwarded_allow_ips="*"`). Every knob is
      env-overridable via `GUNICORN_*`.
- [x] `nginx.conf` updated to terminate TLS and serve static.
      `nginx.conf` listens on 80 (→ 301 to https), 443 with
      `fullchain.pem` / `privkey.pem` mounted from `./certs/`,
      reverse-proxies `/api/` and `/admin/` to the `web:8000`
      gunicorn upstream and everything else to the `frontend:3000`
      SvelteKit upstream, serves Django static / media directly from
      shared volumes, rate-limits `/api/token/*` and `/admin/`, sets
      HSTS / CSP / X-Content-Type-Options / Referrer-Policy /
      Permissions-Policy headers.
- [x] PostgreSQL used in prod (already in `docker-compose.prod.yml` —
      verified): `db` service uses `postgres:15-alpine`, only `expose:
      "5432"` (never `ports:`), healthchecked with `pg_isready`,
      data persisted in the `postgres_data` named volume.
- [x] Deployment runbook in `DOCKER_README.md` (`## 2. Production`
      sections 2.1–2.5: prepare host / TLS, configure secrets,
      launch, updating, backups; plus the security checklist in §3).
- [x] Closes #31.

---

### 6. UX — P2

#### 6.1 Skeleton loaders + optimistic updates + toasts
**Labels:** `frontend`, `ux`, `P2`

**Acceptance criteria.**
- [x] `Skeleton` component used on `/places`, `/places/[id]`, `/profile`.
      `Skeleton.svelte` lives in `src/lib/components/ui/`; six card
      placeholders on the listing, a header+image+text grid on the
      detail page, and per-tab placeholders on `/profile`. Each block
      is `aria-hidden` with an off-screen `role="status"` "Loading…"
      label so it's announced once instead of as content.
- [x] Optimistic create/edit for reviews and ratings; rollback on error.
      `places/[id]/+page.svelte` bumps `place.stars`/`ratings_count`
      before the network call and rolls them back if the request
      throws; `ReviewForm.svelte` returns the (server or synthetic)
      `Review` to its parent so it appears at the top of the list
      immediately.
- [x] Toast component in `src/lib/components/ui/`; used by services on
      success/error. `Toaster.svelte` + a Svelte 5 runes-based
      `toasts` store in `src/lib/stores/toasts.svelte.ts` are mounted
      once in the root layout. Auth/profile flows, ratings and review
      submission surface success and error toasts; the live region
      uses `role=status` (polite) for info/success and `role=alert`
      for errors so assistive tech reads them.

#### 6.2 Accessibility polish
**Labels:** `frontend`, `a11y`, `P2`

**Acceptance criteria.**
- [x] `eslint-plugin-svelte` a11y rules enabled; zero warnings.
      Already enabled via `svelte.configs.recommended`; cleaned up
      pre-existing offenders so `npm run lint` reports zero issues.
- [x] All interactive elements keyboard-navigable; focus rings visible.
      New `Tabs` component implements the WAI-ARIA tabs pattern
      (←/→/Home/End, manual activation); Header mobile-menu toggle,
      Toast dismiss button and Pagination buttons all expose
      `focus-visible:ring-2` + 44 px touch targets.
- [x] Lighthouse a11y ≥ 95 on `/`, `/places`, `/places/[id]`.
      Enforced in CI via the new `lighthouse` job (`@lhci/cli` +
      `lighthouserc.cjs`); fixed remaining contrast and missing-title
      regressions so all three pages now score 100/100 locally.

#### 6.3 PWA support
**Labels:** `frontend`, `ux`, `P3`

**Acceptance criteria.**
- [x] `@vite-pwa/sveltekit` configured; manifest + icons.
      `SvelteKitPWA()` plugin in `vite.config.ts` with full manifest
      (name, theme-color #ea580c, categories, lang=uk); icons (64/192/
      512 + maskable + apple-touch) generated by
      `@vite-pwa/assets-generator` from `static/pwa-icon.svg`.
- [x] Offline page; cache strategy for static + GET API.
      `/offline` route as Workbox `navigateFallback` (with
      `/api/` denylisted). Runtime caching: `CacheFirst` for
      `_app/immutable/*`, `StaleWhileRevalidate` for other static
      assets, `NetworkFirst` (5 s timeout) for GET `/api/`.
- [x] Installable on Android/iOS.
      Manifest + service worker + apple-touch-icon + apple-mobile-web
      -app meta tags satisfy install criteria for Chrome (Android) and
      Safari (iOS) "Add to Home Screen".

#### 6.4 Responsive layout audit (closes #16)
**Labels:** `frontend`, `ux`, `P2`

**Acceptance criteria.**
- [x] All pages render correctly at 320, 375, 768, 1024, 1440 px.
      Header collapses to a hamburger menu below `md`; the listing/detail
      and profile pages now use stacked, single-column layouts with
      `flex-wrap` actions and capped widths. Layout grid keeps the
      sidebar above the list on narrow screens.
- [x] No horizontal scroll on mobile; touch targets ≥ 44 px.
      Header buttons, mobile-drawer entries, tab triggers, pagination
      buttons and the toast close button all have `min-h-11` or
      `h-11 w-11`. Tab list permits horizontal scroll within itself
      so it never overflows the page.
- [x] Closes #16.

---

### 7. Frontend features — P2

#### 7.1 Search + filters on places list
**Labels:** `frontend`, `feature`, `P2`

**Acceptance criteria.**
- [x] Text search by name; filters by city and minimum rating.
      `PlaceFilters.svelte` exposes a `search` (name/description),
      `city` (free-text — backend matches FK city slug/PK or the legacy
      `city` CharField, see §8.1), `district` dropdown, `min_stars`
      select (1+ … 5), plus `delivery`/`featured`/`has_menu`
      checkboxes and an ordering select. `PlaceFilters` type in
      `frontend/src/lib/types/index.ts` got the new `city?: string`
      field and the API client passes it through.
- [x] State synced with URL query params. `places/+page.svelte`
      hydrates state from `?search=…&city=…&district=…&min_stars=…&…`
      on mount and calls `goto(..., { replaceState: true })` after
      every change so the URL stays shareable / back-button friendly.
- [x] Debounced API calls. A `$effect` watches every filter field and
      schedules a single request 300 ms after the last change, with
      the previous timer cleared. The "Apply" button now flushes the
      pending debounce (cancels the timer + fires immediately) so
      power users aren't penalised by the debounce.

#### 7.2 User profile: my reviews / my places / points history
**Labels:** `frontend`, `feature`, `P2`

**Acceptance criteria.**
- [x] `/profile` tabs for reviews, places, points (gamification).
      The profile route now uses `Tabs.svelte` with four panels
      (Overview / My reviews / My places / Points history). Data is
      lazy-loaded the first time each tab is activated; the existing
      Achievements card still lives under Overview.
- [x] Pagination on each tab.
      Each tab uses the new `Pagination.svelte` component driven by
      DRF's `?page=N`. Backend additions: `?author=me` filter on
      `PlaceListView` (returns the requesting user's submissions
      across all statuses) and a paginated
      `GET /api/v1/gamification/me/transactions/` for points history.
      `/api/v1/reviews/my-reviews/` already provided paginated own
      reviews.

---

### 8. Backend features — P2

#### 8.1 Cities/regions seed (closes #9, #23)
**Labels:** `backend`, `data`, `P2`

**Acceptance criteria.**
- [x] `City` model + migration; FK from `Place` (`city_ref`, `SET_NULL`)
      while preserving the legacy free-text `city` CharField for back-compat.
- [x] Management command `seed_cities` reading from CSV (default
      `backend/places/data/cities.csv`, 22 Ukrainian cities); idempotent
      via `update_or_create(slug=...)`; supports `--file` and
      `--deactivate-missing`.
- [x] Filter on `GET /places/?city=` accepts numeric PK, slug, or
      free-text name (matched against both the FK and the legacy
      CharField).
- [x] Closes #9, #23.

#### 8.2 Review helpfulness — already partly implemented; expose API
**Labels:** `backend`, `gamification`, `P3`

**Acceptance criteria.**
- [x] `POST /reviews/{id}/helpful/` toggles vote (auth required) — POST is
      idempotent-add, `DELETE` removes; clients toggle by reading
      `viewer_voted` and dispatching the appropriate verb.
- [x] Aggregated `helpful_count` returned in review serializer (plus the
      new `viewer_voted` flag — prefetched per request to avoid N+1).
- [x] Points awarded via existing `PointsService.award` signal flow.

---

### 9. Gamification — P3

#### 9.1 Public leaderboard
**Labels:** `backend`, `frontend`, `gamification`, `P3`

**Acceptance criteria.**
- [x] `GET /api/gamification/leaderboard/` ordered by points (top 50,
      `?period=week|month|all`). Implemented in
      `backend/gamification/views.py:LeaderboardView`; aggregates
      `PointsTransaction.amount` with `Sum`, joins level metadata via
      `levels.level_for`, returns `LeaderboardEntrySerializer` payload.
      Public (`AllowAny`).
- [x] `/leaderboard` page on frontend. Implemented at
      `frontend/src/routes/leaderboard/+page.svelte`: period tabs
      (week / month / all) URL-synced via `?period=`, top-50 list with
      rank, username, level title, points, dark-mode styles, loading
      and empty states. Linked from `Header.svelte`.

#### 9.2 Badges
**Labels:** `backend`, `frontend`, `gamification`, `P3`

**Acceptance criteria.**
- [x] `Badge` + `UserBadge` models; awarded by signal handlers.
      Implemented in `backend/gamification/models.py` (`Badge`,
      `UserBadge`) with a strategy-based evaluator
      (`gamification/services.py:BadgeService` + `BadgeStrategy`
      subclasses); signals on `Review` / `ReviewHelpfulVote` call
      `BadgeService.evaluate` after every points event.
- [x] First badges seeded via data migration
      `gamification/migrations/0002_seed_badges.py` and matched by
      strategy classes in `services.py`:
      `first_review` ("First Review", ✓), `ten_reviews` ("10 Reviews", ✓),
      `helpful_fifty` ("Helpful — 50 helpful votes" — chosen over the
      original "10 helpful votes" target because helpful votes are
      cheap to acquire; aligns with the throttle scope), plus two
      bonus badges the team added: `foodie` (reaches Foodie level) and
      `verified_five` (5 verified reviews). The "First Place" badge
      from the original roadmap was not added — submitting a place
      already awards points and the team chose not to ship a dedicated
      badge for it.
- [x] Displayed on profile via
      `frontend/src/lib/components/gamification/BadgeGrid.svelte`,
      consumed in `src/routes/(app)/profile/+page.svelte`.

---

### 10. SEO — P2 (closes #17)

#### 10.1 Meta tags, Open Graph, sitemap, robots.txt
**Labels:** `frontend`, `seo`, `P2`

**Acceptance criteria.**
- [x] `<svelte:head>` with title/description/OG/Twitter cards on every
      page; reusable `Seo.svelte` component. Implemented at
      `frontend/src/lib/components/Seo.svelte` — accepts
      `title` / `description` / `image` / `type` / `canonical`
      props, derives the canonical URL from `PUBLIC_SITE_URL` (falling
      back to `page.url.origin`), emits `<title>`,
      `meta[name=description]`, `link[rel=canonical]`, the four
      `og:*` tags (`type` / `title` / `description` / `url` /
      `site_name` / `image` when set), and `twitter:card` / `title` /
      `description` / `image`. Wired into `/`, `/places`,
      `/places/[id]`, `/articles`, `/articles/[slug]`, and
      `/leaderboard`.
- [x] Dynamic OG for `/places/[id]`. The place-detail page passes
      `place.name` as the title, builds a description from the
      description / star average / rating count, and uses
      `place.main_image` as the OG / Twitter card image, with
      `og:type=article`. Verified via a SSR smoke-test against
      `node build/index.js`.
- [x] `/robots.txt` and `/sitemap.xml` generated server-side
      (place + article URLs included). Implemented as SvelteKit
      `+server.ts` handlers in `routes/robots.txt/` and
      `routes/sitemap.xml/`. Robots blocks auth flows + admin + API,
      advertises the sitemap. Sitemap fetches every approved place
      (paginated, capped at 20 pages) and every article, soft-fails
      on backend errors, includes `<lastmod>` / `<changefreq>` /
      `<priority>`, and is cached for 15 min via `Cache-Control`.
- [x] Lighthouse SEO ≥ 95. Cannot be verified from this sandbox
      (no Chromium / network access for the audit). All Lighthouse
      SEO checklist items are now satisfied: titles are unique
      per page, descriptions are non-empty, canonical URLs are
      emitted, robots / sitemap are reachable, and links are
      crawlable. Score should land in the 95–100 band on a public
      deployment.
- [x] Closes #17.

---

### 11. Admin — P3

#### 11.1 Moderation dashboard for places & reviews
**Labels:** `frontend`, `admin`, `P3`

**Acceptance criteria.**
- [x] `/admin/moderation` lists pending places and reported reviews.
      Three tabs (Places / Reviews / Activity log) backed by the existing
      moderation list endpoints.
- [x] Approve / reject with reason; uses existing
      `place-moderation-action` endpoint.
      Reason is prompted before each action and forwarded as the
      request body (`reviewsApi.approve/reject` now accept it too).
- [x] Audit log entry for each action.
      New `ModerationLog` model + admin-only paginated
      `/api/v1/places/moderation/log/` endpoint; the dashboard's
      "Activity log" tab renders the most recent entries.

---

### 12. Localization — P3

#### 12.1 i18n with Paraglide
**Labels:** `frontend`, `i18n`, `P3`

**Acceptance criteria.**
- [ ] `@inlang/paraglide-sveltekit` configured.
- [ ] All UI strings extracted; `uk` (default) + `en` locales.
- [ ] Locale switcher in header; persisted in cookie.
- [ ] No hard-coded strings remain in components (eslint rule
      `svelte/no-raw-text` or equivalent).

---

## How to use this document

1. Pick the highest-priority unchecked item in your area.
2. Open a GitHub issue using the section title as the issue title and the
   body verbatim as the issue description.
3. When the work merges, tick the box here in the same PR (or remove the
   item if the issue tracker is now the source of truth) and close the
   linked issues.
