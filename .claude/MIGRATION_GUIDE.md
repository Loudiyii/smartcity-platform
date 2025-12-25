# Migration Guide: .prompts → Context Engineering

## Vue d'Ensemble

Cette approche hybride combine le meilleur des deux mondes :
- **Skills** = Connaissance technique (comment coder)
- **Commands** = Actions spécifiques (quoi faire)
- **Workflows** = Séquences de tâches (user stories)

## Mapping: Anciens Prompts → Nouvelle Structure

### Catégorie 1: Infrastructure & Patterns Techniques

Ces prompts deviennent des **Skills** (déjà fait ✅)

| Ancien Prompt | Nouveau Skill | Raison |
|---------------|---------------|--------|
| F01-core-infrastructure.md | `backend-api/SKILL.md` | Patterns FastAPI réutilisables |
| F04-database-models.md | `database-schema/SKILL.md` | Schéma DB + patterns SQL |
| F03-iot-simulation.md | `iot-simulation/SKILL.md` | Patterns simulation capteurs |
| F02-data-collection.md | `external-apis/SKILL.md` | Patterns d'intégration API |

### Catégorie 2: Fonctionnalités Spécifiques

Ces prompts deviennent des **Workflows** (à créer)

| Ancien Prompt | Nouveau Workflow | Type |
|---------------|------------------|------|
| F05-basic-dashboard-UPDATED.md | `.claude/workflows/dashboard-setup.md` | Guide étape-par-étape |
| F06-authentication-UPDATED.md | `.claude/workflows/add-authentication.md` | Guide implémentation |
| F07-ml-prediction-UPDATED.md | `.claude/workflows/setup-ml-pipeline.md` | Guide ML |
| F08-advanced-dashboard-UPDATED.md | `.claude/workflows/advanced-features.md` | Guide features |
| F09-alerts-system-UPDATED.md | `.claude/workflows/alerts-implementation.md` | Guide système alertes |
| F10-anomaly-detection-UPDATED.md | `.claude/workflows/anomaly-detection.md` | Guide détection |
| F11-pdf-reports-UPDATED.md | `.claude/workflows/pdf-reports.md` | Guide rapports |

### Catégorie 3: Fonctionnalités Mobilité (Spécifiques)

Ces prompts deviennent des **Skills spécialisés**

| Ancien Prompt | Nouveau Skill | Créer |
|---------------|---------------|-------|
| F02b-mobility-data.md | `.claude/skills/mobility-data/SKILL.md` | ⬜ À créer |
| F02c-realtime-transport.md | `.claude/skills/realtime-transport/SKILL.md` | ⬜ À créer |
| F02d-isochrones-analysis.md | `.claude/skills/isochrones/SKILL.md` | ⬜ À créer |

## Structure Recommandée Finale

```
.claude/
├── skills/                          # Connaissance technique (domain)
│   ├── backend-api/                 # ✅ Créé
│   ├── ml-predictions/              # ✅ Créé
│   ├── frontend-dashboard/          # ✅ Créé
│   ├── database-schema/             # ✅ Créé
│   ├── iot-simulation/              # ✅ Créé
│   ├── external-apis/               # ✅ Créé
│   ├── mobility-data/               # ⬜ Nouveau (si besoin)
│   ├── realtime-transport/          # ⬜ Nouveau (si besoin)
│   └── isochrones/                  # ⬜ Nouveau (si besoin)
│
├── workflows/                       # Séquences de tâches (task)
│   ├── dashboard-setup.md           # ⬜ À créer
│   ├── add-authentication.md        # ⬜ À créer
│   ├── setup-ml-pipeline.md         # ⬜ À créer
│   ├── alerts-implementation.md     # ⬜ À créer
│   ├── anomaly-detection.md         # ⬜ À créer
│   └── pdf-reports.md               # ⬜ À créer
│
├── commands/                        # Actions rapides (quick)
│   ├── add-api-route.md             # ✅ Créé
│   ├── create-component.md          # ✅ Créé
│   ├── run-ml-training.md           # ✅ Créé
│   └── test-sensors.md              # ✅ Créé
│
└── CLAUDE.md                        # ✅ Contexte principal
```

## Quand Utiliser Quoi ?

### 1. Skills (Domaine Technique)
**Utilise quand:** Tu veux définir "comment coder" dans un domaine
**Exemple:** Comment structurer une route FastAPI, comment faire du ML

