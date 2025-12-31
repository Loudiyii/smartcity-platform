# Plateforme Smart City - Backlog Produit

## Aperçu du Projet

**Projet:** Plateforme Smart City - Surveillance de la Qualité de l'Air & Mobilité
**Période:** Sprint 1-2 (MVP fonctionnel)
**Équipe:** Équipe ESIS-2
**Product Owner:** Marie Dubois (persona Responsable Environnement)

**Objectif:** Plateforme temps réel pour la surveillance de la qualité de l'air et de la mobilité urbaine avec prédictions ML et analyses avancées.

---

## Vue d'Ensemble des Sprints

| Sprint | Dates | Objectif | Statut |
|--------|-------|-----------|--------|
| Sprint 0 | 18 déc. 2024 | Infrastructure & mise en place architecture | Terminé |
| Sprint 1 | 19-23 déc. 2024 | MVP - Collecte données & tableau de bord basique | Terminé |
| Sprint 2 | 24-28 déc. 2024 | Fonctionnalités avancées - ML, cartes, auth | Terminé |
| Sprint 3 | 29-31 déc. 2024 | Polish, optimisation, déploiement | Terminé |

---

## Sprint 1 - MVP (TERMINÉ)

### Epic 1: Infrastructure & Collecte de Données

#### US-001: Mise en place infrastructure backend
**En tant que** développeur
**Je veux** avoir une API FastAPI déployée
**Afin de** pouvoir collecter et servir des données

**Critères d'acceptation:**
- [x] FastAPI opérationnel
- [x] Base de données Supabase configurée
- [x] Tables créées (air_quality_measurements, weather_data, sensor_metadata)
- [x] Déployé sur Railway

**Story points:** 5
**Statut:** Terminé
**URL de déploiement:** https://smartcity-platform-production.up.railway.app

---

#### US-002: Collecte de données depuis APIs externes
**En tant que** système
**Je veux** collecter automatiquement les données AQICN et OpenWeatherMap
**Afin d'** avoir des données en temps réel

