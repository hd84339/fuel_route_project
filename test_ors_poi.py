import os
import requests
from dotenv import load_dotenv

load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")

url = 'https://api.openrouteservice.org/pois'
headers = {
    'Authorization': ORS_API_KEY,
    'Content-Type': 'application/json'
}
body = {
    'request': 'pois',
    'geometry': {
        'geojson': {
            'type': 'Point',
            'coordinates': [8.681495, 49.41461]
        },
        'buffer': 2000
    },
    'limit': 2,
    'filters': {
        'category_group_ids': [580]
    }
}
res = requests.post(url, json=body, headers=headers)
print(res.json())
