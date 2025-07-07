from typing import Dict, Any, Optional, List
import googlemaps
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class LocationService:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
    
    async def validate_and_geocode(self, address: str) -> Dict[str, Any]:
        """Validate and geocode an address using Google Maps."""
        try:
            geocode_result = self.gmaps.geocode(address)
            if not geocode_result:
                raise ValueError(f"Could not geocode address: {address}")
            
            location = geocode_result[0]["geometry"]["location"]
            return {
                "address": address,
                "latitude": location["lat"],
                "longitude": location["lng"],
                "formatted_address": geocode_result[0]["formatted_address"]
            }
        except Exception as e:
            raise ValueError(f"Error geocoding address: {str(e)}")
    
    async def calculate_route(self, pickup: Dict[str, Any], dropoff: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate route between two points using Google Maps."""
        try:
            directions = self.gmaps.directions(
                (pickup["latitude"], pickup["longitude"]),
                (dropoff["latitude"], dropoff["longitude"]),
                mode="driving"
            )
            
            if not directions:
                raise ValueError("No route found between points")
            
            route = directions[0]["legs"][0]
            return {
                "duration": route["duration"]["value"],  # in seconds
                "distance": route["distance"]["value"],  # in meters
                "polyline": directions[0]["overview_polyline"]["points"]
            }
        except Exception as e:
            raise ValueError(f"Error calculating route: {str(e)}")
    
    async def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Get detailed information about a place."""
        try:
            place_details = self.gmaps.place(place_id, fields=[
                "name", "formatted_address", "geometry", "rating", "opening_hours"
            ])
            return place_details["result"]
        except Exception as e:
            raise ValueError(f"Error getting place details: {str(e)}")
    
    async def search_nearby_places(self, location: Dict[str, float], radius: int = 1000) -> List[Dict[str, Any]]:
        """Search for nearby places."""
        try:
            places = self.gmaps.places_nearby(
                location=(location["latitude"], location["longitude"]),
                radius=radius
            )
            return places.get("results", [])
        except Exception as e:
            raise ValueError(f"Error searching nearby places: {str(e)}")
    
    async def get_autocomplete_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Get address autocomplete suggestions."""
        try:
            suggestions = self.gmaps.places_autocomplete(
                query,
                types="address"
            )
            return suggestions
        except Exception as e:
            raise ValueError(f"Error getting autocomplete suggestions: {str(e)}") 