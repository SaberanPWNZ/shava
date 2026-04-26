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
- [ ] All public endpoints documented (tags, request/response examples).
      Partial: `users` email-flow endpoints annotated; the auth extension
      now resolves bearer auth on every operation. Remaining APIView-based
      endpoints (`MeView`, `LogoutView`, `UserBanView`, …) still need
      `@extend_schema` decorators — tracked separately.
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
- [ ] Gunicorn config (`backend/gunicorn.conf.py`) with sane workers.
- [ ] `nginx.conf` updated to terminate TLS and serve static.
- [ ] PostgreSQL used in prod (already in `docker-compose.prod.yml` —
      verify and document).
- [ ] Deployment runbook in `DOCKER_README.md`.
- [ ] Closes #31.

---

### 6. UX — P2

#### 6.1 Skeleton loaders + optimistic updates + toasts
**Labels:** `frontend`, `ux`, `P2`

**Acceptance criteria.**
- [ ] `Skeleton` component used on `/places`, `/places/[id]`, `/profile`.
- [ ] Optimistic create/edit for reviews and ratings; rollback on error.
- [ ] Toast component in `src/lib/components/ui/`; used by services on
      success/error.

#### 6.2 Accessibility polish
**Labels:** `frontend`, `a11y`, `P2`

**Acceptance criteria.**
- [ ] `eslint-plugin-svelte` a11y rules enabled; zero warnings.
- [ ] All interactive elements keyboard-navigable; focus rings visible.
- [ ] Lighthouse a11y ≥ 95 on `/`, `/places`, `/places/[id]`.

#### 6.3 PWA support
**Labels:** `frontend`, `ux`, `P3`

**Acceptance criteria.**
- [ ] `@vite-pwa/sveltekit` configured; manifest + icons.
- [ ] Offline page; cache strategy for static + GET API.
- [ ] Installable on Android/iOS.

#### 6.4 Responsive layout audit (closes #16)
**Labels:** `frontend`, `ux`, `P2`

**Acceptance criteria.**
- [ ] All pages render correctly at 320, 375, 768, 1024, 1440 px.
- [ ] No horizontal scroll on mobile; touch targets ≥ 44 px.
- [ ] Closes #16.

---

### 7. Frontend features — P2

#### 7.1 Search + filters on places list
**Labels:** `frontend`, `feature`, `P2`

**Acceptance criteria.**
- [ ] Text search by name; filters by city and minimum rating.
- [ ] State synced with URL query params.
- [ ] Debounced API calls.

#### 7.2 User profile: my reviews / my places / points history
**Labels:** `frontend`, `feature`, `P2`

**Acceptance criteria.**
- [ ] `/profile` tabs for reviews, places, points (gamification).
- [ ] Pagination on each tab.

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
- [ ] `GET /api/gamification/leaderboard/` paginated, ordered by points.
- [ ] `/leaderboard` page on frontend.

#### 9.2 Badges
**Labels:** `backend`, `frontend`, `gamification`, `P3`

**Acceptance criteria.**
- [ ] `Badge` + `UserBadge` models; awarded by signal handlers.
- [ ] First badges: First Review, 10 Reviews, First Place, Helpful (10
      helpful votes).
- [ ] Displayed on profile.

---

### 10. SEO — P2 (closes #17)

#### 10.1 Meta tags, Open Graph, sitemap, robots.txt
**Labels:** `frontend`, `seo`, `P2`

**Acceptance criteria.**
- [ ] `<svelte:head>` with title/description/OG/Twitter cards on every
      page; reusable `Seo.svelte` component.
- [ ] Dynamic OG for `/places/[id]` (place name + rating + photo).
- [ ] `/robots.txt` and `/sitemap.xml` generated server-side
      (place + article URLs included).
- [ ] Lighthouse SEO ≥ 95.
- [ ] Closes #17.

---

### 11. Admin — P3

#### 11.1 Moderation dashboard for places & reviews
**Labels:** `frontend`, `admin`, `P3`

**Acceptance criteria.**
- [ ] `/admin/moderation` lists pending places and reported reviews.
- [ ] Approve / reject with reason; uses existing
      `place-moderation-action` endpoint.
- [ ] Audit log entry for each action.

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
