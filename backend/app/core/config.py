import os


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_positive_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _parse_csv(value: str | None, default: list[str]) -> list[str]:
    if value is None:
        return default
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or default


DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]


API_TITLE = os.getenv("API_TITLE", "LendoJuntos API")
ACCESS_TOKEN_EXPIRE_MINUTES = _parse_positive_int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"), 480)
ENABLE_SEED_DATA = _parse_bool(os.getenv("ENABLE_SEED_DATA"), True)
CORS_ORIGINS = _parse_csv(os.getenv("CORS_ORIGINS"), DEFAULT_CORS_ORIGINS)
