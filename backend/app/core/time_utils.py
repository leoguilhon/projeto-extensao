from datetime import datetime, timedelta, timezone


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_iso() -> str:
    return now_utc().isoformat()


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def to_iso_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return normalize_datetime(value).isoformat()


def add_minutes(value: datetime, minutes: int) -> datetime:
    return value + timedelta(minutes=minutes)


def parse_iso_datetime(value: str) -> datetime:
    return normalize_datetime(datetime.fromisoformat(value))
