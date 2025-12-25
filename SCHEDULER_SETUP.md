# 🤖 Automated Data Collection Setup

## Solution: GitHub Actions Cron Jobs

**Pourquoi GitHub Actions?**
- ✅ **100% Gratuit** (2000 min/mois pour repos privés)
- ✅ **Serverless** - Pas besoin de serveur/PC allumé
- ✅ **Fiable** - Infrastructure GitHub (99.9% uptime)
- ✅ **Simple** - Configuration YAML
- ✅ **Sécurisé** - Secrets chiffrés
- ✅ **Logs** - Historique complet

---

## 📊 Architecture

```
     ⏰ Toutes les heures (00:00, 01:00, 02:00...)
                    │
                    ▼
     ┌──────────────────────────────────┐
     │   GitHub Actions Runner          │
     │   (Ubuntu, Python 3.11)          │
     │                                  │
     │   scripts/collect_data.py        │
     │   ├─ Fetch AQICN API            │──┐
     │   ├─ Fetch WeatherAPI           │──┤
     │   └─ Save to Supabase           │  │
     └──────────────────────────────────┘  │
                                           │
                   ┌───────────────────────┴────────────────┐
                   │                                        │
                   ▼                                        ▼
         ┌─────────────────┐                    ┌──────────────────┐
         │   AQICN API     │                    │  WeatherAPI      │
         │                 │                    │                  │
         │  Air Quality    │                    │  Météo           │
         │  (PM2.5, AQI..) │                    │  (Temp, Vent...) │
         └─────────────────┘                    └──────────────────┘
                   │                                        │
                   └────────────────┬───────────────────────┘
                                    ▼
                         ┌────────────────────┐
                         │   Supabase DB      │
                         │                    │
                         │  • air_quality     │
                         │  • weather_data    │
                         └────────────────────┘
```

---

## 🚀 Setup Instructions (5 minutes)

### Étape 1: Configurer les Secrets GitHub

1. Va sur ton repo: **https://github.com/Loudiyii/smartcity-platform**

2. Clique sur **Settings** → **Secrets and variables** → **Actions**

3. Clique **New repository secret** et ajoute ces 4 secrets:

| Nom du Secret | Valeur | Où la trouver |
|--------------|--------|---------------|
| `SUPABASE_URL` | `https://vnznhsbjqxufvhasotid.supabase.co` | Supabase Dashboard → Settings → API → Project URL |
| `SUPABASE_KEY` | `eyJhbGc...` (ton anon key) | Supabase Dashboard → Settings → API → anon/public |
| `AQICN_API_TOKEN` | `1730a2f22f4d0ce...` (ton token) | https://aqicn.org/data-platform/token/ |
| `WEATHERAPI_KEY` | `f7c6e378f31c44c3...` (ta clé) | https://www.weatherapi.com/my/ |

**IMPORTANT:** Copie-colle exactement les valeurs sans espaces!

### Étape 2: Commit et Push le Code

Les fichiers sont déjà créés localement, il faut juste les pousser sur GitHub:

```bash
cd "C:\Users\abder\Bureau\smartcity"

# Ajouter les nouveaux fichiers
git add .github/workflows/collect-data.yml
git add scripts/collect_data.py
git add scripts/requirements.txt
git add scripts/README.md
git add SCHEDULER_SETUP.md

# Commit
git commit -m "Add GitHub Actions cron for automated data collection

- Workflow runs every hour to collect air quality & weather data
- Standalone Python script (no backend needed)
- Fetches from AQICN and WeatherAPI
- Saves directly to Supabase
- Auto-creates GitHub issue on failure
- 100% serverless solution"

# Push
git push
```

### Étape 3: Activer GitHub Actions

1. Va sur ton repo sur GitHub
2. Clique sur l'onglet **Actions**
3. Si GitHub Actions est désactivé, clique **"I understand my workflows, go ahead and enable them"**

### Étape 4: Tester Manuellement (Recommandé)

Avant d'attendre la première exécution horaire, teste manuellement:

1. Va sur **Actions** tab
2. Clique sur **"Collect Air Quality & Weather Data"** (dans la liste à gauche)
3. Clique **"Run workflow"** (bouton bleu à droite)
4. Sélectionne la branch `main`
5. Clique **"Run workflow"** (dans le popup)

👀 **Tu verras le workflow en cours d'exécution!**

