from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(str(value))
    except Exception:
        return None


def _safe_float(value: Any) -> Optional[float]:
    try:
        return float(str(value))
    except Exception:
        return None


def get_weather_data(location: str, forecast_days: int = 5) -> Optional[Dict[str, Any]]:
    """
    Fetch daily forecast from wttr.in and aggregate useful fields.

    - temp🌡️: daily avgtempC
    - humidity💧: average of hourly humidity values
    - wind💨: max of hourly windspeedKmph
    - precipitation💦: daily totalprecipMM

    Returns a dictionary of the form:
      {"location": <str>, "forecast": [{"date": str, ...}, ...]}
    """
    if not isinstance(location, str) or not location.strip():
        print("❌ Invalid location provided.")
        return None

    url = f"https://wttr.in/{quote(location.strip())}?format=j1"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        print("❌ Error fetching weather:", exc)
        return None

    days: List[Dict[str, Any]] = data.get("weather") or []
    if not days:
        print("❌ Unexpected response shape (missing 'weather').")
        return None

    try:
        num_days = max(1, int(forecast_days))
    except Exception:
        num_days = 5
    num_days = min(num_days, len(days))

    forecast: List[Dict[str, Any]] = []
    for day in days[:num_days]:
        date = day.get("date")
        temp_c = _safe_int(day.get("avgtempC"))
        precip_mm = _safe_float(day.get("totalprecipMM"))

        hourly = day.get("hourly") or []
        humidities = [_safe_int(h.get("humidity")) for h in hourly if h.get("humidity") is not None]
        winds_kmph = [_safe_int(h.get("windspeedKmph")) for h in hourly if h.get("windspeedKmph") is not None]

        valid_h = [h for h in humidities if h is not None]
        avg_humidity = round(sum(valid_h) / len(valid_h)) if valid_h else None

        valid_w = [w for w in winds_kmph if w is not None]
        max_wind_kmph = max(valid_w) if valid_w else None

        forecast.append({
            "date": date,
            "temp🌡️": temp_c,
            "humidity💧": avg_humidity,
            "wind💨": max_wind_kmph,
            "precipitation💦": precip_mm,
        })

    return {"location": location, "forecast": forecast}
