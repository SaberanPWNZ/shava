# Docker deployment guide

This project ships with two ready-to-use Docker stacks:

| Environment | Compose file              | Env file template      |
|-------------|---------------------------|------------------------|
| Development | `docker-compose.yml`      | `.env.dev.example`     |
| Production  | `docker-compose.prod.yml` | `.env.prod.example`    |

Both stacks contain a Django + DRF backend (`web`), a SvelteKit frontend
(`frontend`), PostgreSQL (`db`), Redis (`redis`) and Celery worker / beat
(`celery_worker`, `celery_beat`). The production stack adds an `nginx`
reverse proxy that terminates TLS and serves static / media files. The dev
stack additionally ships a MinIO container as a local S3-compatible store.

---

## 1. Development

```bash
cp .env.dev.example .env.dev
# edit .env.dev as needed (DJANGO_SECRET_KEY, DB credentials, …)
docker compose up --build
```

Services and ports (bound to `127.0.0.1` only — never exposed to the LAN):

- Django backend: <http://127.0.0.1:8000>
- SvelteKit frontend: <http://127.0.0.1:5173>
- PostgreSQL: `127.0.0.1:5432`

Useful commands:

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell
docker compose exec db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
docker compose logs -f web
docker compose down            # stop
docker compose down -v         # stop and DROP the database
```

---

## 2. Production

### 2.1 Prepare the host

1. Install Docker Engine and Docker Compose v2.
2. Open ports **80** and **443** in your firewall. Do **not** open 5432 or 8000
   to the public internet.
3. Obtain TLS certificates (Let's Encrypt is recommended) and place them at:

   ```
   ./certs/fullchain.pem
   ./certs/privkey.pem
   ```

   The simplest one-shot bootstrap with `certbot` running on the host
   (nginx must be temporarily stopped or run with the HTTP server only):

   ```bash
   sudo apt-get install -y certbot
   sudo certbot certonly --standalone \
       -d example.com -d www.example.com \
       --email admin@example.com --agree-tos --non-interactive
   sudo cp /etc/letsencrypt/live/example.com/fullchain.pem ./certs/
   sudo cp /etc/letsencrypt/live/example.com/privkey.pem  ./certs/
   sudo chown "$USER":"$USER" ./certs/*.pem
   ```

   For automated renewals add a host cron entry that copies the renewed
   files into `./certs/` and reloads nginx inside the running container.
   Replace `/opt/shava` with the absolute path to your checkout:

   ```cron
   0 3 * * * certbot renew --quiet --deploy-hook \
       'install -m 644 -o root -g root /etc/letsencrypt/live/example.com/fullchain.pem /opt/shava/certs/fullchain.pem && \
        install -m 600 -o root -g root /etc/letsencrypt/live/example.com/privkey.pem  /opt/shava/certs/privkey.pem && \
        docker compose -f /opt/shava/docker-compose.prod.yml exec -T nginx nginx -s reload'
   ```

   The HTTP server in `nginx.conf` already serves
   `/.well-known/acme-challenge/` from `/var/www/certbot`, so you can
   alternatively run certbot in `--webroot` mode by mounting
   `/var/www/certbot` into the nginx container.

### 2.2 Configure secrets

```bash
cp .env.prod.example .env.prod
# Edit .env.prod and fill in:
#   - DJANGO_SECRET_KEY (long random string)
#   - POSTGRES_PASSWORD
#   - ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS / CORS_ALLOWED_ORIGINS for your domain
#   - DOMAIN_NAME and VITE_API_BASE_URL
```

> ⚠️ **Never commit `.env.prod`.** It is excluded by `.gitignore`.
>
> Generate a secret key:
>
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(64))"
> ```

### 2.3 Launch

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

Migrations and `collectstatic` run automatically on container start.

To create the first admin user:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 2.4 Updating

```bash
git pull
docker compose -f docker-compose.prod.yml pull        # base images
docker compose -f docker-compose.prod.yml up -d --build
```

### 2.5 Backups

```bash
docker compose -f docker-compose.prod.yml exec db \
    pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
    | gzip > backup-$(date +%F).sql.gz
```

---

## 3. Security checklist

The configuration in this repository already enforces the following:

- [x] **No public Postgres port.** In dev it binds to `127.0.0.1`; in prod it
      stays inside the docker network.
- [x] **No public web/frontend ports in prod.** Only nginx (80 + 443) is
      exposed.
- [x] **Containers run as non-root.** Backend, frontend, and nginx all use
      unprivileged users; `no-new-privileges` is set in `docker-compose.prod.yml`.
- [x] **`DEBUG=False` is enforced in prod**, both via `.env.prod` and a
      hard override in `docker-compose.prod.yml`.
- [x] **`SECRET_KEY` is required** when `DEBUG=False` — the app fails to start
      without it.
- [x] **`debug_toolbar`** is loaded only when `DEBUG=True`.
- [x] **HTTPS hardening** when `DEBUG=False`: `SECURE_SSL_REDIRECT`, HSTS,
      `Secure`/`HttpOnly` cookies, `SECURE_PROXY_SSL_HEADER`, `Referrer-Policy`,
      `X-Frame-Options=DENY`, `nosniff`.
- [x] **CSRF trusted origins** are read from `CSRF_TRUSTED_ORIGINS`.
- [x] **CORS origins are explicit** — no wildcards.
- [x] **DRF throttling** for auth, registration, and helpful-vote endpoints.
- [x] **Edge rate limiting** in nginx for `/api/`, `/api/token/*`,
      `/api/users/(login|register|password)`, and `/admin/` (defence in depth).
- [x] **HTTP → HTTPS redirect**, modern TLS only (TLS 1.2 + 1.3), no session
      tickets, server-preferred ciphers.
- [x] **Strict response headers** in nginx: HSTS (1 year, preload),
      strict CSP, `X-Content-Type-Options=nosniff`, `Permissions-Policy`,
      `Cross-Origin-Opener-Policy=same-origin`, `X-Frame-Options=DENY`.
      `X-XSS-Protection` is intentionally omitted (deprecated).
- [x] **Hidden file access blocked** in nginx (e.g. `.git`, `.env`).
- [x] **Body / header timeouts and `client_max_body_size`** set to limit
      slow-loris and large-upload DoS.
- [x] **gzip enabled** for safe MIME types.
- [x] **Healthchecks** on all services.
- [x] **Multi-stage Python image** keeps build tools out of the final
      production image and reduces the attack surface.
- [x] **Multi-stage SvelteKit image** (`frontend/Dockerfile.prod`):
      separate `deps` / `builder` / `production` stages copy only the
      built `build/` directory, pruned production `node_modules` and
      `package.json` into a `node:20-alpine` runtime running as the
      unprivileged `node` user with a baked-in healthcheck. Roughly
      **148 MB** vs **762 MB** for the dev image (~80 % smaller).
      Note: we serve the frontend via `node build/index.js` (SvelteKit
      `@sveltejs/adapter-node`, SSR) rather than copying the build
      output into nginx — `nginx` only fronts TLS / static / media and
      reverse-proxies HTTP to the SvelteKit Node process on port 3000.
- [x] **Pinned Docker base images** (`python:3.12-slim`, `node:20-alpine`,
      `postgres:15-alpine`, `nginx:1.27-alpine`).

### Things to do per environment

- Rotate `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD` on a schedule.
- Restrict access to `/admin/` (e.g., IP allowlist via nginx `allow`/`deny`,
  VPN, or basic auth) if it does not need to be public.
- Run `docker scout cves` (or `trivy image …`) periodically against built
  images.
- Keep base images updated (`docker compose pull && up -d --build`).
- Configure off-host log shipping and monitoring.
- Configure automated database backups and test restores.
