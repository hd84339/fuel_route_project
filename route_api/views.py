import os
import requests
import polyline
import json
from pathlib import Path

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv

load_dotenv()

ORS_API_KEY = os.getenv("ORS_API_KEY")

STATIONS_FILE = Path(__file__).resolve().parent / "processed_stations.json"
with open(STATIONS_FILE, 'r') as f:
    ALL_STATIONS = json.load(f)

# -------------------------------
# 1. GEOCODING FUNCTION
# -------------------------------
def get_coordinates(place):
    url = "https://api.openrouteservice.org/geocode/search"
    params = {
        "api_key": ORS_API_KEY,
        "text": place,
        "size": 1
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()

        if not data.get("features"):
            return None

        return data["features"][0]["geometry"]["coordinates"]  # [lon, lat]

    except Exception:
        return None


# -------------------------------
# 2. DISTANCE BETWEEN 2 POINTS
# -------------------------------
def haversine(p1, p2):
    from math import radians, sin, cos, sqrt, atan2

    lat1, lon1 = p1
    lat2, lon2 = p2

    R = 3958.8  # miles

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c


# -------------------------------
# 3. MAIN API
# -------------------------------
@api_view(['GET'])
def route_api_view(request):

    start_name = request.GET.get("start")
    end_name = request.GET.get("end")

    if not start_name or not end_name:
        return Response(
            {"error": "start and end required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # -------------------------------
    # STEP 1: GET COORDINATES
    # -------------------------------
    start_coords = get_coordinates(start_name)
    end_coords = get_coordinates(end_name)

    if not start_coords or not end_coords:
        return Response({"error": "Invalid locations"}, status=404)

    # -------------------------------
    # STEP 2: GET ROUTE
    # -------------------------------
    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [start_coords, end_coords]
    }

    try:
        res = requests.post(url, json=body, headers=headers)
        res.raise_for_status()
        route_data = res.json()

        route = route_data["routes"][0]

        distance_miles = route["summary"]["distance"] * 0.000621371

        # decode full route path
        geometry = route["geometry"]
        route_points = polyline.decode(geometry)

    except Exception as e:
        return Response(
            {"error": f"Route API failed: {str(e)}"},
            status=500
        )

    # -------------------------------
    # STEP 3: MAP STATIONS TO ROUTE
    # -------------------------------
    cumulative_distances = [0.0]
    for i in range(1, len(route_points)):
        dist = haversine(route_points[i-1], route_points[i])
        cumulative_distances.append(cumulative_distances[-1] + dist)

    min_lat = min(p[0] for p in route_points)
    max_lat = max(p[0] for p in route_points)
    min_lon = min(p[1] for p in route_points)
    max_lon = max(p[1] for p in route_points)

    route_stations = []
    for s in ALL_STATIONS:
        if (min_lat - 0.5 <= s['lat'] <= max_lat + 0.5) and \
           (min_lon - 0.5 <= s['lon'] <= max_lon + 0.5):
            closest_dist = float('inf')
            closest_idx = 0
            # Downsample points for fast closest-point search to avoid timeout
            for i in range(0, len(route_points), 25):
                p = route_points[i]
                d_sq = (s['lat'] - p[0])**2 + (s['lon'] - p[1])**2
                if d_sq < closest_dist:
                    closest_dist = d_sq
                    closest_idx = i
            
            true_dist = haversine((s['lat'], s['lon']), route_points[closest_idx])
            if true_dist <= 15: # Within 15 miles of the route
                s_copy = s.copy()
                s_copy['mile'] = cumulative_distances[closest_idx]
                route_stations.append(s_copy)

    # -------------------------------
    # STEP 4: FUEL STATION OPTIMIZATION
    # -------------------------------
    MPG = 10
    MAX_RANGE = 500

    stations = sorted(route_stations, key=lambda x: x["mile"])

    stops = []
    current = 0
    total_cost = 0

    while current + MAX_RANGE < distance_miles:

        reachable = [
            s for s in stations
            if current < s["mile"] <= current + MAX_RANGE
        ]

        if not reachable:
            return Response({"error": f"No fuel station in range after mile {current}"}, status=400)

        best = min(reachable, key=lambda x: x["price"])
        
        fuel_needed = MAX_RANGE / MPG
        stop_cost = fuel_needed * best["price"]
        total_cost += stop_cost

        stops.append({
            "station": best["name"],
            "mile": round(best["mile"], 2),
            "price": best["price"],
            "fuel_needed": round(fuel_needed, 2),
            "lat": best["lat"],
            "lon": best["lon"]
        })

        current = best["mile"]

    # -------------------------------
    # STEP 4: FINAL RESPONSE
    # -------------------------------
    return Response({
        "trip_info": {
            "start": start_name,
            "end": end_name,
            "distance_miles": round(distance_miles, 2)
        },
        "fuel_summary": {
            "total_stops": len(stops),
            "total_cost": round(total_cost, 2)
        },
        "stops": stops,
        "route_geometry": geometry
    })