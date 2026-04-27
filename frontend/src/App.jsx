import { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import polyline from '@mapbox/polyline';
import 'leaflet/dist/leaflet.css';
import './index.css';

// Fix for default marker icons in Leaflet
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// Custom red icon for fuel stops
const redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Component to handle map bounds
const MapBounds = ({ routePoints }) => {
  const map = useMap();
  useEffect(() => {
    if (routePoints && routePoints.length > 0) {
      map.fitBounds(routePoints, { padding: [50, 50] });
    }
  }, [routePoints, map]);
  return null;
};

function App() {
  const [start, setStart] = useState('New York');
  const [end, setEnd] = useState('Los Angeles');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);
  const [routePoints, setRoutePoints] = useState([]);

  const generateRoute = async () => {
    if (!start || !end) {
      setError('Please enter both start and end locations.');
      return;
    }
    
    setLoading(true);
    setError('');
    setData(null);
    setRoutePoints([]);

    try {
      const response = await axios.get(`http://127.0.0.1:8001/api/route/?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
      
      const routeData = response.data;
      setData(routeData);
      
      // Decode polyline string to array of [lat, lon] coordinates
      const decoded = polyline.decode(routeData.route_geometry);
      setRoutePoints(decoded);
      
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to fetch route. Make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  // Generate default route on load
  useEffect(() => {
    generateRoute();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="app-container">
      {/* Left Panel */}
      <div className="left-panel">
        <div className="header">
          <h1>Fuel Route Optimizer</h1>
          <p>Find the cheapest fuel stops across the country</p>
        </div>

        <div className="input-group">
          <label>Start Location</label>
          <input 
            type="text" 
            value={start} 
            onChange={(e) => setStart(e.target.value)} 
            placeholder="e.g. New York"
          />
        </div>

        <div className="input-group">
          <label>End Location</label>
          <input 
            type="text" 
            value={end} 
            onChange={(e) => setEnd(e.target.value)} 
            placeholder="e.g. Los Angeles"
          />
        </div>

        <button 
          className="generate-btn" 
          onClick={generateRoute}
          disabled={loading}
        >
          {loading ? 'Calculating Route...' : 'Generate Route'}
        </button>

        {error && <div className="error-message">{error}</div>}

        {data && (
          <div className="summary-card">
            <h2>Trip Summary</h2>
            <div className="summary-grid">
              <div className="summary-item full-width">
                <span className="label">Total Distance</span>
                <span className="value">{data.trip_info.distance_miles.toLocaleString()} miles</span>
              </div>
              <div className="summary-item">
                <span className="label">Fuel Stops</span>
                <span className="value">{data.fuel_summary.total_stops}</span>
              </div>
              <div className="summary-item">
                <span className="label">Total Cost</span>
                <span className="value">${data.fuel_summary.total_cost.toLocaleString()}</span>
              </div>
              <div className="summary-item">
                <span className="label">MPG</span>
                <span className="value">10.0</span>
              </div>
              <div className="summary-item">
                <span className="label">Max Range</span>
                <span className="value">500 miles</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Right Panel */}
      <div className="right-panel">
        {loading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
          </div>
        )}
        <MapContainer 
          center={[39.8283, -98.5795]} 
          zoom={4} 
          zoomControl={false}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {routePoints.length > 0 && (
            <>
              <MapBounds routePoints={routePoints} />
              <Polyline 
                positions={routePoints} 
                pathOptions={{ color: '#3b82f6', weight: 4, opacity: 0.7 }} 
              />
              
              {/* Plot Fuel Stops */}
              {data && data.stops.map((stop, index) => (
                <Marker 
                  key={index} 
                  position={[stop.lat, stop.lon]}
                  icon={redIcon}
                >
                  <Popup>
                    <strong>{stop.station}</strong><br/>
                    Price: ${stop.price}/gal<br/>
                    Mile Marker: {stop.mile}
                  </Popup>
                </Marker>
              ))}
              
              {/* Start and End Markers */}
              <Marker position={routePoints[0]}>
                <Popup><strong>Start:</strong> {data?.trip_info?.start}</Popup>
              </Marker>
              <Marker position={routePoints[routePoints.length - 1]}>
                <Popup><strong>End:</strong> {data?.trip_info?.end}</Popup>
              </Marker>
            </>
          )}
        </MapContainer>
      </div>
    </div>
  );
}

export default App;
