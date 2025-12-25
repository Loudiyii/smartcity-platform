# Documentation Fonctionnelle - Plateforme Smart City

## Suivi de la qualité de l'air et de la mobilité

---

## 1. CONTEXTE ET VISION PRODUIT

### Vision Métier

En tant que **Directeur de la Transition Écologique de la Métropole**, la plateforme permet de surveiller en temps réel la qualité de l'air et les données de mobilité du territoire.

**Objectifs principaux :**
- Informer les citoyens sur la qualité de l'air en temps réel
- Anticiper les pics de pollution pour prendre des mesures préventives

### Problématiques Identifiées

1. **Manque de visibilité** sur la qualité de l'air en temps réel
2. **Absence d'outils prédictifs** pour anticiper les épisodes de pollution
3. **Données dispersées** entre différents services (environnement, transport, météo)
4. **Communication citoyenne insuffisante** sur ces enjeux

### Objectifs Business

- Réduire de **15% les épisodes de pollution non anticipés**
- Améliorer la **satisfaction citoyenne** sur l'information environnementale
- Optimiser les **mesures de restriction de circulation**
- Respecter les **obligations réglementaires** de surveillance

---

## 2. PERSONAS ET UTILISATEURS CIBLES

### Persona Principal : Marie Dubois - Responsable Environnement

- **Âge :** 42 ans
- **Rôle :** Responsable du service environnement de la métropole
- **Besoins :**
  - Visualiser les données de pollution en temps réel
  - Recevoir des alertes en cas de dépassement de seuils
  - Générer des rapports pour les élus
  - Prévoir les pics de pollution à J+1

### Persona Secondaire : Jean Martin - Citoyen Sensibilisé

- **Âge :** 35 ans, père de famille
- **Besoins :**
  - Consulter la qualité de l'air avant de sortir avec ses enfants
  - Recevoir des notifications en cas d'alerte pollution
  - Comprendre l'impact de ses déplacements

### Persona Tertiaire : Pierre Lambert - Élu Municipal

- **Âge :** 55 ans
- **Besoins :**
  - Données consolidées pour prendre des décisions
  - Rapports d'activité pour les conseils municipaux
  - Argumentaires chiffrés pour les politiques publiques

---

## 3. DONNÉES DISPONIBLES ET SOURCES

### Sources de Données Obligatoires

#### 3.1 API Open Data - Qualité de l'air
- **Source :** AtmoSud, AQICN, ou données gouvernementales
- **Polluants :** PM2.5, PM10, NO2, O3, SO2
- **Fréquence :** Horaire
- **Format :** JSON/REST API

#### 3.2 Données Météorologiques
- **Source :** OpenWeatherMap API (gratuite)
- **Variables :** Température, humidité, vent, pression
- **Fréquence :** Horaire
- **Impact :** Corrélation avec dispersion des polluants

#### 3.3 Données de Mobilité
- **Source :** API transport public + data.gouv.fr
- **Données :** Trafic routier, fréquentation transports
- **Alternative :** Génération de données simulées réalistes

### Simulation IoT (Capteurs Virtuels)

- **3 capteurs virtuels** positionnés sur la ville
- **Mesures :** PM2.5, température, humidité
- **Fréquence :** Toutes les 15 minutes
- **Format :** JSON via HTTP POST ou MQTT

---

## 4. FONCTIONNALITÉS PAR SPRINT

### SPRINT 1 - MVP (Semaine 1)

**Objectif :** Prototype fonctionnel de base

#### Epic 1 : Collecte de Données

| US | Description | Critères d'acceptation |
|---|---|---|
| **US-001** | En tant qu'administrateur, je veux récupérer les données de qualité de l'air depuis une API publique pour alimenter la plateforme | API connectée, données récupérées toutes les heures |
| **US-002** | En tant que système, je veux stocker les données dans une base de données pour assurer la persistance | Minimum 7 jours d'historique en base |
| **US-003** | En tant que développeur, je veux simuler des capteurs IoT pour tester l'ingestion en temps réel | 3 capteurs virtuels actifs, données toutes les 15 min |

#### Epic 2 : Visualisation de Base

| US | Description | Critères d'acceptation |
|---|---|---|
| **US-004** | En tant qu'utilisateur, je veux voir les données de pollution actuelles sur un dashboard simple | Dashboard avec au moins 3 KPI de pollution |
| **US-005** | En tant qu'utilisateur, je veux filtrer par polluant (PM2.5, PM10, NO2) pour analyser spécifiquement | Filtres fonctionnels pour chaque polluant |
| **US-006** | En tant qu'utilisateur, je veux voir l'évolution sur les dernières 24h sous forme de graphique | Graphique temporel des 24 dernières heures |