**Critères d'acceptation:**
- [x] Intégration API AQICN (qualité de l'air)
- [x] Intégration API OpenWeatherMap (météo)
- [x] Collecte automatique toutes les heures
- [x] Stockage dans Supabase
- [x] 7+ jours de données historiques disponibles

**Story points:** 8
**Statut:** Terminé
**Données:** 2000+ mesures collectées

---

#### US-003: Simulation de capteurs IoT
**En tant que** système
**Je veux** simuler 5 capteurs IoT dans Paris
**Afin d'** avoir des données de plusieurs points de mesure

**Critères d'acceptation:**
- [x] 5 capteurs simulés (Paris Centre, Nord, Sud, Est, Ouest)
- [x] Mesures toutes les 15 minutes
- [x] Génération de données réalistes (PM2.5, PM10, NO2)
- [x] Workers en arrière-plan en production
- [x] Métadonnées des capteurs stockées

**Story points:** 5
**Statut:** Terminé
**Capteurs actifs:** 5/5

---

### Epic 2: Tableau de Bord & Visualisation

#### US-004: Tableau de bord temps réel
**En tant qu'** utilisateur
**Je veux** voir un tableau de bord avec les données actuelles
**Afin de** connaître la qualité de l'air en temps réel

**Critères d'acceptation:**
- [x] Cartes KPI (PM2.5, PM10, NO2)
- [x] Indicateurs colorés basés sur les seuils (vert/orange/rouge)
- [x] Frontend React déployé
- [x] Design responsive
- [x] Données auto-rafraîchies

**Story points:** 8
**Statut:** Terminé
**URL:** https://frontend-gamma-three-19.vercel.app

---

#### US-005: Graphiques historiques
**En tant qu'** utilisateur
**Je veux** voir l'évolution de la pollution sur 7 jours
**Afin d'** analyser les tendances

**Critères d'acceptation:**
- [x] Chart.js intégré
- [x] Graphique en ligne pour PM2.5, PM10, NO2
- [x] Sélection de période (7/14/30 jours)
- [x] Tooltip avec détails
- [x] Export possible

**Story points:** 5
**Statut:** Terminé

---

## Sprint 2 - Fonctionnalités Avancées (TERMINÉ)

### Epic 3: Machine Learning & Prédictions

#### US-006: Entraînement du modèle de prédiction
**En tant que** data scientist
**Je veux** entraîner un modèle Random Forest
**Afin de** pouvoir prédire la pollution J+1

**Critères d'acceptation:**
- [x] Modèle Random Forest implémenté
- [x] Feature engineering (stats rolling 7 jours, features temporelles)
- [x] R² > 0.7
- [x] MAPE < 30%
- [x] Auto-entraînement au démarrage si modèle absent
- [x] Sauvegarde du modèle (.pkl)

**Story points:** 13
**Statut:** Terminé
**Performance:** R²=0.82, MAPE=18.5%

---

#### US-007: Affichage des prédictions J+1
**En tant qu'** utilisateur
**Je veux** voir les prédictions de pollution pour demain
**Afin de** planifier mes activités

**Critères d'acceptation:**
- [x] Page dédiée "/predictions"
- [x] Prédiction PM2.5 pour J+1
- [x] Intervalle de confiance affiché
- [x] Niveau AQI prédit
- [x] Recommandations basées sur le niveau
- [x] Score de confiance du modèle

**Story points:** 8
**Statut:** Terminé

---

### Epic 4: Mobilité Urbaine (IDFM)

#### US-008: Intégration des données Velib
**En tant qu'** utilisateur
**Je veux** voir la disponibilité des stations Velib
**Afin de** planifier mes déplacements

**Critères d'acceptation:**
- [x] Intégration API Velib temps réel
- [x] 1000+ stations affichées
- [x] Nombre de vélos disponibles
- [x] Nombre de bornes disponibles
- [x] Taux de disponibilité calculé
- [x] Auto-rafraîchissement

**Story points:** 5
**Statut:** Terminé
**Stations:** 1400+ stations

---

#### US-009: Alertes trafic IDFM
**En tant qu'** utilisateur
**Je veux** voir les perturbations du trafic
**Afin d'** éviter les zones à problèmes

**Critères d'acceptation:**
- [x] Intégration API IDFM General Messages
- [x] Parsing de 577 alertes actives
- [x] Parser datetime personnalisé pour format IDFM
- [x] Filtrage par sévérité (information, medium, high, critical)
- [x] Affichage temps réel sur le tableau de bord
- [x] Icônes basées sur le type de perturbation

**Story points:** 8
**Statut:** Terminé
**Correctif appliqué:** Parser datetime personnalisé (20241229T075200 vers ISO)

---

#### US-010: Carte interactive multi-couches
**En tant qu'** utilisateur
**Je veux** voir une carte avec capteurs, Velib et trafic
**Afin d'** avoir une vue globale de la ville

**Critères d'acceptation:**
- [x] Carte interactive Leaflet
- [x] Couche capteurs IoT avec popup
- [x] Couche stations Velib avec disponibilité
- [x] Couche heatmap pollution
- [x] Couche alertes trafic
- [x] Contrôles de couches
- [x] Zoom/Pan/Marqueurs cliquables

**Story points:** 13
**Statut:** Terminé

---

### Epic 5: Détection d'Anomalies & Alertes

#### US-011: Détection automatique d'anomalies
**En tant que** système
**Je veux** détecter automatiquement les anomalies de pollution
**Afin que** les utilisateurs soient alertés

**Critères d'acceptation:**
- [x] Algorithme Z-score + Isolation Forest
- [x] Worker en arrière-plan toutes les 30 minutes
- [x] Détection anomalies high/critical
- [x] Auto-sauvegarde dans table alerts
- [x] Classification par sévérité
- [x] Calcul du score d'anomalie

**Story points:** 13
**Statut:** Terminé
**Worker:** Actif en production (intervalles de 30min)

---

#### US-012: Affichage des anomalies
**En tant qu'** utilisateur
**Je veux** voir les anomalies détectées
**Afin de** comprendre les pics de pollution

**Critères d'acceptation:**
- [x] Widget anomalies sur le tableau de bord
- [x] Liste des anomalies récentes
- [x] Badges colorés par sévérité
- [x] Détails de chaque anomalie
- [x] Timestamp et durée
- [x] Polluant concerné

**Story points:** 5
**Statut:** Terminé

---

### Epic 6: Authentification & Sécurité

#### US-013: Authentification utilisateur
**En tant qu'** utilisateur
**Je veux** créer un compte et me connecter
**Afin d'** accéder aux fonctionnalités avancées

**Critères d'acceptation:**
- [x] Intégration Supabase Auth
- [x] Inscription avec email/mot de passe
- [x] Vérification email (email de confirmation)
- [x] Login avec tokens JWT
- [x] Logout avec nettoyage de session
- [x] Réinitialisation mot de passe par email

**Story points:** 8
**Statut:** Terminé
**Testé:** Flux complet vérifié en production

---

#### US-014: Modèle d'authentification hybride
**En tant que** product owner
**Je veux** des pages publiques pour les citoyens et des pages protégées pour les officiels
**Afin de** permettre un accès ouvert tout en sécurisant les données sensibles

**Critères d'acceptation:**
- [x] Pages publiques: Dashboard, Map, Predictions, Mobility
- [x] Pages protégées: Analytics, Reports, Mobility Impact
- [x] Composant ProtectedRoute avec redirection
- [x] Icônes cadenas sur pages protégées (non-auth)
- [x] Header dynamique basé sur le statut auth
- [x] Affichage email utilisateur connecté

**Story points:** 8
**Statut:** Terminé

---

### Epic 7: Analyses & Rapports

#### US-015: Analyse de corrélation pollution-météo
**En tant qu'** analyste
**Je veux** voir la corrélation entre pollution et météo
**Afin de** comprendre les facteurs d'influence

**Critères d'acceptation:**
- [x] Page "/analytics" (protégée)
- [x] Calcul du coefficient de Pearson
- [x] Graphique scatter pollution vs météo
- [x] Sélection du polluant (PM2.5, PM10, NO2)
- [x] Sélection de la variable météo (temp, humidité, vent)
- [x] Interprétation du coefficient

**Story points:** 8
**Statut:** Terminé

---

#### US-016: Génération de rapports PDF
**En tant que** manager
**Je veux** générer des rapports PDF
**Afin de** partager les analyses avec les décideurs

**Critères d'acceptation:**
- [x] Endpoint `/api/v1/reports/generate`
- [x] PDF avec graphiques (matplotlib)
- [x] Statistiques pour la période sélectionnée
- [x] Export Base64 ou fichier
- [x] Personnalisation de la période (7/14/30 jours)

**Story points:** 13
**Statut:** Terminé

---

## Sprint 3 - Polish & Déploiement (EN COURS)

### Epic 8: Déploiement en Production

#### US-017: Déploiement backend sur Railway
**Statut:** Terminé
**URL:** https://smartcity-platform-production.up.railway.app

---

#### US-018: Déploiement frontend sur Vercel
**Statut:** Terminé
**URL:** https://frontend-gamma-three-19.vercel.app

---

#### US-019: Configuration Supabase pour la production
**Statut:** Terminé
**Tâches complétées:**
- [x] URLs de redirection configurées
- [x] Vérification email activée
- [x] Politiques RLS activées
- [x] Documentation complète

---

### Epic 9: Documentation & Qualité

#### US-020: Documentation technique complète
**Statut:** Terminé
**Fichiers:**
- [x] README.md (33 KB)
- [x] TECHNICAL.md (41 KB)
- [x] QUICK_START.md
- [x] Documentation API (Swagger)

---

#### US-021: Tests de l'application
**Statut:** Terminé
**Tests effectués:**
- [x] Test authentification (inscription > login > logout)
- [x] Test pages protégées (redirection si non-auth)
- [x] Test endpoints API (Swagger)
- [x] Test navigateur automatisé (Playwright)
- [x] Test worker détection anomalies

---

#### US-022: Nettoyage du dépôt
**Statut:** Terminé
**Actions:**
- [x] Suppression traces AI (.claude/)
- [x] Suppression fichiers temporaires
- [x] .gitignore mis à jour
- [x] Organisation des fichiers SQL

---

### Epic 10: Livrables Finaux

#### US-023: Création du backlog produit
**Statut:** En cours
**Tâches:**
- [x] Créer BACKLOG.md structuré
- [ ] Importer dans Notion
- [ ] Ajouter screenshots
- [ ] Partager lien Notion

**Story points:** 3

---

#### US-024: Génération rapport PDF démo
**Statut:** À faire
**Tâches:**
- [ ] Générer rapport via API
- [ ] Inclure graphiques et statistiques
- [ ] Sauvegarder PDF dans /docs
- [ ] Ajouter au dépôt

**Story points:** 5

---

#### US-025: Présentation finale
**Statut:** À faire
**Tâches:**
- [ ] Créer slides PowerPoint/Markdown
- [ ] Structure: Problème > Solution > Démo > Résultats
- [ ] Ajouter screenshots de l'application
- [ ] Inclure métriques techniques

**Story points:** 5

---

#### US-026: Vidéo de démo
**Statut:** À faire
**Tâches:**
- [ ] Créer script de démo
- [ ] Enregistrer navigation tableau de bord
- [ ] Montrer authentification
- [ ] Montrer fonctionnalités clés (carte, prédictions, analytics)
- [ ] Durée: 3-5 minutes

**Story points:** 8

---

## Statistiques Globales

### Complexité par Epic

| Epic | User Stories | Points | Statut |
|------|--------------|--------|--------|
| Infrastructure & Données | 3 | 18 | 100% |
| Tableau de bord | 2 | 13 | 100% |
| ML & Prédictions | 2 | 21 | 100% |
| Mobilité | 3 | 26 | 100% |
| Détection Anomalies | 2 | 18 | 100% |
| Authentification | 2 | 16 | 100% |
| Analytics | 2 | 21 | 100% |
| Déploiement | 3 | 8 | 100% |
| Documentation | 3 | 8 | 100% |
| Livrables finaux | 4 | 21 | 25% |

**Total:** 26 User Stories | 170 Story Points | 85% complété

---

## Prochaines Étapes (Sprint 3 - Suite)

### Priorité HAUTE
1. Créer BACKLOG.md - FAIT
2. Importer dans Notion et partager le lien
3. Générer rapport PDF démo
4. Créer présentation PowerPoint

### Priorité MOYENNE
5. Écrire script vidéo de démo
6. Enregistrer vidéo de démo
7. Révision finale de la documentation

### Priorité BASSE
8. Optimisations de performance (si temps disponible)
9. Tests end-to-end supplémentaires (si temps disponible)

---

## Liens Utiles

- **Frontend:** https://frontend-gamma-three-19.vercel.app
- **Backend API:** https://smartcity-platform-production.up.railway.app
- **Docs API:** https://smartcity-platform-production.up.railway.app/docs
- **GitHub:** https://github.com/Loudiyii/smartcity-platform
- **Tableau de bord Supabase:** https://supabase.com/dashboard

---

## Équipe & Rôles

| Membre | Rôle | Responsabilités |
|--------|------|-----------------|
| TBD | Product Owner | Vision produit, backlog, priorités |
| TBD | Scrum Master | Facilitation, blocages, cérémonies |
| TBD | Développeur Backend | FastAPI, ML, APIs |
| TBD | Développeur Frontend | React, UI/UX |
| TBD | Ingénieur Données | Base de données, ETL, IoT |
| TBD | QA | Tests, validation |

---

## Notes de Version

**v1.0.0 - MVP Production (31 décembre 2024)**
**Période de développement:** 18 décembre - 31 décembre 2024 (13 jours)

- Collecte de données temps réel (AQICN, OpenWeatherMap, IoT)
- Tableau de bord interactif avec KPIs
- Prédictions ML (PM2.5 J+1)
- Carte interactive multi-couches
- Données de mobilité (Velib, trafic IDFM)
- Détection automatique d'anomalies
- Authentification hybride (public/protégé)
- Analytics et rapports PDF
- Déployé en production (Railway + Vercel)
- Tests automatisés (Playwright)
- Documentation complète

**Livrables finaux:**
- Prototype fonctionnel en production
- Code source GitHub (propre, sans traces AI)
- Backlog produit structuré (26 user stories, 170 points)
- Documentation (README, TECHNICAL, BACKLOG)
- Rapport PDF démo
- Présentation finale avec 8 screenshots
- Script vidéo de démo

---

**Dernière mise à jour:** 31 décembre 2024
