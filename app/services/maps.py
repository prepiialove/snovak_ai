import googlemaps
from app.core.config import settings
from typing import Optional, Tuple

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

def get_coordinates_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Geocodes an address and returns latitude and longitude.
    """
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
    except Exception as e:
        print(f"Error geocoding address '{address}': {e}")
    
    return None