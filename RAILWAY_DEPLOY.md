# Déploiement Backend sur Railway - Guide Complet

## 📦 Fichiers de Configuration Créés

✅ `backend/railway.json` - Configuration Railway
✅ `backend/Procfile` - Commande de démarrage
✅ `backend/runtime.txt` - Version Python
✅ `backend/.railwayignore` - Fichiers à exclure

---

## 🚀 Méthode 1: Déploiement via Dashboard Railway (Recommandé)

### Étape 1: Créer un Projet Railway

1. Allez sur **https://railway.app**
2. Cliquez sur **Login with GitHub**
3. Autorisez Railway à accéder à vos repos
4. Cliquez sur **New Project**

### Étape 2: Déployer depuis GitHub

1. Sélectionnez **Deploy from GitHub repo**
2. Cherchez et sélectionnez: `Loudiyii/smartcity-platform`
3. Railway va détecter le repository

### Étape 3: Configurer le Service Backend

**Root Directory:**
```
backend
```

Railway détectera automatiquement:
- ✅ Python 3.11 (via `runtime.txt`)
- ✅ FastAPI avec Uvicorn (via `Procfile`)
- ✅ Dépendances (via `requirements.txt`)

### Étape 4: Ajouter les Variables d'Environnement

Dans Railway, allez dans **Variables** et ajoutez:

| Variable | Valeur | Obligatoire |
|----------|--------|-------------|
| `PORT` | `8000` | ✅ Oui |
| `SUPABASE_URL` | `https://vnznhsbjqxufvhasotid.supabase.co` | ✅ Oui |
| `SUPABASE_KEY` | Votre clé anon Supabase | ✅ Oui |
| `SUPABASE_SERVICE_KEY` | Votre service key Supabase | ⚠️ Si RLS |
| `AQICN_API_KEY` | Votre clé AQICN | ✅ Oui |
| `WEATHER_API_KEY` | Votre clé WeatherAPI | ✅ Oui |
| `IDFM_API_KEY` | Votre clé IDFM | ⚠️ Optionnel |
| `ALLOWED_ORIGINS` | `https://smartcity-esic.vercel.app` | ✅ Oui |
| `ENVIRONMENT` | `production` | ✅ Oui |
| `SECRET_KEY` | Générez avec `openssl rand -hex 32` | ✅ Oui |

**Où trouver vos clés API:**
- **Supabase**: https://supabase.com/dashboard → Project Settings → API
- **AQICN**: https://aqicn.org/api/
- **WeatherAPI**: https://www.weatherapi.com/my/
- **IDFM**: https://prim.iledefrance-mobilites.fr/

### Étape 5: Déployer

1. Cliquez sur **Deploy**
2. Attendez 3-5 minutes (build + deploy)
3. Railway génèrera une URL: `https://smartcity-backend-production.up.railway.app`

### Étape 6: Vérifier le Déploiement

Testez ces endpoints:
```bash
# Health check
curl https://votre-url.railway.app/health

# API docs (Swagger)
https://votre-url.railway.app/docs

# Air quality endpoint
curl https://votre-url.railway.app/api/v1/air-quality/current?city=Paris
```

---

## 🔧 Méthode 2: Déploiement via Railway CLI (Après redémarrage)

Après avoir redémarré Claude Code (pour activer MCP Railway):

```bash
# Se connecter
railway login

# Initialiser le projet
cd backend
railway init

# Lier au projet
railway link

# Ajouter les variables d'environnement
railway variables set SUPABASE_URL=https://vnznhsbjqxufvhasotid.supabase.co
railway variables set SUPABASE_KEY=your_key
railway variables set AQICN_API_KEY=your_key
railway variables set WEATHER_API_KEY=your_key
railway variables set ALLOWED_ORIGINS=https://smartcity-esic.vercel.app
railway variables set ENVIRONMENT=production

# Déployer
railway up
```

---

## 🔗 Connecter Frontend ↔ Backend

### 1. Obtenir l'URL Railway

Une fois déployé, Railway vous donnera une URL:
```
https://smartcity-backend-production.up.railway.app
```

### 2. Mettre à Jour Vercel

Allez sur **Vercel Dashboard** → **smartcity-esic** → **Settings** → **Environment Variables**

Ajoutez/Modifiez:
```
VITE_API_BASE_URL = https://smartcity-backend-production.up.railway.app
```

### 3. Redéployer le Frontend

```bash
cd frontend
vercel --prod
```

Ou depuis le dashboard Vercel → **Deployments** → **Redeploy**

---

## 🔐 Configurer CORS sur le Backend

Le backend est déjà configuré pour accepter les requêtes depuis:
```python
ALLOWED_ORIGINS = "https://smartcity-esic.vercel.app"
```

Si vous avez plusieurs domaines:
```
ALLOWED_ORIGINS = https://smartcity-esic.vercel.app,https://autre-domaine.com
```

---

## 📊 Monitoring Railway

### Logs en Temps Réel
```bash
railway logs
```

Ou dans le dashboard: **Deployments** → **View Logs**

### Métriques
- **CPU/RAM**: Onglet **Metrics**
- **Requêtes**: Onglet **Observability**

### Redémarrer le Service
```bash
railway restart
```

---

## 🐛 Troubleshooting

### Erreur: "Module not found"
**Solution**: Vérifier `requirements.txt` est complet
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### Erreur: "Port already in use"
**Solution**: Railway utilise `$PORT` automatiquement, c'est normal

### Erreur 500 sur les endpoints
**Solution**:
1. Vérifier les logs: `railway logs`
2. Vérifier les variables d'environnement
3. Tester en local d'abord

### Build échoue
**Solution**:
1. Vérifier `runtime.txt` (Python 3.11.7)
2. Vérifier `Procfile` (commande uvicorn)
3. Tester: `pip install -r requirements.txt` en local

---

## 💰 Pricing Railway

**Plan Gratuit:**
- $5 de crédits gratuits/mois
- 500 MB RAM
- 1 GB stockage
- Parfait pour un projet étudiant

**Plan Développeur ($5/mois):**
- $5 crédits + ce que vous payez
- Domaines personnalisés
- Plus de ressources

---

## ✅ Checklist Finale

- [ ] Backend déployé sur Railway
- [ ] Variables d'environnement configurées
- [ ] `/health` endpoint retourne `200 OK`
- [ ] `/docs` affiche Swagger UI
- [ ] Frontend met à jour `VITE_API_BASE_URL`
- [ ] Frontend redéployé
- [ ] Tester login/register fonctionne
- [ ] Tester dashboard charge les données
- [ ] Tester carte heatmap s'affiche

---

**Dernière mise à jour**: 2025-12-27
**Support Railway**: https://docs.railway.app
