# 🚀 Déployer Backend Railway - Guide Rapide

## Étape 1: Créer le Projet Railway (2 min)

1. **Ouvrez votre navigateur** et allez sur: **https://railway.app/new**

2. **Login** avec GitHub

3. **Deploy from GitHub repo**
   - Cherchez: `smartcity-platform`
   - Sélectionnez: `Loudiyii/smartcity-platform`

4. **Configure Service**
   - Root Directory: `backend`
   - Cliquez sur **Add variables**

---

## Étape 2: Ajouter Variables d'Environnement (3 min)

### Variables OBLIGATOIRES

Copiez-collez ces variables dans Railway (Settings → Variables):

```bash
# Supabase
SUPABASE_URL=https://vnznhsbjqxufvhasotid.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZuem5oc2JqcXh1ZnZoYXNvdGlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ1MjczODgsImV4cCI6MjA1MDEwMzM4OH0.JaGOKe4GKEVu2vEE_7X3qNqEHmJ-lzvFxN3PoKVjD4c

# APIs - REMPLACEZ PAR VOS CLÉS
AQICN_API_KEY=YOUR_KEY_HERE
WEATHER_API_KEY=YOUR_KEY_HERE

# Application
ENVIRONMENT=production
ALLOWED_ORIGINS=https://smartcity-esic.vercel.app
SECRET_KEY=your_generated_secret_key_here
```

### Où Trouver Vos Clés API

| API | URL | Gratuit? |
|-----|-----|----------|
| **AQICN** | https://aqicn.org/api/ | ✅ Oui |
| **WeatherAPI** | https://www.weatherapi.com/signup.aspx | ✅ Oui (1M calls/mois) |
| **IDFM** | https://prim.iledefrance-mobilites.fr/ | ⚠️ Optionnel |

### Générer SECRET_KEY

```bash
# Sur Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# Ou utilisez ce générateur:
# https://randomkeygen.com/ (Fort Passwords)
```

---

## Étape 3: Déployer (Automatique - 3 min)

1. Cliquez sur **Deploy**
2. Railway va:
   - ✅ Détecter Python 3.11
   - ✅ Installer dependencies
   - ✅ Lancer Uvicorn
   - ✅ Générer une URL

3. **Copiez l'URL** générée:
   ```
   https://smartcity-backend-production-XXXX.up.railway.app
   ```

---

## Étape 4: Vérifier le Déploiement

Testez ces URLs dans votre navigateur:

```
✅ Health: https://votre-url.railway.app/health
✅ Docs: https://votre-url.railway.app/docs
✅ API: https://votre-url.railway.app/api/v1/air-quality/current?city=Paris
```

Si tout fonctionne, vous verrez:
- `/health` → `{"status":"healthy"...}`
- `/docs` → Interface Swagger

---

## Étape 5: Connecter Frontend → Backend (2 min)

### Sur Vercel

1. Allez sur: **https://vercel.com/abderrahims-projects-0a2fe811/frontend/settings/environment-variables**

2. **Ajoutez** cette variable:
   ```
   Name: VITE_API_BASE_URL
   Value: https://votre-url.railway.app
   Environment: Production ✅
   ```

3. **Redéployez** le frontend:
   ```bash
   cd frontend
   vercel --prod
   ```

   Ou depuis le dashboard Vercel:
   - Deployments → Latest → ⋯ → Redeploy

---

## ✅ Test Final

1. **Ouvrez**: https://smartcity-esic.vercel.app

2. **Testez**:
   - ✅ Dashboard charge les données
   - ✅ Carte heatmap s'affiche
   - ✅ Créer un compte (/register)
   - ✅ Se connecter (/login)
   - ✅ Impact Mobilité affiche les graphiques

---

## 🐛 Problèmes Courants

### Erreur: "Module not found"
**Solution**: Vérifier `requirements.txt` contient toutes les dépendances

### Erreur 500 sur /health
**Solution**:
1. Vérifier logs Railway (Deployments → View Logs)
2. Vérifier `SUPABASE_URL` et `SUPABASE_KEY`

### Frontend: "Network Error"
**Solution**:
1. Vérifier `VITE_API_BASE_URL` sur Vercel
2. Vérifier `ALLOWED_ORIGINS` sur Railway
3. Redéployer frontend après changement

### CORS Error
**Solution**: Vérifier `ALLOWED_ORIGINS` contient EXACTEMENT:
```
https://smartcity-esic.vercel.app
```
(sans / à la fin)

---

## 📊 Monitoring

### Logs Railway
```bash
railway logs --tail 100
```

Ou Dashboard → Deployments → View Logs

### Metrics
Dashboard → Metrics:
- CPU usage
- RAM usage
- Request count

---

## 💰 Coûts Railway

**Gratuit**:
- $5 crédits/mois
- 500 MB RAM
- 1 GB storage
- Suffisant pour démo/projet étudiant

**Optimisations**:
- Backend: ~100-200 MB RAM
- Coût estimé: $0-2/mois

---

**Support**:
- Railway: https://docs.railway.app
- Discord Railway: https://discord.gg/railway
