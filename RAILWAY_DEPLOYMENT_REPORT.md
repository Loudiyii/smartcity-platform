# Rapport d'investigation - Déploiement Railway

**Date**: 31 décembre 2025
**Projet**: smartcity-platform
**Service**: smartcity-platform
**Environnement**: production

## Problème initial

Le déploiement Railway échouait avec l'erreur:
```
Railpack could not determine how to build the app
```

## Investigation

### 1. Configuration conflictuelle

Le projet avait des fichiers de configuration Railway à deux endroits:
- **Racine** (`C:\Users\abder\Bureau\smartcity\`):
  - `nixpacks.toml` - Configuration Nixpacks
  - `railway.json` - Configuration Railway

- **Backend** (`C:\Users\abder\Bureau\smartcity\backend\`):
  - `railway.toml` - Configuration Railway (spécifie DOCKERFILE)
  - `railway.json` - Configuration Railway (spécifie NIXPACKS)
  - `Dockerfile` - Dockerfile fonctionnel

### 2. Erreurs rencontrées

#### Erreur 1: Variable Nix non définie
```
error: undefined variable 'pip'
at /app/.nixpacks/nixpkgs-5148520bfab61f99fd25fb9ff7bfbb50dad3c9db.nix:19:9:
```

**Cause**: Dans Nixpacks, `pip` n'est pas un package séparé, il est inclus avec Python.

**Solution**: Retirer `pip` de la liste `nixPkgs` dans `nixpacks.toml`:
```toml
[phases.setup]
nixPkgs = ["python311"]  # Retiré "pip"
```

#### Erreur 2: Commande pip introuvable
```
/bin/bash: line 1: pip: command not found
```

**Cause**: Nixpacks n'ajoute pas `pip` au PATH. Il faut utiliser `python -m pip`.

**Solution**: Modifier les commandes dans `nixpacks.toml` et `railway.json`:
```toml
[phases.install]
cmds = ["cd backend && python -m pip install -r requirements.txt"]

[start]
cmd = "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### 3. Solution finale

Le déploiement manuel via `railway up` depuis le dossier `backend/` a fonctionné car il utilise le **Dockerfile** au lieu de Nixpacks (via `railway.toml` dans backend/).

## Résultat

**Statut**: ✅ SUCCESS
**Deployment ID**: 2ccb06df-c854-408e-b0c9-7c7780619fb5
**URL**: https://smartcity-platform-production.up.railway.app
**Build time**: 65.36 secondes
**Builder utilisé**: DOCKERFILE

### Vérifications

1. **Healthcheck**: ✅ Réussi (`/health` retourne 200 OK)
2. **Services actifs**:
   - ✅ Uvicorn server (port 8080)
   - ✅ IoT Worker (5 capteurs simulés)
   - ✅ Anomaly Detection Worker
3. **Logs**: Application démarre correctement, capteurs envoient des données

## Recommandations

### Option 1: Utiliser Dockerfile (RECOMMANDÉ - Déjà actif)

Le Dockerfile dans `backend/` fonctionne parfaitement. C'est la solution actuellement active.

**Avantages**:
- Déploiement stable et prévisible
- Build rapide (~65 secondes)
- Contrôle total sur l'environnement
- Pas de problèmes de PATH avec pip/uvicorn

**Configuration active**:
- Fichier: `backend/railway.toml`
- Builder: DOCKERFILE
- Dockerfile: `backend/Dockerfile`

### Option 2: Corriger Nixpacks (Optionnel)

Si vous voulez utiliser Nixpacks depuis la racine:

1. **Supprimer les fichiers en conflit** dans `backend/`:
   ```bash
   rm backend/railway.toml backend/railway.json
   ```

2. **Utiliser les fichiers corrigés à la racine**:
   - `nixpacks.toml` (déjà corrigé avec `python -m pip`)
   - `railway.json` (déjà corrigé avec `python -m uvicorn`)

3. **Configurer le Root Directory** dans Railway settings:
   - Aller sur railway.app → Project → Service Settings
   - Définir "Root Directory" = `/` (racine)
   - Rebuild le service

**Note**: Cette option n'est pas nécessaire car le Dockerfile fonctionne déjà bien.

## Fichiers modifiés

### C:\Users\abder\Bureau\smartcity\nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["cd backend && python -m pip install -r requirements.txt"]

[phases.build]
cmds = ["echo 'No build needed'"]

[start]
cmd = "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### C:\Users\abder\Bureau\smartcity\railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd backend && python -m pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### C:\Users\abder\Bureau\smartcity\backend\Dockerfile (Déjà existant - ACTIF)
```dockerfile
# Backend Dockerfile for Railway deployment
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Railway provides PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
```

## Commits effectués

1. **e1dd818**: Fix: Remove pip from nixPkgs and add cd backend to commands
2. **b2378b6**: Fix: Use 'python -m pip' and 'python -m uvicorn' for Nixpacks

## Conclusion

Le problème de déploiement Railway a été résolu avec succès. L'application est maintenant déployée et fonctionnelle en utilisant le Dockerfile dans le dossier `backend/`. Les fichiers de configuration Nixpacks à la racine ont été corrigés mais ne sont pas utilisés actuellement (le service utilise le Dockerfile via `backend/railway.toml`).

L'API est accessible à: **https://smartcity-platform-production.up.railway.app**

Tous les services (API, workers IoT, détection d'anomalies) fonctionnent correctement.
