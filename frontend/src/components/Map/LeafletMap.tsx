import React from 'react'
import { MapContainer, TileLayer, LayersControl } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

const { Overlay } = LayersControl

interface LeafletMapProps {
  children?: React.ReactNode
  center?: [number, number]
  zoom?: number
  height?: string
}

export const LeafletMap: React.FC<LeafletMapProps> = ({
  children,
  center = [48.8566, 2.3522], // Paris coordinates
  zoom = 12,
  height = '600px'
}) => {
  return (
    <div style={{ height, width: '100%' }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        {/* Base Map Layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Layer Controls for toggling layers */}
        <LayersControl position="topright">
          {children}
        </LayersControl>
      </MapContainer>
    </div>
  )
}