Attends 30-60 secondes, puis:
- Clique sur le workflow en cours
- Clique sur le job `collect-data`
- Regarde les logs en temps réel

**Résultat attendu:**
```
🌍 Smart City - Data Collection
📅 2024-12-25 19:00:00 UTC
======================================================================
✅ Supabase client initialized

📍 Processing PARIS...
✅ Saved air quality data for Paris: PM2.5=45.0, AQI=120
✅ Saved weather data for Paris: 12.5°C, 75% humidity

📍 Processing LYON...
✅ Saved air quality data for Lyon: PM2.5=38.0, AQI=105
✅ Saved weather data for Lyon: 10.2°C, 80% humidity

📍 Processing MARSEILLE...
✅ Saved air quality data for Marseille: PM2.5=32.0, AQI=95
✅ Saved weather data for Marseille: 15.8°C, 65% humidity

======================================================================
📊 Collection Summary:
   ✅ Successful: 6
   ❌ Errors: 0
   🏙️  Cities processed: 3
======================================================================
```

### Étape 5: Vérifier les Données dans Supabase

1. Va sur ton projet Supabase
2. Clique **Table Editor** → `air_quality_measurements`
3. Tu devrais voir de nouvelles lignes avec `source = 'AQICN'`
4. Vérifie que le timestamp correspond à l'heure actuelle

---

## ⏱️ Calendrier d'Exécution

**Fréquence:** **Toutes les heures** (à la minute 00)

**Exemples:**
- 00:00 UTC
- 01:00 UTC
- 02:00 UTC
- ... 23:00 UTC

**Données collectées par jour:**
- 3 villes × 24 heures = **72 mesures air quality**
- 3 villes × 24 heures = **72 mesures météo**
- **Total: 144 mesures/jour**

**Données collectées par mois:**
- 144 × 30 jours = **~4,320 mesures**

**Stockage Supabase:**
- Gratuit jusqu'à 500 MB
- Chaque mesure ≈ 200 bytes
- 4,320 mesures × 200 bytes = **~0.86 MB/mois**
- ✅ **Largement dans le free tier!**

---

## 📈 Monitoring & Maintenance

### Voir l'Historique des Exécutions

1. GitHub → Actions → "Collect Air Quality & Weather Data"
2. Liste de toutes les exécutions (succès ✅ ou échec ❌)
3. Clique sur une exécution pour voir les détails

### Notifications d'Échec

Si la collecte échoue:
- ❌ Le workflow crée automatiquement une **GitHub Issue**
- 📧 Tu reçois une notification email (si activé dans GitHub)
- Issue contient:
  - Timestamp de l'échec
  - Lien vers les logs
  - Labels: `automated`, `data-collection`, `bug`

### Vérifier les Données

**Via Supabase Dashboard:**
```sql
-- Dernières mesures
SELECT source, city, pm25, aqi, timestamp
FROM air_quality_measurements
WHERE source = 'AQICN'
ORDER BY timestamp DESC
LIMIT 20;

-- Fréquence de collecte
SELECT
  DATE_TRUNC('hour', timestamp) as hour,
  COUNT(*) as count
FROM air_quality_measurements
WHERE source = 'AQICN'
GROUP BY hour
ORDER BY hour DESC
LIMIT 24;
```

**Via API:**
```bash
curl "http://localhost:8000/api/v1/air-quality/history?city=Paris&limit=10"
```

---

## 🎛️ Personnalisation

### Changer la Fréquence

Édite `.github/workflows/collect-data.yml`:

```yaml
schedule:
  # Toutes les heures (actuel)
  - cron: '0 * * * *'

  # Autres options:
  # Toutes les 30 minutes
  - cron: '*/30 * * * *'

  # Toutes les 3 heures
  - cron: '0 */3 * * *'

  # 2 fois par jour (midi et minuit)
  - cron: '0 0,12 * * *'

  # Une fois par jour à 8h du matin
  - cron: '0 8 * * *'
```

**⚠️ Limite GitHub:** Minimum 5 minutes entre chaque exécution

### Ajouter Plus de Villes

Édite `scripts/collect_data.py`:

```python
# Ligne 17-18
CITIES = [
    'paris',
    'lyon',
    'marseille',
    'toulouse',  # Ajouté
    'nice',      # Ajouté
    'nantes',    # Ajouté
]
```

### Changer la Source de Données

**Pour utiliser une autre API d'air quality:**

