import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet's default icon assets issue in bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const URGENCY_COLORS = {
  critical: '#dc2626', // red
  high: '#ea580c',     // orange
  medium: '#ca8a04',   // yellow
  low: '#16a34a',      // green
};

export default function MapView({ incidents, onSelectIncident, t }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersLayerRef = useRef(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Initialize Leaflet map if not already initialized
    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [8.5, 4.5], // Center of southern/western Nigeria
        zoom: 7,
        scrollWheelZoom: true,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
      }).addTo(map);

      markersLayerRef.current = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;
    const markersLayer = markersLayerRef.current;

    // Clear previous markers
    markersLayer.clearLayers();

    const validIncidents = incidents.filter((i) => i.lat && i.lng);
    const bounds = [];

    validIncidents.forEach((incident) => {
      const color = URGENCY_COLORS[incident.urgency] || '#64748b';
      const latLng = [incident.lat, incident.lng];
      bounds.push(latLng);

      // Create urgency-colored circular pin
      const marker = L.circleMarker(latLng, {
        radius: 11,
        fillColor: color,
        color: '#ffffff',
        weight: 2.5,
        opacity: 1,
        fillOpacity: 0.9,
      });

      // Build HTML popup
      const popupDiv = document.createElement('div');
      popupDiv.className = 'map-popup-content';
      popupDiv.innerHTML = `
        <div style="font-family: inherit; font-size: 13px;">
          <div style="display: flex; gap: 6px; align-items: center; margin-bottom: 6px;">
            <span style="font-weight: 800; font-size: 11px; background: #e2e8f0; padding: 2px 5px; border-radius: 4px;">#${incident.id}</span>
            <span style="font-weight: 700; font-size: 10px; text-transform: uppercase; background: ${color}20; color: ${color}; padding: 2px 6px; border-radius: 8px;">${incident.urgency}</span>
            <span style="font-weight: 700; font-size: 10px; text-transform: uppercase; background: #f1f5f9; color: #475569; padding: 2px 6px; border-radius: 8px;">${incident.verification_state}</span>
          </div>
          <h4 style="margin: 0 0 6px 0; font-size: 14px; color: #0f172a; line-height: 1.3;">${incident.title}</h4>
          <p style="margin: 0 0 8px 0; color: #64748b; font-size: 12px;">📍 ${incident.location_text}</p>
          <button id="popup-btn-${incident.id}" style="width: 100%; background: #0f172a; color: #fff; border: none; border-radius: 4px; padding: 6px 10px; font-size: 12px; font-weight: 600; cursor: pointer;">
            ${t('btn_view_details')}
          </button>
        </div>
      `;

      // Wire button click handler
      const btn = popupDiv.querySelector(`#popup-btn-${incident.id}`);
      if (btn) {
        btn.addEventListener('click', () => {
          onSelectIncident(incident.id);
        });
      }

      marker.bindPopup(popupDiv);
      markersLayer.addLayer(marker);
    });

    // Auto-fit bounds if we have valid coordinates
    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 13 });
    }

    // Force Leaflet recalculation after DOM render
    setTimeout(() => {
      map.invalidateSize();
    }, 150);

  }, [incidents, onSelectIncident, t]);

  // Clean up map on unmount
  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div className="map-view-wrapper">
      <div className="map-legend">
        <span className="legend-item"><span className="legend-dot dot-critical"></span> {t('urgency_critical')}</span>
        <span className="legend-item"><span className="legend-dot dot-high"></span> {t('urgency_high')}</span>
        <span className="legend-item"><span className="legend-dot dot-medium"></span> {t('urgency_medium')}</span>
        <span className="legend-item"><span className="legend-dot dot-low"></span> {t('urgency_low')}</span>
      </div>
      <div ref={mapContainerRef} className="leaflet-map-container" />
    </div>
  );
}

