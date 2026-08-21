import os

from .base import *

CURRENT_ENV = "development"


def _env_list(name, default):
    # Comma-separated env var, e.g. CORS_ALLOWED_ORIGINS=http://a,http://b —
    # keeps the existing hardcoded defaults when unset, so plain local dev
    # is unaffected. Lets a deployment (Portainer, etc.) whitelist its own
    # actual host/port without a code change or rebuild.
    raw = os.environ.get(name)
    if not raw:
        return default
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])

CORS_ALLOWED_ORIGINS = _env_list(
    "CORS_ALLOWED_ORIGINS",
    [
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:5173",
    ],
)

CSRF_TRUSTED_ORIGINS = _env_list(
    "CSRF_TRUSTED_ORIGINS",
    [
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:5173",
    ],
)
