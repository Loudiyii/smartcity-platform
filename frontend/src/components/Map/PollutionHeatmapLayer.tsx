import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'
import { useCurrentAirQuality } from '../../hooks/useAirQuality'
import { useSensors } from '../../hooks/useSensors'

// Extend Leaflet types for heatLayer
declare module 'leaflet' {
  function heatLayer(
    latlngs: [number, number, number][],
    options?: any
  ): L.Layer
}

export const PollutionHeatmapLayer: React.FC = () => {
  const map = useMap()
  const { data: sensors } = useSensors()
  const { data: airQuality } = useCurrentAirQuality('Paris')

  useEffect(() => {
    if (!map || !airQuality) return

    // Get PM2.5 value from current air quality
    const currentPM25 = airQuality.pm25 || 45

    // Create heatmap data points [lat, lon, intensity]
    const heatData: [number, number, number][] = []

    // Add sensor locations with PM2.5 readings
    if (sensors && sensors.length > 0) {
      sensors.forEach((sensor) => {
        const lat = sensor.location?.lat || (sensor.location as any)?.latitude
        const lon = sensor.location?.lon || (sensor.location as any)?.longitude

        if (lat && lon) {
          // Use current PM2.5 value (in real app, would use sensor-specific readings)
          heatData.push([lat, lon, currentPM25 / 100]) // Normalize intensity
        }
      })
    }

    // Add extensive simulated pollution hotspots for Paris
    // Dense grid covering all arrondissements with realistic pollution patterns
    const pollutionHotspots: [number, number, number][] = [
      // VERY HIGH pollution zones (red) - Major traffic arteries and industrial
      [48.8566, 2.3522, 1.0],   // Châtelet-Les Halles (très dense)
      [48.8738, 2.2950, 0.95],  // La Défense (business + autoroutes)
      [48.8584, 2.2945, 0.9],   // Arc de Triomphe (Champs-Élysées trafic)
      [48.8932, 2.3550, 0.95],  // Gare du Nord (pollution gare)
      [48.8442, 2.3736, 0.9],   // Gare de Lyon + Bastille
      [48.8606, 2.3376, 0.85],  // Opéra - Boulevard Haussmann
      [48.8466, 2.3379, 0.9],   // Saint-Germain-des-Prés
      [48.8534, 2.3488, 0.95],  // Louvre - Rivoli (trafic dense)

      // HIGH pollution (orange-red) - Secondary roads, dense urbain
      [48.8584, 2.3944, 0.8],   // Nation - Cours de Vincennes
      [48.8738, 2.3547, 0.8],   // Gare de l'Est
      [48.8350, 2.3200, 0.75],  // Montparnasse
      [48.8650, 2.3700, 0.8],   // Belleville
      [48.8400, 2.3400, 0.75],  // Panthéon - Quartier Latin
      [48.8700, 2.3100, 0.8],   // Batignolles
      [48.8500, 2.3800, 0.75],  // Père Lachaise
      [48.8720, 2.3310, 0.75],  // Gare Saint-Lazare
      [48.8420, 2.3220, 0.7],   // Montparnasse Sud
      [48.8380, 2.3520, 0.75],  // Gobelins - Place d'Italie

      // MEDIUM pollution (yellow-orange) - Residential + some traffic
      [48.8529, 2.3499, 0.6],   // Île de la Cité
      [48.8462, 2.3372, 0.6],   // Luxembourg Gardens area
      [48.8620, 2.3270, 0.65],  // Madeleine
      [48.8480, 2.3550, 0.6],   // Marais
      [48.8570, 2.3350, 0.65],  // Palais Royal
      [48.8410, 2.3620, 0.6],   // Bercy
      [48.8680, 2.3450, 0.6],   // République
      [48.8300, 2.3100, 0.55],  // Parc Montsouris area
      [48.8390, 2.2880, 0.6],   // Porte de Versailles
      [48.8280, 2.3650, 0.6],   // Ivry - périphérie Sud

      // LOWER pollution (yellow-green) - Parks, green spaces
      [48.8656, 2.3212, 0.45],  // Parc Monceau
      [48.8799, 2.3365, 0.4],   // Montmartre (hauteur)
      [48.8275, 2.3690, 0.45],  // Parc Montsouris
      [48.8462, 2.2500, 0.4],   // Bois de Boulogne
      [48.8280, 2.4025, 0.4],   // Bois de Vincennes
      [48.8770, 2.3400, 0.45],  // Buttes-Chaumont
      [48.8330, 2.3750, 0.5],   // Parc de Bercy

      // Additional dense grid for complete coverage
      [48.8600, 2.3400, 0.75],  // Centre Nord
      [48.8550, 2.3300, 0.7],   // Centre Ouest
      [48.8550, 2.3600, 0.75],  // Centre Est
      [48.8450, 2.3400, 0.7],   // Centre Sud
      [48.8750, 2.3300, 0.7],   // Nord-Ouest
      [48.8750, 2.3600, 0.75],  // Nord-Est
      [48.8350, 2.3300, 0.65],  // Sud-Ouest
      [48.8350, 2.3600, 0.7],   // Sud-Est

      // Périphérique (ring road) - HIGH pollution
      [48.8900, 2.3200, 0.85],  // Périph Nord-Ouest
      [48.8900, 2.3700, 0.85],  // Périph Nord-Est
      [48.8200, 2.3200, 0.85],  // Périph Sud-Ouest
      [48.8200, 2.3700, 0.85],  // Périph Sud-Est
      [48.8550, 2.2650, 0.85],  // Périph Ouest
      [48.8550, 2.4100, 0.85],  // Périph Est
    ]

    // Combine sensor data with simulated hotspots
    const allHeatData = [...heatData, ...pollutionHotspots]

    // Create heatmap layer with increased visibility
    const heatLayer = L.heatLayer(allHeatData, {
      radius: 50,        // Increased from 40
      blur: 40,          // Increased from 35
      maxZoom: 14,       // Increased from 13
      max: 0.6,          // Reduced from 1.0 to make colors more saturated
      minOpacity: 0.5,   // Added minimum opacity
      gradient: {
        0.0: '#00ff00',  // Green - low pollution
        0.2: '#ffff00',  // Yellow
        0.4: '#ffa500',  // Orange
        0.6: '#ff6347',  // Tomato red
        0.8: '#ff4500',  // Red-orange
        1.0: '#dc143c'   // Crimson - high pollution
      }
    })

    // Add layer to map
    heatLayer.addTo(map)

    // Cleanup function
    return () => {
      map.removeLayer(heatLayer)
    }
  }, [map, sensors, airQuality])

  return null // This component doesn't render anything visible directly
}
