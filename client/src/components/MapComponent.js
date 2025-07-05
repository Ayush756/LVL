import React from 'react';
// Import Marker and Popup
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
function MapEventsHandler({ onMapClick }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng);
    },
  });
  return null;
}

function MapComponent({ onMapClick, clickedCoords }) {
  // Center the map on Nepal
  const initialPosition = [28.3949, 84.1240]; 

  // Define the bounding box for Nepal to restrict panning
  const nepalBounds = [
    [26.347, 80.058], // Southwest corner
    [30.447, 88.201], // Northeast corner
  ];

  return (
    <div className="map-container">
      <MapContainer 
        center={initialPosition} 
        zoom={7} 
        className="leaflet-container"
        maxBounds={nepalBounds} // Restrict map panning
        minZoom={7}             // Prevent zooming out too far
      >
        <TileLayer
          attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapEventsHandler onMapClick={onMapClick} />
        
        {/* --- ADD MARKER --- */}
        {/* This will only render the marker if clickedCoords is not null */}
        {clickedCoords && (
          <Marker position={clickedCoords}>
            <Popup>
              Selected Location <br /> 
              Lat: {clickedCoords.lat.toFixed(4)}, Lng: {clickedCoords.lng.toFixed(4)}
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconUrl: markerIcon,
    iconRetinaUrl: markerIcon2x,
    shadowUrl: markerShadow,
});
export default MapComponent;