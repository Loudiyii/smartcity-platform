# Scripts d'initialisation et simulation

## 🎯 Objectif

Ces scripts permettent de :
1. **Enregistrer les capteurs IoT** dans Supabase avec leurs coordonnées GPS
2. **Simuler l'envoi de données** depuis ces capteurs vers l'API en production

Ceci est **nécessaire** pour que l'endpoint `/api/v1/mobility/spatial-pollution-analysis` fonctionne.

---

## 📋 Prérequis

1. Variables d'environnement configurées dans `backend/.env` :
   ```bash
   SUPABASE_URL=https://vnznhsbjqxufvhasotid.supabase.co
   SUPABASE_SERVICE_KEY=your_service_key
   ```

2. Dépendances installées :
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

---

## 🚀 Étape 1 : Initialiser les métadonnées des capteurs

Cette étape enregistre 5 capteurs IoT dans la table `sensor_metadata` avec leurs coordonnées GPS.

```bash
cd backend
python scripts/init_sensor_metadata.py
```

**Résultat attendu :**
```
✅ SENSOR_001: Registered at (48.8566, 2.3522)
✅ SENSOR_002: Registered at (48.8738, 2.2950)
✅ SENSOR_003: Registered at (48.8414, 2.3209)
✅ SENSOR_004: Registered at (48.8467, 2.3775)
✅ SENSOR_005: Registered at (48.8656, 2.2879)
```

**Capteurs enregistrés :**
| ID | Nom | Localisation | Coordonnées |
|----|-----|--------------|-------------|
| SENSOR_001 | Paris Centre | Near Notre-Dame | 48.8566, 2.3522 |
| SENSOR_002 | Paris Nord | Near Gare du Nord | 48.8738, 2.2950 |
| SENSOR_003 | Paris Sud | Near Place d'Italie | 48.8414, 2.3209 |
| SENSOR_004 | Paris Est | Near Gare de Lyon | 48.8467, 2.3775 |
| SENSOR_005 | Paris Ouest | Near Arc de Triomphe | 48.8656, 2.2879 |

---

## 📡 Étape 2 : Lancer la simulation IoT

Cette étape lance 5 capteurs qui envoient des mesures de pollution toutes les **15 minutes** vers l'API en production.

```bash
cd backend
python scripts/run_iot_simulation.py
```

**Que fait ce script ?**
- Envoie des mesures PM2.5, PM10, NO2 toutes les 15 minutes
- Simule des variations réalistes (heures de pointe, nuit, pics aléatoires)
- Pointe vers l'API Railway : `https://smartcity-platform-production.up.railway.app`

**Exemple de sortie :**
```
🚀 Starting sensors...

✅ [SENSOR_001] PM2.5=25.4, PM10=38.1 | Total sent: 1
✅ [SENSOR_002] PM2.5=31.2, PM10=46.8 | Total sent: 1
✅ [SENSOR_003] PM2.5=22.7, PM10=34.1 | Total sent: 1
...

✨ All sensors started. Press Ctrl+C to stop.
```

**⚠️ Important :**
- Le script doit **rester actif** pour continuer à envoyer des données
- Il faut au moins **24 heures de données** pour que l'analyse spatiale soit pertinente
- Vous pouvez le lancer en arrière-plan :
  ```bash
  nohup python scripts/run_iot_simulation.py &
  ```

---

## 🧪 Étape 3 : Tester l'endpoint d'analyse spatiale

Après **24 heures** de simulation (ou au moins 5 mesures par capteur), testez l'endpoint :

```bash
curl "https://smartcity-platform-production.up.railway.app/api/v1/mobility/spatial-pollution-analysis?hours_back=24"
```

**Réponse attendue (exemple) :**
```json
{
  "status": "success",
  "analysis_period": "24h",
  "near_stops": {
    "avg_pm25": 28.5,
    "count": 3,
    "sensors": ["SENSOR_001", "SENSOR_004"]
  },
  "far_from_stops": {
    "avg_pm25": 22.1,
    "count": 2,
    "sensors": ["SENSOR_003", "SENSOR_005"]
  },
  "difference": {
    "pm25_delta": 6.4,
    "percentage": 28.9,
    "is_significant": true
  },
  "conclusion": "La pollution est 28.9% plus élevée près des arrêts de transport",
  "recommendation": "Installer des zones à faibles émissions autour des hubs de transport"
}
```

---

## 🔍 Vérification des données

### Vérifier les capteurs enregistrés
Requête SQL Supabase :
```sql
SELECT * FROM sensor_metadata WHERE sensor_type = 'air_quality';
```

### Vérifier les mesures reçues
Requête SQL Supabase :
```sql
SELECT
  source,
  COUNT(*) as measurement_count,
  AVG(pm25) as avg_pm25,
  MIN(timestamp) as first_measurement,
  MAX(timestamp) as last_measurement
FROM air_quality_measurements
WHERE source LIKE 'SENSOR_%'
GROUP BY source
ORDER BY source;
```

---

## 🛠️ Dépannage

### Erreur "Table sensor_metadata doesn't exist"
Créer la table dans Supabase :
```sql
CREATE TABLE IF NOT EXISTS sensor_metadata (
  id BIGSERIAL PRIMARY KEY,
  sensor_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  latitude DOUBLE PRECISION NOT NULL,
  longitude DOUBLE PRECISION NOT NULL,
  location_description TEXT,
  sensor_type TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  installed_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Erreur "Connection refused" lors de la simulation
Vérifier que l'API Railway est bien accessible :
```bash
curl https://smartcity-platform-production.up.railway.app/health
```

### "Pas assez de mesures de capteurs" après 24h
Vérifier que le simulateur est toujours actif et que les mesures arrivent bien dans Supabase.

---

## 📊 Données générées

Avec 5 capteurs envoyant des mesures toutes les 15 minutes :
- **Par heure :** 5 × 4 = 20 mesures
- **Par jour :** 20 × 24 = 480 mesures
- **Par semaine :** 480 × 7 = 3 360 mesures

**Stockage estimé :** ~200 Ko par jour