#### Epic 3 : Infrastructure

| US | Description | Critères d'acceptation |
|---|---|---|
| **US-007** | En tant qu'administrateur, je veux que l'application soit accessible via une URL sécurisée (HTTPS) | Certificat SSL/TLS configuré |
| **US-008** | En tant que responsable cyber, je veux une authentification basique pour protéger l'accès admin | JWT ou sessions implémentés |

### SPRINT 2 - Enrichissement (3 semaines intermittentes)

**Objectif :** Fonctionnalités avancées et prédiction

#### Epic 4 : Analyse Prédictive

| US | Description | Critères d'acceptation |
|---|---|---|
| **US-009** | En tant que responsable environnement, je veux une prévision de la qualité de l'air à J+1 pour anticiper les actions | Modèle prédictif avec précision > 70% |
| **US-010** | En tant que système, je veux détecter automatiquement les anomalies dans les mesures | Détection par Z-score ou Isolation Forest |
| **US-011** | En tant qu'utilisateur, je veux voir le niveau de fiabilité des prédictions | Indicateur de confiance affiché |

#### Epic 5 : Dashboard Avancé

| US | Description | Critères d'acceptation |
|---|---|---|
| **US-012** | En tant qu'utilisateur, je veux une carte interactive montrant la qualité de l'air par zone | Carte avec marqueurs de pollution |
| **US-013** | En tant qu'analyste, je veux corréler pollution et données météo sur un même graphique | Graphique multi-axes fonctionnel |
| **US-014** | En tant qu'élu, je veux générer un rapport PDF des données de la semaine | Export PDF fonctionnel |

#### Epic 6 : Alertes et Notifications

| US | Description | Critères d'acceptation |
|---|---|---|
| **US-015** | En tant que responsable, je veux recevoir une alerte email en cas de dépassement de seuil | Notification email avec seuil paramétrable |
| **US-016** | En tant que citoyen, je veux consulter des recommandations selon le niveau de pollution | Recommandations contextuelles affichées |

### SPRINT 3 - Finalisation (1 semaine)

**Objectif :** Produit final et optimisations

#### Epic 7 : Optimisations et Monitoring

| US | Description | Critères d'acceptation |
|---|---|---|
| **US-017** | En tant qu'administrateur système, je veux monitorer les performances de l'application | Dashboard de monitoring actif |
| **US-018** | En tant que développeur, je veux des logs détaillés pour le debugging | Logs structurés et traçables |
| **US-019** | En tant qu'utilisateur, je veux que l'interface soit responsive sur mobile | Interface utilisable sur smartphone |

---

## 5. ARCHITECTURE TECHNIQUE

### Stack Technologique Recommandée

- **Frontend :** Angular / React.js / Vue.js + Chart.js/D3.js pour les visualisations
- **Backend :** Spring Boot / Node.js/Express / Python/Flask + API REST
- **Base de données :** MySQL / PostgreSQL + InfluxDB (time series) / MongoDB
- **ML/IA :** Python + Scikit-learn / TensorFlow Lite / Java
- **IoT Simulation :** Python + MQTT / HTTP POST
- **Infra :** Docker + Docker Compose pour le déploiement
- **Dashboard BI :** Grafana, Metabase ou PowerBI

### Contraintes d'Hébergement

- **Environnement de développement :** Local (Docker)
- **Environnement de test :** VM ou cloud gratuit (Heroku, Vercel, ou VPS)
- **RGPD :** Anonymisation des données utilisateur, pas de géolocalisation précise

---

## 6. MODÈLE IA/DATA SCIENCE

### Modèle Prédictif Principal

**Objectif :** Prédire la concentration de PM2.5 à J+1

**Variables d'entrée :**
- Données historiques de pollution (7 derniers jours)
- Données météorologiques (température, vent, humidité, pression)
- Jour de la semaine (impact trafic)
- Saison

**Algorithme suggéré :**
- **Phase 1 :** Régression linéaire multiple (baseline)
- **Phase 2 :** Random Forest ou XGBoost (si temps disponible)
- **Métrique :** RMSE et MAPE sur données de test

### Modèle de Détection d'Anomalies

**Objectif :** Détecter les mesures aberrantes des capteurs

- **Méthode :** Z-score ou Isolation Forest
- **Seuil d'alerte :** 3 écarts-types ou score d'anomalie > 0.7

---

## 7. EXIGENCES SÉCURITÉ ET CONFORMITÉ

### Sécurité Basique Requise

