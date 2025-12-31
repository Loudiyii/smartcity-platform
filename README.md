# Plateforme Smart City - Surveillance de la Qualité de l'Air et de la Mobilité

Une plateforme en temps réel pour surveiller la qualité de l'air et la mobilité urbaine à Paris. Ce projet utilise des capteurs IoT, des API externes, des prédictions par apprentissage automatique et des cartes interactives pour suivre les niveaux de pollution et les données de mobilité.

## Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Stack technologique](#stack-technologique)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Capteurs IoT](#capteurs-iot)
- [Documentation API](#documentation-api)
- [Déploiement](#déploiement)
- [URLs de production](#urls-de-production)
- [Contribution](#contribution)
- [Licence](#licence)

---

## Vue d'ensemble

Cette plateforme surveille la qualité de l'air à Paris et prédit les niveaux de pollution. Elle combine :

- Surveillance en temps réel de la qualité de l'air à partir de 5 capteurs IoT
- Prédictions de pollution sur 24 heures utilisant l'apprentissage automatique
- Analyse des corrélations entre météo, trafic et qualité de l'air
- Alertes lorsque la pollution dépasse les niveaux sûrs
- Cartes interactives avec heatmaps et données de mobilité
- Stations Vélib, perturbations de trafic et informations de transport
- Génération de rapports PDF

Construit entre le 18 et le 31 décembre 2024 comme projet étudiant.

---

## Fonctionnalités

### Surveillance en temps réel
- 5 capteurs IoT mesurant PM2.5, PM10 et NO2
- Données collectées toutes les 15 minutes
- Tableau de bord en direct affichant les niveaux de pollution actuels
- Données historiques pour l'analyse des tendances

### Prédictions par apprentissage automatique
- Modèle Random Forest prédisant PM2.5 pour les prochaines 24 heures
- Auto-entraînement au démarrage si le modèle n'existe pas
- Performance : R² > 0.7, MAPE < 30%
- Affiche les scores de confiance pour les prédictions
- Analyse de l'importance des caractéristiques

### Cartographie interactive
- Cartes Leaflet avec heatmaps de pollution
- Emplacements des capteurs IoT avec lectures en temps réel
- Plus de 1000 stations Vélib avec disponibilité des vélos
- Perturbations de trafic depuis l'API IDFM
  - 577 perturbations actives en temps réel
  - Parser personnalisé pour le format datetime IDFM
  - Filtrage par gravité (info, medium, high, critical)
- Arrêts de transport avec horaires de départ
- Analyse spatiale de la pollution avec krigeage

### Analytique
- Graphiques de corrélation pollution vs météo
- Détection d'anomalies (Z-score et Isolation Forest)
  - S'exécute automatiquement toutes les 30 minutes en production
  - Enregistre les anomalies high/critical dans les alertes
  - Surveille les pics de pollution inhabituels
- Analyse de patterns (horaire, quotidien, hebdomadaire)
- Impact de la mobilité sur la qualité de l'air
- Plages de temps personnalisables

### Authentification
- Pages publiques (Dashboard, Map, Predictions, Mobility) - pas de connexion requise
- Pages protégées (Analytics, Reports) - connexion requise
- Supabase Auth pour la gestion des utilisateurs
- Tokens JWT pour l'accès API
- Inscription email/mot de passe avec vérification
- Réinitialisation du mot de passe par email
- Gestion des sessions avec auto-refresh
- Row-level security sur la base de données
- Flux testé : inscription, connexion, contrôle d'accès, déconnexion

### Alertes
- Surveille les seuils PM2.5, PM10, NO2
- Notifications par email lorsque les limites sont dépassées
- Alertes d'anomalies pour les pics de pollution
- Détection des capteurs hors ligne
- Niveaux de gravité (low, medium, high, critical)

### Rapports
- Génération PDF avec graphiques et statistiques
- Périodes personnalisables (daily, weekly, monthly)
- Export de données en plusieurs formats

---

## Stack technologique

### Backend
- Python 3.11+ - langage principal
- FastAPI 0.109.0 - REST API
- Uvicorn 0.27.0 - serveur web
- Supabase 2.10.0 - base de données & auth
- Scikit-learn 1.3.2 - modèles ML
- Pandas 2.1.4 - traitement de données
- NumPy 1.26.3 - calculs
- HTTPX 0.27.0 - requêtes HTTP
- Pydantic 2.5.3 - validation
- ReportLab 4.0.8 - rapports PDF
- Matplotlib 3.8.2 - graphiques
- APScheduler 3.10.4 - tâches planifiées

### Frontend
- React 18.2.0 - framework UI
- TypeScript 5.3.3 - JavaScript typé
- Vite 5.0.8 - outil de build
- TanStack Query 5.13.0 - récupération de données
- Zustand 4.4.7 - gestion d'état
- React Router 6.30.2 - routage
- Leaflet 1.9.4 - cartes
- Leaflet.heat 0.2.0 - heatmaps
- Chart.js 4.4.0 - graphiques
- Axios 1.6.2 - client HTTP
- Tailwind CSS 3.3.6 - styling
- Lucide React 0.294.0 - icônes
- React Hook Form 7.48.2 - formulaires
- Zod 3.22.4 - validation

### Base de données
- PostgreSQL 17
- Supabase Cloud (PostgreSQL managé + Auth)

### Déploiement
- Railway - hébergement backend
- Vercel - hébergement frontend
- Supabase Cloud - base de données
- IDFM APIs - données de mobilité

---

## Architecture

### Fonctionnement

```
Frontend (React) → Backend (FastAPI) → Base de données (PostgreSQL)
     ↓                    ↓                      ↓
Dashboard/Map        Routes API            air_quality_meas
Analytics         Couche Service          predictions
Reports           Modèles ML              alerts
                  API externes            weather_data
```

### Flux de données

1. Les capteurs IoT génèrent des mesures toutes les 15 minutes → POST vers `/api/v1/air-quality/measurements`
2. Les modèles ML s'auto-entraînent au démarrage → prédisent la pollution sur 24h → stockent dans la base de données
3. Les API IDFM récupèrent les données de mobilité à la demande → retournent au frontend
4. Le frontend interroge le backend via REST API → affiche dans dashboard/cartes/graphiques
5. Le worker en arrière-plan surveille les seuils → envoie des alertes par email

### Tâches en arrière-plan (Production)

1. Simulateur de capteurs IoT (continu)
   - 5 capteurs générant des données PM2.5, PM10, NO2
   - Intervalles de 15 minutes
   - Auto-enregistrement dans la table sensor_metadata

2. Détection d'anomalies (toutes les 30 minutes)
   - Algorithmes Z-score et Isolation Forest
   - Analyse des dernières 24 heures
   - Enregistre les anomalies high/critical dans la table alerts

---

## Installation

### Prérequis

- Python 3.11+
- Node.js 18+
- npm ou yarn
- Git
- Compte Supabase (le tier gratuit fonctionne)

### Configuration du Backend

1. Cloner le repo
   ```bash
   git clone https://github.com/yourusername/smartcity.git
   cd smartcity/backend
   ```

2. Créer un environnement virtuel
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. Installer les dépendances
   ```bash
   pip install -r requirements.txt
   ```

4. Créer un fichier `.env` dans le répertoire `backend/` :
   ```env
   # Configuration Supabase
   SUPABASE_URL=https://vnznhsbjqxufvhasotid.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key

   # API externes
   WEATHERAPI_KEY=your_weatherapi_key
   AQICN_API_TOKEN=your_aqicn_token
   IDFM_API_KEY=your_idfm_api_key

   # Sécurité
   SECRET_KEY=your_secret_key_here_min_32_chars
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60

   # Application
   ENVIRONMENT=development
   PORT=8080
   DEBUG=true

   # CORS
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

   # SMTP (pour les alertes email)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ALERT_RECIPIENTS=manager@example.com,admin@example.com
   ```

5. Configurer la base de données
   - Aller sur https://supabase.com et créer un projet
   - Ouvrir Supabase SQL Editor
   - Copier le contenu de `backend/database/schema.sql`
   - Coller et exécuter pour créer les tables
   - Aller dans Settings → API et copier vos clés
   - Ajouter les clés au fichier `.env`

6. Lancer le backend
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

   API à : http://localhost:8080
   Docs à : http://localhost:8080/docs

### Configuration du Frontend

1. Naviguer vers le frontend
   ```bash
   cd ../frontend
   ```

2. Installer les dépendances
   ```bash
   npm install
   ```

3. Créer un fichier `.env` dans le répertoire `frontend/` :
   ```env
   VITE_API_URL=http://localhost:8080
   ```

4. Lancer le serveur de développement
   ```bash
   npm run dev
   ```

   Frontend à : http://localhost:5173

---

## Utilisation

### Démarrer l'application

Mode développement :

1. Démarrer le backend (Terminal 1) :
   ```bash
   cd backend
   source venv/bin/activate  # Windows: venv\Scripts\activate
   uvicorn app.main:app --reload --port 8080
   ```

2. Démarrer le frontend (Terminal 2) :
   ```bash
   cd frontend
   npm run dev
   ```

3. Démarrer les capteurs IoT (Terminal 3, optionnel) :
   ```bash
   cd backend
   python app/simulators/iot_sensor.py
   ```

### Points d'accès

- Frontend : http://localhost:5173
- Backend : http://localhost:8080
- API Docs : http://localhost:8080/docs
- Health : http://localhost:8080/health

### Comment utiliser

1. Dashboard - Voir les niveaux actuels de PM2.5, PM10, NO2 et les tendances
2. Map - Activer/désactiver heatmap de pollution, capteurs, stations Vélib, trafic, transport
3. Predictions - Voir les prévisions PM2.5 sur 24 heures avec scores de confiance
4. Mobility - Vérifier la disponibilité Vélib, perturbations de trafic, horaires de transport
5. Analytics - Analyser la corrélation pollution-météo et les patterns (connexion requise)
6. Reports - Générer des rapports PDF pour des plages de dates personnalisées (connexion requise)

---

## Capteurs IoT

### Emplacements des capteurs

5 capteurs placés à travers Paris :

- SENSOR_001 - Paris Centre (48.8566°N, 2.3522°E)
- SENSOR_002 - Paris Nord (48.8738°N, 2.2950°E)
- SENSOR_003 - Paris Sud (48.8414°N, 2.3209°E)
- SENSOR_004 - Paris Est (48.8467°N, 2.3775°E)
- SENSOR_005 - Paris Ouest (48.8656°N, 2.2879°E)

Tous mesurent : PM2.5, PM10, NO2

### Collecte de données

- Mesure toutes les 15 minutes
- 96 lectures par capteur par jour
- 480 lectures quotidiennes totales (5 capteurs × 96)
- Envoie via HTTP POST vers `/api/v1/air-quality/measurements`

### Simulation

Les capteurs sont simulés avec des patterns réalistes :
- Cycles quotidiens (pics pendant les heures de pointe 7-9h, 17-19h)
- Bruit aléatoire (±10%)
- Pics occasionnels (5% de chance, multiplicateur 1.5-2x)
- Dérive progressive dans le temps

Lancer le simulateur :
```bash
cd backend
python app/simulators/iot_sensor.py
```

Auto-enregistre les capteurs, envoie des données toutes les 15 min, enregistre les transmissions.

---

## Documentation API

### URLs de base

- Développement : http://localhost:8080
- Production : https://smartcity-platform-production.up.railway.app

### Authentification

Certains endpoints nécessitent une authentification JWT via Supabase :

```bash
# 1. Enregistrer un nouvel utilisateur
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"  # optionnel
}

# Réponse
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}

# 2. Connexion
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}

# Réponse
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {...}
}

# 3. Mot de passe oublié (envoie un email de réinitialisation)
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}

# 4. Réinitialiser le mot de passe (avec le token de l'email)
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "token": "reset_token_from_email",
  "new_password": "newsecurepassword"
}

# 5. Déconnexion
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# 6. Utiliser le token dans les requêtes suivantes
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

#### Configuration Supabase pour la production

Avant le déploiement, configurer Supabase :

1. Aller sur https://supabase.com/dashboard
2. Sélectionner votre projet → Authentication → URL Configuration
3. Définir Site URL : `https://frontend-gamma-three-19.vercel.app`
4. Ajouter les Redirect URLs :
   - `https://frontend-gamma-three-19.vercel.app/**`
   - `https://frontend-gamma-three-19.vercel.app/login`
   - `http://localhost:3000/**`
5. Activer la vérification email : Authentication → Providers → Email → Confirm email
6. Les utilisateurs doivent vérifier leur email avant que la connexion fonctionne

### Endpoints principaux

Qualité de l'air :
- `GET /api/v1/air-quality/current?city=paris` - lectures actuelles
- `GET /api/v1/air-quality/history?city=paris&limit=100` - données historiques
- `POST /api/v1/air-quality/measurements` - créer une mesure (capteurs)

Prédictions :
- `GET /api/v1/predictions/current?city=paris` - prévisions sur 24h
- `GET /api/v1/predictions/history?city=paris&days=7` - prédictions passées
- `POST /api/v1/predictions/train` - ré-entraîner le modèle

Mobilité :
- `GET /api/v1/mobility/velib?limit=50` - stations Vélib
- `GET /api/v1/mobility/traffic-disruptions?severity=high` - problèmes de trafic
- `GET /api/v1/mobility/transit-stops?limit=50` - arrêts de transport
- `GET /api/v1/mobility/next-departures?stop_id=STIF:StopPoint:Q:41322:` - départs

Analytique :
- `GET /api/v1/analytics/pollution-weather-correlation?city=paris&days=30`
- `GET /api/v1/analytics/temporal-analysis?city=paris&days=7`
- `GET /api/v1/analytics/statistics?city=paris&days=30`

Alertes :
- `GET /api/v1/alerts/active` - alertes actives
- `POST /api/v1/alerts` - créer une alerte
- `PATCH /api/v1/alerts/{id}/acknowledge` - accuser réception d'une alerte

Rapports :
- `POST /api/v1/reports/generate` - générer un PDF

Documentation complète : http://localhost:8080/docs

---

## Déploiement

### Backend (Railway)

1. Créer un compte sur https://railway.app
2. Créer un nouveau projet : `railway init`
3. Ajouter les variables d'environnement dans le tableau de bord Railway
4. Déployer : `railway up`
5. Obtenir l'URL : https://smartcity-platform-production.up.railway.app

### Frontend (Vercel)

1. Installer CLI : `npm install -g vercel`
2. Déployer : `cd frontend && vercel`
3. Ajouter la variable d'environnement `VITE_API_URL` dans le tableau de bord Vercel
4. Obtenir l'URL : https://frontend-gamma-three-19.vercel.app
5. Mettre à jour les URLs de redirection Supabase (voir section Authentification)

### Base de données (Supabase)

Déjà hébergée dans le cloud. Il suffit d'activer les politiques RLS et de créer des index.

---

## URLs de production

Application en ligne :
- Frontend : https://frontend-gamma-three-19.vercel.app
- Backend : https://smartcity-platform-production.up.railway.app
- API Docs : https://smartcity-platform-production.up.railway.app/docs
- Health : https://smartcity-platform-production.up.railway.app/health

Connexion démo :
- Email : anamrabdo1@smartcity.com
- Mot de passe : SmartCity2025!

---

## Structure du projet

```
smartcity/
├── backend/                      # Backend FastAPI
│   ├── app/
│   │   ├── main.py              # Point d'entrée de l'application FastAPI
│   │   ├── config.py            # Gestion de la configuration
│   │   ├── dependencies.py      # Injection de dépendances
│   │   ├── api/
│   │   │   └── v1/              # Routes API version 1
│   │   │       ├── air_quality.py
│   │   │       ├── predictions.py
│   │   │       ├── mobility.py
│   │   │       ├── analytics.py
│   │   │       ├── alerts.py
│   │   │       └── reports.py
│   │   ├── services/            # Couche de logique métier
│   │   │   ├── supabase_service.py
│   │   │   ├── mobility_service.py
│   │   │   ├── alert_service.py
│   │   │   └── pdf_service.py
│   │   ├── ml/                  # Apprentissage automatique
│   │   │   ├── trainer.py       # Entraînement du modèle
│   │   │   ├── predictor.py     # Prédictions
│   │   │   ├── feature_engineering.py
│   │   │   └── anomaly_detector.py
│   │   ├── models/              # Modèles Pydantic
│   │   │   ├── air_quality.py
│   │   │   ├── prediction.py
│   │   │   ├── mobility.py
│   │   │   └── alert.py
│   │   ├── simulators/          # Simulation IoT
│   │   │   └── iot_sensor.py
│   │   └── utils/               # Utilitaires
│   ├── database/
│   │   └── schema.sql           # Schéma de base de données
│   ├── requirements.txt         # Dépendances Python
│   └── .env                     # Variables d'environnement
│
├── frontend/                    # Frontend React
│   ├── src/
│   │   ├── pages/               # Composants de pages
│   │   │   ├── Dashboard.tsx
│   │   │   ├── DashboardMap.tsx
│   │   │   ├── Predictions.tsx
│   │   │   ├── Mobility.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── Reports.tsx
│   │   ├── components/          # Composants réutilisables
│   │   │   ├── Dashboard/       # Spécifiques au Dashboard
│   │   │   ├── Map/             # Couches de carte
│   │   │   ├── Charts/          # Composants de graphiques
│   │   │   └── Predictions/     # Cartes de prédiction
│   │   ├── services/            # Services API
│   │   │   └── api.ts
│   │   ├── hooks/               # Hooks React personnalisés
│   │   │   ├── useAirQuality.ts
│   │   │   ├── usePredictions.ts
│   │   │   ├── useMobility.ts
│   │   │   └── useAnalytics.ts
│   │   ├── stores/              # Stores d'état Zustand
│   │   ├── types/               # Types TypeScript
│   │   ├── App.tsx              # Composant principal de l'app
│   │   └── main.tsx             # Point d'entrée
│   ├── package.json             # Dépendances Node
│   ├── vite.config.ts           # Configuration Vite
│   └── .env                     # Variables d'environnement
│
├── docs/                        # Documentation
│   ├── TECHNICAL.md             # Documentation technique
│   ├── ARCHITECTURE_SEPARATION.md
│   └── TESTING.md
│
└── README.md                    # Ce fichier
```

---

## Performance

- Réponse API : < 200ms
- Chargement Dashboard : < 2 secondes
- Requêtes base de données : < 50ms
- Prédictions ML : < 500ms
- Génération PDF : < 3 secondes

Optimisations :
- Index de base de données sur city, timestamp, source
- Cache TanStack Query (5min stale time)
- Code splitting avec React.lazy()
- Vercel Edge CDN
- Compression Gzip/Brotli

---

## Sécurité

- Tokens JWT (HS256, expiration 60min)
- Row Level Security sur la base de données
- Validation des entrées avec Pydantic
- Prévention des injections SQL
- Protection XSS
- HTTPS partout
- Variables d'environnement pour les secrets

---

## Monitoring

- Health check : `/health`
- Logging JSON
- Tableau de bord Supabase pour les requêtes
- Alertes email pour les erreurs et dépassements de seuils
- Détection des capteurs hors ligne

---

## Contribution

1. Forker le repo
2. Créer une branche feature : `git checkout -b feature/name`
3. Commiter les changements : `git commit -m "Add feature"`
4. Pousser : `git push origin feature/name`
5. Créer une Pull Request

Standards de code :
- Backend : PEP 8, type hints, docstrings
- Frontend : TypeScript strict mode
- Écrire des tests pour les nouvelles fonctionnalités

Lancer les tests :
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

---

## Licence

MIT License

---

## Crédits

- Île-de-France Mobilités (IDFM) - APIs de mobilité
- Supabase - base de données et auth
- Communautés FastAPI et React
- Équipe ESIC

---

**Construit :** 18-31 décembre 2025
**Version :** 1.0.0