**Caractéristiques:**
- < 500 lignes
- Patterns réutilisables
- Best practices
- Exemples de code
- Trade-offs

**Charge:** Automatiquement selon le contexte

### 2. Workflows (Séquences de Tâches)
**Utilise quand:** Tu veux guider l'implémentation d'une feature complète
**Exemple:** "Implémenter le système d'alertes de A à Z"

**Caractéristiques:**
- Étapes numérotées
- Références aux skills
- Critères d'acceptation
- Tests à faire

**Charge:** Manuellement via `/workflow [nom]` ou par référence

### 3. Commands (Actions Rapides)
**Utilise quand:** Action ponctuelle et répétitive
**Exemple:** "Ajouter un endpoint", "Créer un composant"

**Caractéristiques:**
- Très court (< 100 lignes)
- Action unique et claire
- Template/scaffold

**Charge:** Via `/[command-name]`

## Exemple Concret: Dashboard Setup

### ❌ Ancien (.prompts/F05-basic-dashboard-UPDATED.md)
```markdown
# F05 - Basic Dashboard

Tu vas créer un dashboard React qui:
1. Affiche les KPI de pollution
2. Utilise Chart.js pour les graphiques
3. Se connecte à l'API FastAPI
4. ...
[Instructions complètes mélangées]
```

### ✅ Nouveau (Approche hybride)

**Skills utilisés automatiquement:**
- `frontend-dashboard/SKILL.md` → Comment faire du React
- `backend-api/SKILL.md` → Comment structurer l'API

**Workflow créé:**
`.claude/workflows/dashboard-setup.md`
```markdown
# Workflow: Dashboard Setup

## Objectif
Créer le dashboard de base avec KPIs et graphiques

## Prérequis
- Backend API fonctionnel
- Frontend React initialisé

## Étapes

### 1. Créer la structure des pages
Utilise le skill `frontend-dashboard` pour créer:
- `src/pages/Dashboard.tsx`
- Suivre les patterns de composants fonctionnels

### 2. Créer les composants KPI
```bash
/create-component
```
Nom: KPICard
Props: title, value, unit, severity

### 3. Intégrer Chart.js
Référence: `frontend-dashboard/SKILL.md` section "Chart.js Integration"
...
```

## Migration Pratique

### Option 1: Migration Automatique (Recommandé)
Je peux créer les workflows automatiquement depuis tes prompts existants:
```bash
/migrate-prompts
```

### Option 2: Migration Manuelle
1. Identifie la nature du prompt (skill vs workflow)
2. Copie le contenu vers le bon endroit
3. Adapte le format
4. Référence les skills existants

### Option 3: Hybride (Meilleur)
1. Garde les skills génériques (déjà fait)
2. Crée des workflows pour les features complexes
3. Utilise commands pour les actions rapides
4. Garde les anciens prompts comme référence

## Avantages de la Migration

### Avant (.prompts)
- ❌ Tout rechargé à chaque fois
- ❌ Redondance entre prompts
- ❌ Contexte saturé rapidement
- ❌ Pas de réutilisation

### Après (Context Engineering)
- ✅ Chargement on-demand
- ✅ Patterns réutilisables
- ✅ Contexte optimisé
- ✅ Progressive disclosure
- ✅ Combinaison skills + workflows

## Recommandation Finale

**Garde les deux pendant la transition:**

1. **Utilise les skills** pour le code quotidien
2. **Crée des workflows** pour les features complexes (basés sur tes prompts F05-F11)
3. **Garde tes anciens prompts** dans `.prompts/` comme référence
4. **Migre progressivement** les prompts les plus utilisés

**Workflow type:**
```bash
# Dans ta conversation avec Claude:
"En utilisant le workflow dashboard-setup, aide-moi à créer le dashboard"

# Claude va:
1. Charger le workflow dashboard-setup.md
2. Activer automatiquement les skills frontend-dashboard et backend-api
3. Te guider étape par étape
4. Utiliser les patterns des skills pour le code
```

## Prochaine Étape

Veux-tu que je:
1. ✅ Crée le dossier `.claude/workflows/` ?
2. ✅ Migre tes prompts F05-F11 vers des workflows ?
3. ✅ Crée des skills pour la mobilité (F02b, F02c, F02d) ?
4. ✅ Génère un command `/migrate-prompts` automatique ?

Dis-moi ce que tu préfères !
