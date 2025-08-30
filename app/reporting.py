from io import BytesIO
from typing import List
from datetime import datetime
import base64
import pandas as pd
import matplotlib.pyplot as plt  # do not set styles; keep defaults
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

from app.schemas import WeatherReadingOut

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

# def to_dataframe(readings: List[WeatherReadingOut]) -> pd.DataFrame:
#     rows = [{
#         "timestamp": r.timestamp,
#         "temperature_2m": r.temperature_2m,
#         "relative_humidity_2m": r.relative_humidity_2m
#     } for r in readings]
#     df = pd.DataFrame(rows).sort_values("timestamp")
#     return df
#static working for location 47.37, 8.55 (Zurich)

def to_dataframe(readings: List[WeatherReadingOut]) -> pd.DataFrame:
    if not readings:
        # Return empty dataframe with expected columns if no data
        return pd.DataFrame(columns=["timestamp", "temperature_2m", "relative_humidity_2m"])
    
    rows = [{
        "timestamp": r.timestamp,
        "temperature_2m": r.temperature_2m,
        "relative_humidity_2m": r.relative_humidity_2m
    } for r in readings]
    df = pd.DataFrame(rows)
    
    # Only sort if we have data and the column exists
    if not df.empty and "timestamp" in df.columns:
        df = df.sort_values("timestamp")
    
    return df

def excel_bytes(df: pd.DataFrame) -> bytes:
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="weather")
    return bio.getvalue()

def chart_png_b64(df: pd.DataFrame) -> str:
    if df.empty:
        # Return a tiny blank image
        bio = BytesIO()
        plt.figure()
        plt.text(0.5, 0.5, "No data", ha="center", va="center")
        plt.savefig(bio, format="png", bbox_inches="tight")
        plt.close()
        return base64.b64encode(bio.getvalue()).decode()

    # Plot temperature and humidity vs time with separate axes labels
    fig = plt.figure(figsize=(10, 4.5))
    ax = plt.gca()
    ax.plot(df["timestamp"], df["temperature_2m"], label="Temperature (°C)")
    ax.plot(df["timestamp"], df["relative_humidity_2m"], label="Humidity (%)")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Value")
    ax.legend()
    fig.autofmt_xdate()
    bio = BytesIO()
    plt.savefig(bio, format="png", bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(bio.getvalue()).decode()

def render_pdf(readings: List[WeatherReadingOut], lat: float, lon: float) -> bytes:
    df = to_dataframe(readings)
    chart_b64 = chart_png_b64(df)

    if not df.empty:
        start = df["timestamp"].min()
        end = df["timestamp"].max()
    else:
        start = end = datetime.utcnow()

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape()
    )
    template = env.get_template("report.html")
    html = template.render(
        lat=lat,
        lon=lon,
        start=start,
        end=end,
        chart_b64=chart_b64,
        generated_at=datetime.utcnow()
    )

    pdf_bytes = HTML(string=html).write_pdf(stylesheets=[
        CSS(string="""
            @page { size: A4; margin: 18mm; }
            body { font-family: sans-serif; }
            h1 { margin-bottom: 0.2rem; }
            .meta { color: #444; font-size: 12px; margin-bottom: 1rem; }
            .chart { margin-top: 12px; }
            .footer { margin-top: 24px; font-size: 11px; color: #555; }
        """)
    ])
    return pdf_bytes
