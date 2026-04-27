# ⛽ Fuel Route Optimizer

Fuel Route Optimizer is a sophisticated full-stack application designed to minimize travel costs for long-distance trips across the USA. By analyzing route data and real-time fuel prices, it identifies the most cost-effective gas stations along your journey, ensuring you never overpay for fuel.

![Application Preview](https://via.placeholder.com/800x450.png?text=Fuel+Route+Optimizer+Dashboard)

## 🌟 Key Features
- **Smart Routing**: Calculate precise driving directions between any two locations in the USA.
- **Cost Optimization**: An intelligent algorithm selects the cheapest fuel stops based on vehicle range (500 miles) and efficiency (10 MPG).
- **Interactive Mapping**: Powered by Leaflet, the map displays the full route, specific fuel stops, and detailed station information.
- **Data-Driven Insights**: Provides a complete trip summary, including total distance, number of stops, and total estimated fuel cost.

## 🛠️ Tech Stack
- **Frontend**: React (Vite), Leaflet, Axios, Vanilla CSS.
- **Backend**: Django, Django REST Framework.
- **Routing API**: [OpenRouteService](https://openrouteservice.org/) (Directions & Geocoding).
- **Data Processing**: Python scripts for mapping city/state data to geographical coordinates.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js & npm
- [OpenRouteService API Key](https://openrouteservice.org/dev/#/signup)

### Backend Setup
1. **Clone the repository** (if not already local).
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install Python dependencies**:
   ```bash
   pip install django djangorestframework django-cors-headers requests python-dotenv polyline
   ```
4. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   ORS_API_KEY=your_openrouteservice_api_key
   ```
5. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```
6. **Start the API server**:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. **Navigate to the frontend folder**:
   ```bash
   cd frontend
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Launch the development server**:
   ```bash
   npm run dev
   ```

## 📊 Data Processing
The project includes a utility script to process raw fuel price data and map it to GPS coordinates:
```bash
python scripts/process_stations.py
```
This script downloads a US cities database and generates `processed_stations.json` for the API to use.

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Built with ❤️ for efficient travel.*
