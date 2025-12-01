"""
Geolocation module for IP address location lookups.
"""

from typing import TypedDict

import requests


class GeoLocation(TypedDict):
    """Type definition for geolocation data."""

    country: str
    region: str
    city: str


def get_geo(ip: str, timeout: int = 5) -> GeoLocation:
    """
    Get geolocation information for an IP address using ipwhois.app API.

    Args:
        ip: IP address to lookup
        timeout: Request timeout in seconds (default: 5)

    Returns:
        Dictionary with country, region, and city
    """
    try:
        response = requests.get(f"https://ipwhois.app/json/{ip}", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country", "Unknown"),
                "region": data.get("region", "Unknown"),
                "city": data.get("city", "Unknown"),
            }
    except Exception:
        pass

    return {"country": "Unknown", "region": "Unknown", "city": "Unknown"}
