import React from 'react';
import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css'; // This import is crucial

function MapEventsHandler({ onMapClick }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng);
    },
  });
  return null;
}

function MapComponent({ onMapClick }) {
  const initialPosition = [51.505, -0.09];

  return (
    <div className="map-container">
      <MapContainer center={initialPosition} zoom={13} className="leaflet-container">
        <TileLayer
          attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapEventsHandler onMapClick={onMapClick} />
      </MapContainer>
    </div>
  );
}

export default MapComponent;