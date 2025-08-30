from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Iterable, List, Tuple
from .models import WeatherReading

def upsert_readings(
    db: Session,
    lat: float,
    lon: float,
    rows: Iterable[Tuple[datetime, float, float]]
) -> int:
    """
    Insert-if-not-exists on (lat, lon, timestamp).
    Returns number of rows inserted (best-effort).
    """
    inserted = 0
    for ts, temp, rh in rows:
        exists = db.query(WeatherReading).filter(
            and_(
                WeatherReading.lat == lat,
                WeatherReading.lon == lon,
                WeatherReading.timestamp == ts
            )
        ).first()
        if exists:
            continue
        rec = WeatherReading(
            lat=lat, lon=lon, timestamp=ts,
            temperature_2m=temp, relative_humidity_2m=rh
        )
        db.add(rec)
        inserted += 1
    db.commit()
    return inserted

def last_hours(db: Session, hours: int, lat: float = None, lon: float = None) -> List[WeatherReading]:
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    q = db.query(WeatherReading).filter(WeatherReading.timestamp >= cutoff)
    if lat is not None and lon is not None:
        q = q.filter(and_(WeatherReading.lat == lat, WeatherReading.lon == lon))
    return q.order_by(WeatherReading.timestamp.asc()).all()

def by_range(db: Session, start: datetime, end: datetime, lat: float, lon: float) -> List[WeatherReading]:
    q = db.query(WeatherReading).filter(
        and_(
            WeatherReading.timestamp >= start,
            WeatherReading.timestamp <= end,
            WeatherReading.lat == lat,
            WeatherReading.lon == lon
        )
    )
    return q.order_by(WeatherReading.timestamp.asc()).all()