Modifie la fonction `fetch_aqicn_data()` dans `scripts/collect_data.py`

**Pour ajouter d'autres types de données:**

Ajoute une nouvelle fonction, par exemple:
```python
def fetch_traffic_data(city: str) -> Optional[dict]:
    # Fetch traffic/mobility data
    pass
```

---

## 💰 Coûts & Limites

### GitHub Actions (Free Tier)

| Ressource | Limite Gratuite | Usage Actuel | Status |
|-----------|----------------|--------------|--------|
| Minutes/mois | 2,000 | ~720 (30s × 24h × 30j) | ✅ 36% |
| Storage | 500 MB | < 1 MB | ✅ < 1% |
| Concurrent jobs | 20 | 1 | ✅ 5% |

### APIs Externes

| API | Limite Gratuite | Usage Actuel | Status |
|-----|----------------|--------------|--------|
| AQICN | 1,000 req/jour | 72 req/jour | ✅ 7% |
| WeatherAPI | 1M req/mois | 2,160 req/mois | ✅ 0.2% |

### Supabase (Free Tier)

| Ressource | Limite Gratuite | Usage Estimé | Status |
|-----------|----------------|--------------|--------|
| Database | 500 MB | ~26 MB/an | ✅ 5% |
| API requests | 50K/jour | ~150/jour | ✅ 0.3% |
| Bandwidth | 2 GB/mois | ~10 MB/mois | ✅ 0.5% |

✅ **Tout est largement dans les limites gratuites!**

---

## 🐛 Troubleshooting

### Erreur: "Secret not found"

**Cause:** Secret mal configuré dans GitHub

**Solution:**
1. Va sur Settings → Secrets → Actions
2. Vérifie que les 4 secrets existent
3. Noms doivent être EXACTEMENT: `SUPABASE_URL`, `SUPABASE_KEY`, `AQICN_API_TOKEN`, `WEATHERAPI_KEY`
4. Pas d'espaces avant/après les valeurs

### Erreur: "Failed to save data"

**Cause:** Problème de permissions Supabase

**Solution:**
1. Vérifie que `SUPABASE_KEY` est bien l'**anon key** (pas le service key)
2. Va sur Supabase → Authentication → Policies
3. Vérifie que RLS permet les INSERT sur `air_quality_measurements`

### Erreur: "API rate limit exceeded"

**Cause:** Trop de requêtes API

**Solution:**
1. Réduis le nombre de villes
2. Augmente l'intervalle (ex: toutes les 3h au lieu de 1h)
3. Ou upgrade le plan API

### Workflow ne se déclenche pas

**Cause:** Branch par défaut incorrecte

**Solution:**
1. Le workflow doit être sur la branch `main`
2. Vérifie: Settings → General → Default branch = `main`
3. Si besoin, merge dans `main`

---

## 🎯 Prochaines Étapes

Une fois le système en place:

1. **Laisse tourner 7 jours** pour accumuler de l'historique
2. **Vérifie quotidiennement** les premières 48h
3. **Après 1 semaine:** Tu auras assez de données pour:
   - Entraîner le modèle ML de prédiction
   - Créer des analyses de tendances
   - Générer des rapports hebdomadaires

**Données nécessaires pour Phase 2 (ML):**
- Minimum: 30 jours (720 mesures par ville)
- Idéal: 6 mois (4,320 mesures par ville)
- Pour entraîner Random Forest avec précision > 70%

---

## ✅ Checklist de Setup

- [ ] Secrets GitHub configurés (4 secrets)
- [ ] Code poussé sur GitHub (`git push`)
- [ ] GitHub Actions activé (onglet Actions)
- [ ] Test manuel effectué (workflow ran successfully)
- [ ] Données vérifiées dans Supabase
- [ ] Première exécution horaire automatique confirmée
- [ ] Notifications configurées (optionnel)

**Une fois tous cochés → Le système tourne automatiquement! 🎉**

---

## 📞 Support

**Problèmes?**
- Logs GitHub Actions: Actions tab → Click sur run → Expand steps
- Logs Supabase: Dashboard → Logs
- Check API status: [AQICN Status](https://aqicn.org/), [WeatherAPI Status](https://www.weatherapi.com/)

---

**Status:** 🚧 À configurer
**Temps de setup:** ~5 minutes
**Maintenance:** Aucune (100% automatique)
**Dernière mise à jour:** 2024-12-25
