from sqlalchemy import Column, Integer, Float, String, DateTime, UniqueConstraint
from .db import Base

class WeatherReading(Base):
    __tablename__ = "weather_readings"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, index=True, nullable=False)
    lon = Column(Float, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    temperature_2m = Column(Float, nullable=True)
    relative_humidity_2m = Column(Float, nullable=True)
    source = Column(String, default="open-meteo")

    __table_args__ = (
        UniqueConstraint("lat", "lon", "timestamp", name="uq_location_time"),
    )
