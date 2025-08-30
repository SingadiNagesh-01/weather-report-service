from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WeatherReadingOut(BaseModel):
    lat: float
    lon: float
    timestamp: datetime
    temperature_2m: Optional[float]
    relative_humidity_2m: Optional[float]

    class Config:
        from_attributes = True
