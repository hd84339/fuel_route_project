import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv

load_dotenv()

ORS_API_KEY = os.getenv("ORS_API_KEY")

def get_coordinates(place):
    """Converts a string location to [lon, lat] coordinates."""
    url = "https://api.openrouteservice.org/geocode/search"
    params = {
        "api_key": ORS_API_KEY,
        "text": place,
        "size": 1  # We only need the top result
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        
        if not data.get('features'):
            return None
            
        return data['features'][0]['geometry']['coordinates']
    except (requests.exceptions.RequestException, KeyError, IndexError):
        return None

@api_view(['GET'])
def route_api_view(request):
    start_name = request.GET.get('start')
    end_name = request.GET.get('end')

    if not start_name or not end_name:
        return Response({"error": "Please provide both 'start' and 'end' parameters."}, 
                        status=status.HTTP_400_BAD_REQUEST)

    # 1. Geocoding
    start_coords = get_coordinates(start_name)
    end_coords = get_coordinates(end_name)

    if not start_coords or not end_coords:
        return Response({"error": "Could not find one or both locations."}, 
                        status=status.HTTP_404_NOT_FOUND)

    # 2. Routing
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {"coordinates": [start_coords, end_coords]}

    try:
        res = requests.post(url, json=body, headers=headers)
        res.raise_for_status()
        data = res.json()
        
        # ORS distance is returned in meters
        distance_m = data['routes'][0]['summary']['distance']
    except (requests.exceptions.RequestException, KeyError, IndexError):
        return Response({"error": "Failed to calculate route."}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 3. Calculations
    distance_km = distance_m / 1000
    distance_miles = distance_km * 0.621371
    
    # Assuming 10 MPG (miles per gallon) based on your original logic
    fuel_needed = distance_miles / 10

    fuel_prices = [
        {"name": "Station A", "price": 3.5},
        {"name": "Station B", "price": 3.2},
        {"name": "Station C", "price": 3.8},
    ]

    cheapest_station = min(fuel_prices, key=lambda x: x["price"])
    total_cost = fuel_needed * cheapest_station["price"]

    return Response({
        "start": start_name,
        "end": end_name,
        "distance_km": round(distance_km, 2),
        "distance_miles": round(distance_miles, 2),
        "fuel_needed_gallons": round(fuel_needed, 2),
        "cheapest_fuel_price": cheapest_station["price"],
        "estimated_cost": round(total_cost, 2)
    })