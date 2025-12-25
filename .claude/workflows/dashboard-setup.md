# Workflow: Dashboard Setup (Basic)

## Objectif
Créer l'interface dashboard temps réel avec KPIs et graphiques (Qualité Air + Mobilité).

## Référence
- **User Stories:** US-004, US-005, US-006 (voir `docs/fonctionnel.md`)
- **Ancien Prompt:** `.prompts/F05-basic-dashboard-UPDATED.md` (référence)
- **Skills Utilisés:** `frontend-dashboard`, `backend-api`

## Prérequis
- ✅ Backend FastAPI démarré
- ✅ Base de données Supabase configurée
- ✅ Frontend React initialisé
- ✅ APIs mobilité (F02b, F02c) disponibles

## Architecture Cible

```
Dashboard Page
├── Section Qualité Air
│   ├── KPI Card: PM2.5
│   ├── KPI Card: PM10
│   ├── KPI Card: NO2
│   └── Chart.js: Évolution 24h
│
└── Section Mobilité
    ├── KPI Card: Perturbations actives
    ├── KPI Card: Disponibilité Vélib
    ├── KPI Card: Prochains passages
    ├── Chart.js: Vélib 24h
    └── Chart.js: Retards transport
```

---

## Étape 1: Créer la Page Dashboard

### 1.1 Créer le composant page

**Skill utilisé:** `frontend-dashboard/SKILL.md` section "React Component Structure"

```bash
# Créer le fichier
frontend/src/pages/Dashboard.tsx
```

**Code:**
```typescript
// frontend/src/pages/Dashboard.tsx
import React from 'react';
import { AirQualitySection } from '../components/Dashboard/AirQualitySection';
import { MobilitySection } from '../components/Dashboard/MobilitySection';

export const Dashboard: React.FC = () => {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">
        Smart City Dashboard
      </h1>

      {/* Section Qualité Air */}
      <AirQualitySection />

      {/* Section Mobilité */}
      <MobilitySection />
    </div>
  );
};
```

### 1.2 Ajouter la route

**Skill utilisé:** `frontend-dashboard/SKILL.md` section "React Router Configuration"

```typescript
// frontend/src/router.tsx
import { Dashboard } from './pages/Dashboard';

// Ajouter dans le router:
{
  path: '/dashboard',
  element: <Dashboard />
}
```

---

## Étape 2: Créer les Composants KPI

### 2.1 Créer le composant KPICard réutilisable

**Command:** `/create-component`

**Prompt suggéré:**
```
Crée un composant KPICard avec:
- Props: title, value, unit, severity, trend
- Severity colors: good (green), moderate (yellow), poor (orange), unhealthy (red)
- Optionnel: icône de tendance (up/down)
- Style: Tailwind CSS
```

**Référence code:** Voir `frontend-dashboard/SKILL.md` section "React Component Structure" → exemple KPICard

### 2.2 Créer la section Air Quality

```typescript
// frontend/src/components/Dashboard/AirQualitySection.tsx
import React from 'react';
import { KPICard } from '../UI/KPICard';
import { AirQualityChart } from '../Charts/AirQualityChart';
import { useCurrentAirQuality } from '../../hooks/useAirQuality';

export const AirQualitySection: React.FC = () => {
  const { data, isLoading, error } = useCurrentAirQuality('paris');

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message="Erreur chargement données" />;

  return (
    <section className="mb-12">
      <h2 className="text-2xl font-semibold mb-6">Qualité de l'Air</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <KPICard
          title="PM2.5"
          value={data?.pm25 || 0}
          unit="μg/m³"
          severity={getPM25Severity(data?.pm25)}
        />
        <KPICard
          title="PM10"
          value={data?.pm10 || 0}
          unit="μg/m³"
          severity={getPM10Severity(data?.pm10)}
        />
        <KPICard
          title="NO2"
          value={data?.no2 || 0}
          unit="μg/m³"
          severity={getNO2Severity(data?.no2)}
        />
      </div>

      {/* Chart */}
      <AirQualityChart />
    </section>
  );
};
```

---

## Étape 3: Créer le Hook de Données

### 3.1 Hook pour Air Quality

**Skill utilisé:** `frontend-dashboard/SKILL.md` section "Data Fetching with TanStack Query"

```typescript
// frontend/src/hooks/useAirQuality.ts
import { useQuery } from '@tanstack/react-query';
import { airQualityService } from '../services/airQualityService';

export const useCurrentAirQuality = (city: string) => {
  return useQuery({
    queryKey: ['airQuality', 'current', city],
    queryFn: () => airQualityService.getCurrent(city),
    refetchInterval: 5 * 60 * 1000, // 5 minutes
    staleTime: 2 * 60 * 1000,
  });
};

export const useAirQualityHistory = (city: string) => {
  return useQuery({
    queryKey: ['airQuality', 'history', city],
    queryFn: () => airQualityService.getHistory(city, undefined, undefined, 24),
  });
};
```

---

## Étape 4: Créer les Graphiques Chart.js

### 4.1 Graphique Air Quality

**Skill utilisé:** `frontend-dashboard/SKILL.md` section "Chart.js Integration"

