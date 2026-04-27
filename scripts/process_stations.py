import csv
import json
import urllib.request

# Download US cities database to map City, State to Lat, Lon
url = "https://raw.githubusercontent.com/kelvins/US-Cities-Database/main/csv/us_cities.csv"
response = urllib.request.urlopen(url)
lines = [l.decode('utf-8') for l in response.readlines()]

cities_coords = {}
reader = csv.reader(lines)
next(reader) # skip header
for row in reader:
    try:
        city = row[3].strip().upper()
        state = row[1].strip().upper()
        lat = float(row[5])
        lon = float(row[6])
        cities_coords[f"{city},{state}"] = (lat, lon)
    except Exception:
        continue

# Now process the stations CSV
processed_stations = []
missing_cities = 0

with open('data/fuel-prices-for-be-assessment.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        if len(row) < 7:
            continue
        try:
            station_id = int(row[0])
            name = row[1].strip()
            address = row[2].strip()
            city = row[3].strip().upper()
            state = row[4].strip().upper()
            price = float(row[6])
            
            key = f"{city},{state}"
            if key in cities_coords:
                lat, lon = cities_coords[key]
                processed_stations.append({
                    "id": station_id,
                    "name": name,
                    "address": address,
                    "city": city,
                    "state": state,
                    "price": price,
                    "lat": lat,
                    "lon": lon
                })
            else:
                missing_cities += 1
        except Exception as e:
            continue

print(f"Successfully processed {len(processed_stations)} stations.")
print(f"Could not map {missing_cities} stations due to missing city data.")

with open('route_api/processed_stations.json', 'w') as f:
    json.dump(processed_stations, f, indent=2)

print("Saved to route_api/processed_stations.json")
