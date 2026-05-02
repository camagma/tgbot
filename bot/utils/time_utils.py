from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def is_night_hour(dt: datetime) -> bool:
    return 0 <= dt.hour <= 5
