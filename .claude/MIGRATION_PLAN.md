# Plan de Migration Complet - .prompts → Context Engineering

## Vue d'Ensemble

Migration de 18 fichiers prompts vers structure Context Engineering optimisée.

## Statut Actuel

### ✅ Déjà Migrés (6 Skills de base)
| Ancien Prompt | Nouveau Skill | Statut |
|---------------|---------------|--------|
| F01-core-infrastructure.md | `backend-api/SKILL.md` | ✅ Créé (450 lignes) |
| F02-data-collection.md | `external-apis/SKILL.md` | ✅ Créé (380 lignes) |
| F03-iot-simulation.md | `iot-simulation/SKILL.md` | ✅ Créé (350 lignes) |
| F04-database-models.md | `database-schema/SKILL.md` | ✅ Créé (380 lignes) |
| - | `ml-predictions/SKILL.md` | ✅ Créé (400 lignes) |
| - | `frontend-dashboard/SKILL.md` | ✅ Créé (460 lignes) |

**Total:** 2,420 lignes de context technique réutilisable

---

## Phase 1: Skills Mobilité IDFM (F02b, F02c, F02d)

### 🔄 À Créer: 3 nouveaux skills

Ces prompts contiennent de la **connaissance technique spécialisée** → Skills

| Prompt Source | Nouveau Skill | Priorité | Estimation |
|---------------|---------------|----------|------------|
| F02b-mobility-data.md | `mobility-data/SKILL.md` | Haute | ~400 lignes |
| F02c-realtime-transport.md | `realtime-transport/SKILL.md` | Haute | ~380 lignes |
| F02d-isochrones-analysis.md | `isochrones/SKILL.md` | Moyenne | ~350 lignes |

#### Contenu Attendu

**mobility-data/SKILL.md:**
- Intégration API IDFM Traffic
- Intégration Vélib stations
- Patterns de cache pour APIs IDFM
- Modèles Pydantic pour mobilité
- Exemples requêtes IDFM

**realtime-transport/SKILL.md:**
- API temps réel IDFM
- WebSocket / Polling patterns
- Gestion des delays/disruptions
- Calcul prochains passages
- Format GTFS-RT

**isochrones/SKILL.md:**
- Calcul zones accessibles
- Intégration API routing
- Algorithmes isochrones
- Visualisation sur carte
- Cache des résultats

---

## Phase 2: Workflows Features (F05-F14)

### 🔄 À Créer: 8 workflows

Ces prompts sont des **séquences de tâches** → Workflows

| Prompt Source | Nouveau Workflow | Priorité | Statut |
|---------------|------------------|----------|--------|
| F05-basic-dashboard-UPDATED.md | `dashboard-setup.md` | Haute | ✅ Créé |
| F06-authentication-UPDATED.md | `authentication-setup.md` | Haute | ⬜ À créer |
| F07-ml-prediction-UPDATED.md | `ml-pipeline-setup.md` | Haute | ⬜ À créer |
| F08-advanced-dashboard-UPDATED.md | `advanced-features.md` | Moyenne | ⬜ À créer |
| F09-alerts-system-UPDATED.md | `alerts-implementation.md` | Moyenne | ⬜ À créer |
| F10-anomaly-detection-UPDATED.md | `anomaly-detection-setup.md` | Moyenne | ⬜ À créer |
| F11-pdf-reports-UPDATED.md | `pdf-reports-implementation.md` | Basse | ⬜ À créer |
| F12-F14-UPDATED.md | `final-touches.md` | Basse | ⬜ À créer |

#### Format des Workflows

Chaque workflow suivra ce template:
```markdown
# Workflow: [Nom]

## Objectif
Description concise

## Référence
- User Stories: US-XXX
- Ancien Prompt: .prompts/FXX-xxx.md
- Skills Utilisés: [liste]

## Prérequis
- [ ] Liste de checks

## Étapes
### 1. [Titre étape]
**Skill utilisé:** [skill-name]
[Instructions détaillées]
[Code exemples]

### 2. [Titre étape]
...

## Critères d'Acceptation
- [ ] Tests fonctionnels
- [ ] Tests techniques

## Dépannage
Problèmes courants et solutions

## Prochaines Étapes
Workflows suivants recommandés
```

---

## Phase 3: Optimisation & Documentation

### 🔄 Tâches finales

1. **Créer index des workflows**
   - `.claude/workflows/INDEX.md`
   - Carte de navigation entre workflows
   - Dépendances entre workflows

2. **Créer commandes supplémentaires**
   - `/start-workflow [name]` - Lance un workflow
   - `/list-skills` - Liste skills disponibles
   - `/migrate-feature [Fxx]` - Migre un ancien prompt

3. **Documenter la migration**
   - Guide utilisateur
   - Exemples d'utilisation
   - Comparaison avant/après

4. **Nettoyer anciens prompts (optionnel)**
   - Garder `.prompts/` comme archive
   - Ajouter liens vers nouveaux workflows
   - README avec mapping

---

## Calendrier de Migration

### Étape 1: Skills Mobilité (Priorité Haute)
**Durée:** ~30 min
- [ ] Créer `mobility-data/SKILL.md`
- [ ] Créer `realtime-transport/SKILL.md`
- [ ] Créer `isochrones/SKILL.md`

### Étape 2: Workflows Critiques (Priorité Haute)
**Durée:** ~45 min
- [x] `dashboard-setup.md` ✅
- [ ] `authentication-setup.md`
- [ ] `ml-pipeline-setup.md`

### Étape 3: Workflows Avancés (Priorité Moyenne)
**Durée:** ~30 min
- [ ] `advanced-features.md`
- [ ] `alerts-implementation.md`
- [ ] `anomaly-detection-setup.md`

### Étape 4: Workflows Finaux (Priorité Basse)
**Durée:** ~15 min
- [ ] `pdf-reports-implementation.md`
- [ ] `final-touches.md`

### Étape 5: Documentation & Cleanup
**Durée:** ~20 min
- [ ] INDEX.md
- [ ] Commandes supplémentaires
- [ ] Guide migration

**Total estimé:** ~2h30 pour migration complète

---

## Bénéfices Attendus

### Avant (Prompts)
```
18 fichiers prompts
~15,000 lignes au total
Chargement complet à chaque fois
Redondance entre prompts
```

### Après (Context Engineering)
```
9 Skills (domain knowledge)
  → ~3,500 lignes
  → Chargement on-demand

8 Workflows (task sequences)
  → ~4,000 lignes
  → Utilisation ponctuelle

= Réduction ~50% tokens utilisés
= Contexte mieux organisé
= Réutilisation maximale
```

---

## Prochaine Action

**Que veux-tu que je fasse maintenant ?**

### Option A: Migration Automatique Complète
Je crée automatiquement:
- ✅ 3 skills mobilité (F02b, F02c, F02d)
- ✅ 7 workflows restants (F06-F12)
- ✅ Documentation complète

**Durée:** ~10 minutes
**Commande:** "Lance la migration complète"

### Option B: Migration Progressive
Tu choisis l'ordre de migration:
1. D'abord les skills mobilité ?
2. D'abord les workflows critiques ?
3. Un prompt spécifique ?

**Commande:** "Migre d'abord [nom du prompt]"

### Option C: Migration Manuelle Guidée
Je te guide étape par étape pour chaque migration
Tu valides chaque transformation

**Commande:** "Guide-moi pour migrer [nom]"

---

**Quelle option préfères-tu ?** 🚀
