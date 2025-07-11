"""Helper functions for accessing the OpenAQ API."""

from datetime import datetime
from typing import Optional, List

import pandas as pd
import requests
from openaq import OpenAQ

BASE_URL = "https://api.openaq.org/v3"


def fetch_measurements_rest(city: Optional[str] = None,
                            country: Optional[str] = None,
                            parameter: str = "pm25",
                            date_from: Optional[str] = None,
                            date_to: Optional[str] = None,
                            limit: int = 100,
                            max_pages: int = 5,
                            api_key: Optional[str] = None) -> pd.DataFrame:
    """Fetch measurements from the REST API and return as DataFrame.

    Parameters
    ----------
    city : optional str
        City to filter measurements.
    country : optional str
        Country code to filter measurements.
    parameter : str
        Pollutant parameter (e.g., pm25, pm10, no2).
    date_from : optional str
        Start date in YYYY-MM-DD format.
    date_to : optional str
        End date in YYYY-MM-DD format.
    limit : int
        Number of records per page.
    max_pages : int
        Maximum number of pages to fetch.
    """
    headers = {"X-API-Key": api_key} if api_key else None

    # First fetch locations
    loc_params = {"limit": 1}
    if country:
        loc_params["iso"] = country
    loc_resp = requests.get(f"{BASE_URL}/locations", params=loc_params, headers=headers, timeout=30)
    loc_resp.raise_for_status()
    locations = [
        loc for loc in loc_resp.json().get("results", [])
        if city is None or (loc.get("locality") and loc["locality"].lower() == city.lower())
    ]

    records: List[dict] = []
    for loc in locations:
        sens_resp = requests.get(f"{BASE_URL}/locations/{loc['id']}/sensors", headers=headers, timeout=30)
        sens_resp.raise_for_status()
        sensors = [s for s in sens_resp.json().get("results", []) if s.get("parameter", {}).get("name") == parameter]
        for sensor in sensors:
            page = 1
            while page <= max_pages:
                params = {
                    "page": page,
                    "limit": limit,
                }
                if date_from:
                    params["date_from"] = date_from
                if date_to:
                    params["date_to"] = date_to
                resp = requests.get(
                    f"{BASE_URL}/sensors/{sensor['id']}/measurements",
                    params=params,
                    headers=headers,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                for m in data.get("results", []):
                    records.append({
                        "location": loc.get("name"),
                        "city": loc.get("locality"),
                        "sensor_id": sensor["id"],
                        "value": m.get("value"),
                        "unit": sensor["parameter"]["units"],
                        "datetime": m["period"]["datetimeFrom"]["utc"],
                        "coordinates.latitude": (m.get("coordinates", {}).get("latitude")
                                                 if m.get("coordinates") else loc.get("coordinates", {}).get("latitude")),
                        "coordinates.longitude": (m.get("coordinates", {}).get("longitude")
                                                  if m.get("coordinates") else loc.get("coordinates", {}).get("longitude")),
                    })
                if len(data.get("results", [])) < limit:
                    break
                page += 1
    df = pd.DataFrame.from_records(records)
    return df


def save_dataframe(df: pd.DataFrame, path: str) -> None:
    """Save DataFrame as CSV."""
    df.to_csv(path, index=False)


def fetch_measurements(city: Optional[str] = None,
                       country: Optional[str] = None,
                       parameter: str = "pm25",
                       date_from: Optional[str] = None,
                       date_to: Optional[str] = None,
                       limit: int = 100,
                       max_pages: int = 5,
                       api_key: Optional[str] = None) -> pd.DataFrame:
    """Fetch measurements using the official OpenAQ Python client.

    This helper queries locations matching the given filters, retrieves
    sensors for those locations and then fetches measurement data.
    """

    client = OpenAQ(api_key=api_key)

    param_map = {p.name: p.id for p in client.parameters.list().results}
    param_id = param_map.get(parameter)
    if param_id is None:
        raise ValueError(f"Unknown parameter '{parameter}'")

    loc_resp = client.locations.list(iso=country, limit=1)
    locations = [
        loc for loc in loc_resp.results
        if city is None or (hasattr(loc, "locality") and loc.locality and loc.locality.lower() == city.lower())
    ]

    records: List[dict] = []
    for loc in locations:
        sensors_resp = client.locations.sensors(loc.id)
        sensors = [s for s in sensors_resp.results if s.parameter["id"] == param_id]
        for sensor in sensors:
            page = 1
            while page <= max_pages:
                meas_resp = client.measurements.list(
                    sensor.id,
                    datetime_from=date_from,
                    datetime_to=date_to,
                    page=page,
                    limit=limit,
                )
                for m in meas_resp.results:
                    records.append({
                        "location": loc.name,
                        "city": getattr(loc, "locality", None),
                        "sensor_id": sensor.id,
                        "value": m.value,
                        "unit": sensor.parameter["units"],
                        "datetime": m.period.datetime_from.utc,
                        "coordinates.latitude": (m.coordinates.latitude
                                                 if m.coordinates else loc.coordinates.latitude),
                        "coordinates.longitude": (m.coordinates.longitude
                                                  if m.coordinates else loc.coordinates.longitude),
                    })
                if len(meas_resp.results) < limit:
                    break
                page += 1

    return pd.DataFrame.from_records(records)

