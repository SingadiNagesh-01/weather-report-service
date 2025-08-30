from datetime import datetime, timedelta, timezone

def last_n_days_range_utc(days: int):
    """
    Returns (start_utc, end_utc) as timezone-aware datetimes in UTC
    covering the last N days.
    """
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=days)
    return start, end


def date_params_for_open_meteo(start, end):
    """
    Convert datetimes to the YYYY-MM-DD format required by Open-Meteo API.
    """
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
from datetime import datetime, timedelta, timezone

def last_n_days_range_utc(days: int):
    """
    Returns (start_utc, end_utc) as timezone-aware datetimes in UTC
    covering the last N days.
    """
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=days)
    return start, end


def date_params_for_open_meteo(start, end):
    """
    Convert datetimes to the YYYY-MM-DD format required by Open-Meteo API.
    """
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
