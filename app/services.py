import requests
from datetime import datetime, timezone
from typing import List, Tuple

# OPEN_METEO_BASE = "https://api.open-meteo.com/v1/meteoswiss"
OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"

def fetch_open_meteo_timeseries(lat: float, lon: float, start_date: str, end_date: str) -> List[Tuple[datetime, float, float]]:
    """
    Calls Open-Meteo MeteoSwiss hourly API for temperature_2m and relative_humidity_2m
    Returns list of (timestamp_utc, temperature, humidity)
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m",
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "UTC"
    }
    r = requests.get(OPEN_METEO_BASE, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    hrs = data.get("hourly", {})
    times = hrs.get("time", [])
    temps = hrs.get("temperature_2m", [])
    rhs = hrs.get("relative_humidity_2m", [])

    rows = []
    for i in range(min(len(times), len(temps), len(rhs))):
        ts = datetime.fromisoformat(times[i].replace("Z", "+00:00")).astimezone(timezone.utc)
        t = temps[i]
        h = rhs[i]
        rows.append((ts.replace(tzinfo=None), t, h))  # store naive UTC in SQLite
    return rows
