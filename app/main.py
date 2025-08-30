from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional
from datetime import datetime
import io

from app.db import Base, engine, get_db
from app.models import WeatherReading
from .schemas import WeatherReadingOut
from app.services import fetch_open_meteo_timeseries
from app.crud import upsert_readings, last_hours, by_range
from app.utils import last_n_days_range_utc, date_params_for_open_meteo
from app.reporting import to_dataframe, excel_bytes, render_pdf

app = FastAPI(title="Weather Report Service", version="1.0.0")

# Create tables on startup
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/weather-report", response_model=dict)
def weather_report(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    days: int = Query(2, ge=1, le=7),
    db=Depends(get_db)
):
    """
    Fetch past N days (default 2) of hourly temp & humidity from Open-Meteo
    and upsert into SQLite.
    """
    start_utc, end_utc = last_n_days_range_utc(days)
    start_date, end_date = date_params_for_open_meteo(start_utc, end_utc)

    rows = fetch_open_meteo_timeseries(lat, lon, start_date, end_date)
    inserted = upsert_readings(db, lat, lon, rows)

    return {
        "lat": lat,
        "lon": lon,
        "start_date": start_date,
        "end_date": end_date,
        "fetched_count": len(rows),
        "inserted_count": inserted
    }

@app.get("/export/excel")
def export_excel(
    hours: int = Query(48, ge=1, le=240),
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lon: Optional[float] = Query(None, ge=-180, le=180),
    db=Depends(get_db)
):
    """
    Returns the last `hours` hours as an Excel (.xlsx).
    If lat/lon provided, filters to that location.
    """
    if (lat is None) ^ (lon is None):
        raise HTTPException(status_code=400, detail="Provide both lat and lon, or neither.")

    readings = last_hours(db, hours, lat=lat, lon=lon)
    out = [WeatherReadingOut.model_validate(r) for r in readings]
    df = to_dataframe(out)
    xlsx = excel_bytes(df)

    fname = f"weather_data_{hours}h"
    if lat is not None and lon is not None:
        fname += f"_{lat}_{lon}"
    fname += ".xlsx"

    return StreamingResponse(
        io.BytesIO(xlsx),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'}
    )

@app.get("/export/pdf")
def export_pdf(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    start: Optional[str] = Query(None, description="ISO datetime UTC, e.g. 2025-08-27T00:00:00"),
    end: Optional[str] = Query(None, description="ISO datetime UTC, e.g. 2025-08-29T00:00:00"),
    db=Depends(get_db)
):
    """
    Generates a PDF report with a Matplotlib chart, via WeasyPrint.
    Date range defaults to last 48h if not provided.
    """
    if (start and not end) or (end and not start):
        raise HTTPException(status_code=400, detail="Provide both start and end, or neither.")

    if start and end:
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO like 2025-08-27T00:00:00")
    else:
        # default to last 48h
        from datetime import timedelta
        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(hours=48)

    readings = by_range(db, start_dt, end_dt, lat=lat, lon=lon)
    out = [WeatherReadingOut.model_validate(r) for r in readings]
    pdf = render_pdf(out, lat=lat, lon=lon)

    fname = f"weather_report_{lat}_{lon}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'}
    )
