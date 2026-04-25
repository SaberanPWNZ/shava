"""Gunicorn configuration for the Shava backend.

Tuned for running behind nginx (which terminates TLS and forwards via the
``X-Forwarded-Proto`` header — see ``config.settings.SECURE_PROXY_SSL_HEADER``).

Most knobs are overridable via environment variables so the same image can be
re-used across staging / production with different sizing.
"""

from __future__ import annotations

import multiprocessing
import os


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


# ----- Networking -------------------------------------------------------------
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")

# ----- Worker model -----------------------------------------------------------
# Default to (2 * CPU) + 1 sync workers, the value Gunicorn itself recommends
# for typical Django workloads.
workers = _env_int("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")
threads = _env_int("GUNICORN_THREADS", 1)

# Recycle workers periodically to mitigate memory leaks in long-running
# processes; jitter avoids a thundering herd on restart.
max_requests = _env_int("GUNICORN_MAX_REQUESTS", 1000)
max_requests_jitter = _env_int("GUNICORN_MAX_REQUESTS_JITTER", 100)

# ----- Timeouts ---------------------------------------------------------------
timeout = _env_int("GUNICORN_TIMEOUT", 60)
graceful_timeout = _env_int("GUNICORN_GRACEFUL_TIMEOUT", 30)
keepalive = _env_int("GUNICORN_KEEPALIVE", 5)

# ----- Reverse-proxy awareness ------------------------------------------------
# Trust forwarded headers from nginx running on the same Docker network.
forwarded_allow_ips = os.getenv("GUNICORN_FORWARDED_ALLOW_IPS", "*")

# ----- Logging ---------------------------------------------------------------
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")  # stdout
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")    # stderr
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s '
    '"%(f)s" "%(a)s" %(D)sus'
)

# ----- Process naming --------------------------------------------------------
proc_name = os.getenv("GUNICORN_PROC_NAME", "shava-backend")

# ----- Preload application ---------------------------------------------------
# Reduces per-worker memory by loading the WSGI app once in the master.
preload_app = os.getenv("GUNICORN_PRELOAD", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