1. **Authentification :** JWT ou sessions pour l'accès admin
2. **HTTPS :** Certificat SSL/TLS obligatoire
3. **Validation des données :** Sanitisation des inputs utilisateur
4. **Logs de sécurité :** Traçabilité des accès et actions sensibles

### RGPD et Protection des Données

1. **Anonymisation :** Pas de données personnelles stockées
2. **Consentement :** Banner cookies si analytics
3. **Droit à l'oubli :** Possibilité de supprimer les données utilisateur
4. **Documentation :** Registre des traitements de données

---

## 8. CRITÈRES D'ACCEPTATION DÉTAILLÉS

### Critères MVP (Sprint 1)

- ✅ **Collecte :** L'application récupère des données réelles toutes les heures
- ✅ **Stockage :** Minimum 7 jours d'historique en base
- ✅ **Affichage :** Dashboard avec au moins 3 KPI de pollution
- ✅ **Temps de réponse :** < 3 secondes pour charger le dashboard
- ✅ **Disponibilité :** Application accessible 95% du temps

### Critères Finaux (Sprint 3)

- ✅ **Prédiction :** Modèle avec précision > 70% sur 30 jours de test
- ✅ **Alertes :** Notification email fonctionnelle avec seuil paramétrable
- ✅ **Performance :** Support de 50 utilisateurs simultanés
- ✅ **Mobile :** Interface utilisable sur smartphone
- ✅ **Documentation :** README complet + documentation API

---

## 9. SCÉNARIOS DE DÉMONSTRATION

### Démo Sprint 1 (5 minutes)

1. **Ouverture de l'application** → Dashboard principal s'affiche
2. **Visualisation temps réel** → Données actuelles de pollution
3. **Historique** → Graphique des 24 dernières heures
4. **Admin** → Connexion et visualisation des logs

### Démo Finale (10 minutes)

1. **Scénario nominal** → Consultation citoyenne standard
2. **Scénario d'alerte** → Simulation pic de pollution + notification
3. **Scénario prédiction** → Affichage prévision J+1 avec explication
4. **Scénario mobile** → Navigation sur smartphone
5. **Scénario rapport** → Génération PDF pour les élus

---

## 10. DONNÉES DE TEST ET RÉFÉRENCES

### Jeux de Données pour Tests

- **Historique pollution :** 6 mois de données réelles (CSV fourni)
- **Données météo :** Corrélées aux données de pollution
- **Seuils d'alerte :**
  - PM2.5 > 50 μg/m³
  - PM10 > 80 μg/m³
  - NO2 > 200 μg/m³

### APIs Publiques Recommandées

- **World Air Quality Index :** https://aqicn.org/api/
- **OpenWeatherMap :** https://openweathermap.org/api
- **data.gouv.fr :** Données transport et environnement

---

## 11. CONTRAINTES ET DÉLAIS

### Contraintes Techniques

- **Budget :** 0€ (uniquement services gratuits)
- **Équipe :** 5-7 personnes avec spécialités mixtes
- **Temps :** 1 mois avec 3 semaines intermittentes

### Points de Validation Obligatoires

- **J+2 :** Architecture validée + premiers développements
- **Fin Sprint 1 :** Démo MVP fonctionnel
- **Mi-projet :** Point d'avancement modèle IA
- **J-3 :** Tests finaux et préparation soutenance

### Livrables Attendus

1. **Code source :** GitHub avec README complet
2. **Application déployée :** URL d'accès fonctionnelle
3. **Documentation technique :** Architecture + API
4. **Rapport d'analyse :** Insights sur les données + performances IA
5. **Vidéo démo :** 5 minutes de présentation
6. **Backlog final :** Évolutions possibles V2

---

## 12. FAQ - QUESTIONS POTENTIELLES

### Q : Faut-il vraiment implémenter l'IoT ?
**R :** Oui, mais simulation Python ou autres acceptable. L'important est le flux de données temps réel.

### Q : Quelle précision minimum pour le modèle IA ?
**R :** 70% de précision acceptable pour un MVP, avec méthode d'évaluation documentée.

### Q : Faut-il gérer plusieurs villes ?
**R :** Non, concentrez-vous sur une ville fictive ou réelle comme cas d'usage.

### Q : Niveau de sécurité attendu ?
**R :** Basique mais réel : HTTPS + auth + validation inputs. Pas de pentesting poussé.

---

## 13. CONTACT ET SUPPORT

- **Contact Client :** Joel BANKA
- **Disponibilité :** Daily meetings possibles, validation rapide des livrables
- **Budget formation :** Accompagnement technique possible si blocage majeur

---

*Document généré à partir de l'Expression de Besoin : Plateforme Smart City v2*
*Projet de rentrée ESIS-2/CPDIA-2*