```typescript
// frontend/src/components/Charts/AirQualityChart.tsx
import React from 'react';
import { Line } from 'react-chartjs-2';
import { useAirQualityHistory } from '../../hooks/useAirQuality';

export const AirQualityChart: React.FC = () => {
  const { data: history } = useAirQualityHistory('paris');

  const chartData = {
    labels: history?.map(d => new Date(d.timestamp).toLocaleTimeString()) || [],
    datasets: [
      {
        label: 'PM2.5',
        data: history?.map(d => d.pm25) || [],
        borderColor: 'rgb(59, 130, 246)', // blue
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
      },
      {
        label: 'PM10',
        data: history?.map(d => d.pm10) || [],
        borderColor: 'rgb(239, 68, 68)', // red
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
      },
      {
        label: 'NO2',
        data: history?.map(d => d.no2) || [],
        borderColor: 'rgb(251, 146, 60)', // orange
        backgroundColor: 'rgba(251, 146, 60, 0.1)',
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Évolution Qualité Air (24h)',
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <Line data={chartData} options={options} />
    </div>
  );
};
```

### 4.2 Graphique Vélib

Similaire au graphique Air Quality, mais avec:
```typescript
// Utilise hook useMobility (à créer)
const { data } = useVelibHistory(stationId);

// 2 datasets:
// - Vélos disponibles (vert)
// - Places disponibles (bleu)
```

---

## Étape 5: Section Mobilité

### 5.1 Créer le composant MobilitySection

**Structure similaire à AirQualitySection:**

```typescript
// frontend/src/components/Dashboard/MobilitySection.tsx
export const MobilitySection: React.FC = () => {
  const { data: disruptions } = useActiveDisruptions();
  const { data: velib } = useVelibStats();
  const { data: transit } = useTransitDepartures();

  return (
    <section>
      <h2 className="text-2xl font-semibold mb-6">Mobilité</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <KPICard
          title="Perturbations"
          value={disruptions?.length || 0}
          unit="actives"
          severity={disruptions?.length > 5 ? 'poor' : 'good'}
        />
        <KPICard
          title="Vélib Dispo"
          value={velib?.availabilityPercent || 0}
          unit="%"
          severity={velib?.availabilityPercent > 70 ? 'good' : 'moderate'}
        />
        <KPICard
          title="Prochains Passages"
          value={transit?.departuresCount || 0}
          unit="< 10min"
          severity="good"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <VelibChart />
        <TransitDelaysChart />
      </div>
    </section>
  );
};
```

---

## Étape 6: Backend API Endpoints (si manquants)

### 6.1 Vérifier les endpoints requis

**Skill utilisé:** `backend-api/SKILL.md`

**Endpoints nécessaires:**
```
GET /api/v1/air-quality/current?city=paris
GET /api/v1/air-quality/history?city=paris&limit=24
GET /api/v1/mobility/traffic-disruptions/active
GET /api/v1/mobility/velib/history/{station_id}?hours=24
GET /api/v1/realtime-transport/departures/{stop_id}?limit=50
```

### 6.2 Créer endpoints manquants

**Command:** `/add-api-route`

Exemple pour mobility disruptions:
```python
# backend/app/api/v1/mobility.py
@router.get("/traffic-disruptions/active")
async def get_active_disruptions():
    # Récupérer depuis Supabase
    result = supabase.table('traffic_disruptions') \
        .select('*') \
        .eq('status', 'active') \
        .execute()
    return result.data
```

---

## Étape 7: Auto-refresh

### 7.1 Configuration TanStack Query

**Déjà configuré dans les hooks avec:**
```typescript
refetchInterval: 5 * 60 * 1000  // 5 minutes
```

### 7.2 Indicateur de dernière mise à jour

```typescript
// Ajouter dans Dashboard.tsx
const lastUpdate = new Date().toLocaleTimeString();

<p className="text-sm text-gray-500">
  Dernière mise à jour: {lastUpdate}
</p>
```

---

## Critères d'Acceptation

### Tests Fonctionnels
- [ ] Page `/dashboard` accessible
- [ ] 3 KPI Air Quality affichent valeurs réelles
- [ ] 3+ KPI Mobilité affichent valeurs réelles
- [ ] Graphique Air Quality affiche évolution 24h
- [ ] Graphique Vélib affiche disponibilité
- [ ] Auto-refresh fonctionne (5 min)
- [ ] Interface responsive (mobile + desktop)
- [ ] Loading states affichés pendant fetch
- [ ] Error states gérés proprement

### Tests Techniques
```bash
# Frontend
npm run lint
npm run type-check

# Vérifier les appels API
# Ouvrir DevTools → Network → vérifier requêtes
```

---

## Dépannage

### Problème: Graphiques ne s'affichent pas
**Solution:**
1. Vérifier que Chart.js est enregistré (voir `frontend-dashboard/SKILL.md`)
2. Vérifier format des données
3. Inspecter console pour erreurs

### Problème: Données non à jour
**Solution:**
1. Vérifier `refetchInterval` dans hooks
2. Vérifier connexion API backend
3. Vérifier données en DB

### Problème: Layout cassé sur mobile
**Solution:**
1. Utiliser `grid-cols-1 md:grid-cols-3` (Tailwind responsive)
2. Tester avec DevTools responsive mode

---

## Prochaines Étapes

Après avoir terminé ce workflow:
1. Tester complètement le dashboard
2. Passer au workflow suivant: `advanced-features.md`
3. Ou implémenter: `alerts-implementation.md`

---

**Skill References:**
- 📘 `frontend-dashboard/SKILL.md` - Patterns React
- 📘 `backend-api/SKILL.md` - Patterns API
- 📘 `database-schema/SKILL.md` - Queries DB

**Old Prompt Reference:**
- 📄 `.prompts/F05-basic-dashboard-UPDATED.md` (historique)
