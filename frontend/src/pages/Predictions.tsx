import React, { useState } from 'react'
import { usePM25Prediction, useTrainModel } from '../hooks/usePredictions'
import { PredictionCard } from '../components/Predictions/PredictionCard'

const CITIES = ['Paris']

export const Predictions: React.FC = () => {
  const [selectedCity, setSelectedCity] = useState('Paris')

  const { data: prediction, isLoading, error, refetch } = usePM25Prediction(selectedCity)
  const trainModel = useTrainModel()

  const handleTrain = async () => {
    try {
      await trainModel.mutateAsync({
        city: selectedCity,
        days: 60,
        n_estimators: 100,
        max_depth: 20
      })
      // Refetch prediction after training
      setTimeout(() => refetch(), 1000)
    } catch (err) {
      console.error('Training failed:', err)
    }
  }

  return (
    <div className="max-w-7xl mx-auto py-6 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Prédictions de Qualité de l'Air
        </h1>
        <p className="text-gray-600">
          Prédictions PM2.5 à J+1 générées par modèle Random Forest
        </p>
      </div>

      {/* City Selector */}
      <div className="mb-6">
        <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-2">
          Sélectionnez une ville
        </label>
        <div className="flex gap-4">
          {CITIES.map((city) => (
            <button
              key={city}
              onClick={() => setSelectedCity(city)}
              className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                selectedCity === city
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-blue-400'
              }`}
            >
              {city}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Chargement de la prédiction...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border-2 border-red-500 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-800 mb-2">
            Erreur de prédiction
          </h3>
          <p className="text-sm text-red-700 mb-4">
            {error.message || 'Impossible de charger la prédiction'}
          </p>
          <p className="text-sm text-red-600 mb-4">
            Le modèle n'a peut-être pas encore été entraîné pour {selectedCity}.
          </p>
          <button
            onClick={handleTrain}
            disabled={trainModel.isPending}
            className="px-6 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {trainModel.isPending ? 'Entraînement...' : `Entraîner le modèle pour ${selectedCity}`}
          </button>
          {trainModel.isError && (
            <p className="mt-2 text-sm text-red-600">
              Erreur d'entraînement: {trainModel.error?.message}
            </p>
          )}
          {trainModel.isSuccess && (
            <div className="mt-4 p-4 bg-green-50 border border-green-500 rounded">
              <p className="text-sm text-green-800 font-semibold">
                {trainModel.data.message}
              </p>
              <p className="text-xs text-green-700 mt-1">
                R² Score: {trainModel.data.metrics.r2.toFixed(3)} |
                MAPE: {trainModel.data.metrics.mape.toFixed(1)}%
              </p>
            </div>
          )}
        </div>
      )}

      {/* Prediction Card */}
      {!isLoading && !error && prediction && (
        <div className="space-y-6">
          <PredictionCard prediction={prediction} />

          {/* Additional Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-start gap-4">
              <div className="text-3xl">ℹ️</div>
              <div>
                <h4 className="font-semibold text-blue-900 mb-2">
                  Comment fonctionnent les prédictions ?
                </h4>
                <ul className="text-sm text-blue-800 space-y-2">
                  <li>
                    <strong>Modèle:</strong> Random Forest entraîné sur 60 jours de données historiques
                  </li>
                  <li>
                    <strong>Features:</strong> Statistiques rolling 7 jours, données météo, patterns temporels
                  </li>
                  <li>
                    <strong>Prédiction:</strong> PM2.5 concentration 24 heures à l'avance (J+1)
                  </li>
                  <li>
                    <strong>Confiance:</strong> Calculée à partir du MAPE du modèle (1 - MAPE/100)
                  </li>
                  <li>
                    <strong>Intervalle:</strong> Utilise le RMSE comme approximation de l'écart-type
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Retrain Button */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Réentraîner le modèle
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Réentraînez le modèle avec les données les plus récentes pour améliorer la précision.
              L'entraînement prend environ 30-60 secondes.
            </p>
            <button
              onClick={handleTrain}
              disabled={trainModel.isPending}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {trainModel.isPending ? 'Entraînement en cours...' : 'Réentraîner'}
            </button>
            {trainModel.isSuccess && (
              <div className="mt-4 p-4 bg-green-50 border border-green-500 rounded">
                <p className="text-sm text-green-800 font-semibold">
                  {trainModel.data.message}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
