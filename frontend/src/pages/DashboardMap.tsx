import React from 'react'
import { LayersControl } from 'react-leaflet'
import { LeafletMap } from '../components/Map/LeafletMap'
import { IoTSensorsLayer } from '../components/Map/IoTSensorsLayer'
import { VelibStationsLayer } from '../components/Map/VelibStationsLayer'
import { TransitStopsLayer } from '../components/Map/TransitStopsLayer'
import { TrafficDisruptionsLayer } from '../components/Map/TrafficDisruptionsLayer'

const { Overlay } = LayersControl

export const DashboardMap: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto py-6 px-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Carte Interactive - Paris Temps Réel
        </h1>
        <p className="text-gray-600">
          Qualité de l'air, mobilité et perturbations en temps réel
        </p>
      </div>

      {/* Legend */}
      <div className="bg-white p-4 rounded-lg shadow mb-4">
        <h3 className="font-semibold text-sm mb-3 text-gray-700">Légende</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500 border-2 border-white"></div>
            <span>IoT Sensors (Air quality)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500 border-2 border-white"></div>
            <span>Vélib disponible</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-orange-500 border-2 border-white"></div>
            <span>Vélib faible</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500 border-2 border-white"></div>
            <span>Arrêts transport</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500 border-2 border-white flex items-center justify-center text-white text-xs">
              ⚠️
            </div>
            <span>Perturbations</span>
          </div>
        </div>
      </div>

      {/* Interactive Map */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <LeafletMap height="700px">
          <Overlay checked name="Capteurs IoT">
            <IoTSensorsLayer />
          </Overlay>

          <Overlay checked name="Stations Vélib (IDFM)">
            <VelibStationsLayer />
          </Overlay>

          <Overlay name="Arrêts Transport (IDFM)">
            <TransitStopsLayer />
          </Overlay>

          <Overlay checked name="Perturbations Trafic (IDFM)">
            <TrafficDisruptionsLayer />
          </Overlay>
        </LeafletMap>
      </div>

      {/* Info Card */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <span className="text-2xl">ℹ️</span>
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">
              Carte Interactive Multi-couches
            </h4>
            <p className="text-sm text-blue-800">
              Utilisez le contrôle des couches (coin supérieur droit) pour activer/désactiver les différentes données.
              Cliquez sur les markers pour voir les détails.
            </p>
            <ul className="text-sm text-blue-700 mt-2 space-y-1">
              <li>• <strong>Capteurs IoT:</strong> Mesures en temps réel de la qualité de l'air</li>
              <li>• <strong>Vélib:</strong> Disponibilité des vélos en stations (données IDFM)</li>
              <li>• <strong>Transports:</strong> Arrêts métro, RER, bus (données IDFM)</li>
              <li>• <strong>Perturbations:</strong> Alertes trafic actives (données IDFM)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
