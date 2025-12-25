# Workflows Index

Navigation complète des workflows disponibles pour le projet Smart City.

## Par Ordre d'Implémentation (Recommandé)

### Phase 1: MVP (Sprint 1)
1. **dashboard-setup.md** - Dashboard basique avec KPIs
2. **authentication-setup.md** - Login/logout et routes protégées

### Phase 2: Features Avancées (Sprint 2)
3. **ml-pipeline-setup.md** - Prédictions PM2.5 à J+1
4. **advanced-features.md** - Carte interactive 5 couches
5. **alerts-implementation.md** - Système d'alertes email
6. **anomaly-detection-setup.md** - Détection anomalies capteurs

### Phase 3: Finalisations (Sprint 3)
7. **pdf-reports-implementation.md** - Rapports PDF
8. **final-touches.md** - Optimisations et monitoring

---

## Par Catégorie

### 🎨 Frontend
- dashboard-setup.md - Dashboard temps réel
- advanced-features.md - Features avancées UI

### 🔧 Backend
- authentication-setup.md - Auth JWT
- alerts-implementation.md - Alertes automatiques
- pdf-reports-implementation.md - Génération PDF

### 🤖 Machine Learning
- ml-pipeline-setup.md - Training & prédictions
- anomaly-detection-setup.md - Détection anomalies

### 🚀 DevOps
- final-touches.md - Optimisations & monitoring

---

## Dépendances entre Workflows

```
dashboard-setup
    ↓
authentication-setup
    ↓
ml-pipeline-setup ←→ anomaly-detection-setup
    ↓
advanced-features
    ↓
alerts-implementation
    ↓
pdf-reports-implementation
    ↓
final-touches
```

---

## Par Priorité

### Haute (Semaine 1)
- ⚡ dashboard-setup.md
- ⚡ authentication-setup.md
- ⚡ ml-pipeline-setup.md

### Moyenne (Semaine 2-3)
- 📊 advanced-features.md
- 🔔 alerts-implementation.md
- 🔍 anomaly-detection-setup.md

### Basse (Semaine 4)
- 📄 pdf-reports-implementation.md
- ✨ final-touches.md

---

## Mapping Anciens Prompts → Workflows

| Ancien Prompt | Nouveau Workflow | Statut |
|---------------|------------------|--------|
| F05-basic-dashboard-UPDATED.md | dashboard-setup.md | ✅ Créé |
| F06-authentication-UPDATED.md | authentication-setup.md | ✅ Créé |
| F07-ml-prediction-UPDATED.md | ml-pipeline-setup.md | ✅ Créé |
| F08-advanced-dashboard-UPDATED.md | advanced-features.md | ✅ Créé |
| F09-alerts-system-UPDATED.md | alerts-implementation.md | ✅ Créé |
| F10-anomaly-detection-UPDATED.md | anomaly-detection-setup.md | ✅ Créé |
| F11-pdf-reports-UPDATED.md | pdf-reports-implementation.md | ✅ Créé |
| F12-F14-UPDATED.md | final-touches.md | ✅ Créé |

---

## Skills Utilisés par Workflow

| Workflow | Skills Principaux |
|----------|-------------------|
| dashboard-setup | frontend-dashboard, backend-api |
| authentication-setup | backend-api, frontend-dashboard, database-schema |
| ml-pipeline-setup | ml-predictions, backend-api |
| advanced-features | frontend-dashboard, backend-api, database-schema |
| alerts-implementation | backend-api, database-schema, external-apis |
| anomaly-detection-setup | ml-predictions, backend-api |
| pdf-reports-implementation | backend-api |
| final-touches | Tous |

---

## Guide d'Utilisation

### Comment démarrer un workflow ?

1. **Lire le workflow** souhaité
2. **Vérifier les prérequis**
3. **Activer les skills** mentionnés (automatique)
4. **Suivre les étapes** numérotées
5. **Valider les critères** d'acceptation

### Exemple
```
Je veux implémenter les prédictions ML:

1. Ouvrir ml-pipeline-setup.md
2. Vérifier: ✅ Backend configuré, ✅ Données historiques disponibles
3. Skills activés automatiquement: ml-predictions, backend-api
4. Suivre Étape 1 → Feature Engineering
5. Vérifier: [ ] Model R² > 0.7
```

---

## Documentation Complémentaire

### Skills
Voir `.claude/skills/` pour les patterns techniques détaillés

### Anciens Prompts
Voir `C:\smartcity\.prompts\` pour référence historique

### Documentation Projet
- `docs/TECHNICAL.md` - Spécifications techniques
- `docs/fonctionnel.md` - Cahier des charges
- `.claude/CLAUDE.md` - Contexte principal

---

**Dernière mise à jour:** 2025-12-24
**Version:** 1.0
