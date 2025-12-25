# MCP Servers Configuration Guide

## Serveurs installés

✅ **GitHub MCP** - Accès avancé aux repos, issues, PRs
✅ **Supabase MCP** - Connexion directe à ta base Supabase
✅ **Playwright MCP** - Automation web et scraping

---

## Configuration actuelle

### ✅ Tous les MCP servers sont configurés et prêts!

Les 3 serveurs MCP sont installés et configurés avec tes credentials:

- **GitHub MCP** → Token configuré ✅
- **Supabase MCP** → URL + Anon Key configurés ✅
- **Playwright MCP** → Prêt (aucune config requise) ✅

---

## Configuration des serveurs

### 1. GitHub MCP Server

**Status:** ✅ Configuré

**Configuration actuelle:**
```json
"github": {
  "command": "mcp-server-github",
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_***" (configuré)
  }
}
```

**Capacités:**
- Créer/éditer des issues
- Gérer des Pull Requests
- Lire/modifier des fichiers dans les repos
- Rechercher dans le code
- Gérer les GitHub Actions
- Lister branches, commits, releases

**Exemples d'utilisation:**
```
"Crée une issue pour implémenter les alertes email"
"Liste toutes les PR ouvertes sur le repo"
"Recherche tous les fichiers qui utilisent axios"
"Affiche les derniers commits du repo"
```

---

### 2. Supabase MCP Server

**Status:** ✅ Configuré

**Configuration actuelle:**
```json
"supabase": {
  "command": "mcp-server-supabase",
  "env": {
    "SUPABASE_URL": "https://vnznhsbjqxufvhasotid.supabase.co",
    "SUPABASE_ANON_KEY": "eyJ***" (configuré)
  }
}
```

**Capacités:**
- Lire/écrire dans les tables Supabase
- Exécuter des requêtes sur la base de données
- Gérer l'authentification
- Accéder au Storage (fichiers)
- Utiliser les Realtime features
- Appeler les Edge Functions

**Exemples d'utilisation:**
```
"Affiche les 10 dernières mesures de qualité de l'air"
"Compte combien de capteurs sont actifs dans sensor_metadata"
"Insère une nouvelle mesure dans air_quality_measurements"
"Liste tous les utilisateurs authentifiés"
"Récupère les fichiers uploadés dans le Storage"
```

**Avantage vs Postgres MCP:**
- API Supabase complète (pas seulement SQL)
- Accès au Storage, Auth, Realtime
- Plus adapté à ton stack actuel
- Pas besoin du mot de passe PostgreSQL

---

### 3. Playwright MCP Server

**Status:** ✅ Prêt

**Configuration:**
```json
"playwright": {
  "command": "mcp-playwright",
  "env": {}
}
```

**Capacités:**
- Naviguer sur des sites web
- Capturer des screenshots
- Remplir des formulaires automatiquement
- Extraire des données (web scraping)
- Tester des interfaces web
- Automatiser des workflows web
- Supporter Chrome, Firefox, Safari

**Exemples d'utilisation:**
```
"Va sur aqicn.org et récupère les données de pollution de Paris"
"Prends un screenshot de notre dashboard à localhost:5173"
"Teste le formulaire de login sur notre app"
"Scrape les prévisions météo sur meteofrance.com"
"Automatise le remplissage du formulaire de contact"
```

---

## Activation

### ⚡ Tout est déjà configuré!

Les 3 MCP servers sont installés et configurés. Pour les activer:

**Redémarre Claude Code:**
1. Ferme complètement Claude Code
2. Relance-le
3. Les MCP servers seront automatiquement chargés

**Vérification:**
Une fois redémarré, demande:
```
"Quels MCP servers sont actifs?"
```

Je devrais pouvoir confirmer que GitHub, Supabase et Playwright sont disponibles.

---

## Exemples concrets pour ton projet

### Scénario 1: Développement Features

**Avec GitHub MCP:**
```
"Crée une issue pour Phase 2: implémenter les prédictions ML PM2.5"
"Liste toutes les branches du repo smartcity"
"Crée une PR pour merge feature/dashboard dans main"
```

**Avec Supabase MCP:**
```
"Affiche la structure de la table air_quality_measurements"
"Compte combien de mesures ont été insérées aujourd'hui"
"Trouve les capteurs qui n'ont pas envoyé de données depuis 1 heure"
```

### Scénario 2: Testing & QA

**Avec Playwright MCP:**
```
"Va sur localhost:5173 et teste que le dashboard s'affiche correctement"
"Prends des screenshots du dashboard en mobile et desktop"
"Vérifie que les KPI cards affichent bien les données"
"Teste le workflow complet: login → dashboard → logout"
```

### Scénario 3: Monitoring & Debug

**Avec Supabase MCP:**
```
"Affiche les 20 dernières erreurs dans les logs"
"Trouve les mesures avec des valeurs PM2.5 anormales (> 200)"
"Vérifie que les 3 capteurs ont envoyé des données récentes"
```

**Avec GitHub MCP:**
```
"Recherche tous les TODO dans le code"
"Liste les issues ouvertes avec le tag 'bug'"
"Affiche l'historique de commits sur le fichier main.py"
```

---

## Troubleshooting

### MCP servers ne se chargent pas après redémarrage

**Solution 1 - Vérifier les logs:**
- Ouvre les logs Claude Code
- Cherche des erreurs liées aux MCP servers

**Solution 2 - Vérifier les commandes:**
```bash
# Teste si les commandes sont disponibles
which mcp-server-github
which mcp-server-supabase
which mcp-playwright
```

**Solution 3 - Réinstaller:**
```bash
npm install -g @modelcontextprotocol/server-github @supabase/mcp-server-supabase @ejazullah/mcp-playwright
```

### GitHub MCP - Erreur d'authentification

**Causes possibles:**
- ❌ Token expiré → Regénère un nouveau token sur GitHub
- ❌ Scopes insuffisants → Ajoute `repo`, `read:org`, `workflow`
- ❌ Token révoqué → Vérifie sur GitHub settings

**Solution:**
1. Va sur https://github.com/settings/tokens
2. Révoque l'ancien token
3. Crée un nouveau token avec tous les scopes
4. Mets à jour `.claude/mcp.json`

### Supabase MCP - Erreur de connexion

**Causes possibles:**
- ❌ URL incorrecte → Vérifie `SUPABASE_URL` dans `.env`
- ❌ Anon key invalide → Vérifie sur Supabase dashboard
- ❌ Projet Supabase paused → Réactive-le

**Solution:**
1. Va sur https://supabase.com/dashboard/project/vnznhsbjqxufvhasotid
2. Vérifie que le projet est actif
3. Settings → API → Copie l'URL et l'anon key
4. Mets à jour `.claude/mcp.json`

### Playwright MCP - Lent ou timeout

**Causes:**
- ℹ️ Première exécution télécharge Chromium (~100MB)
- ℹ️ Le navigateur prend du temps à démarrer

**Solutions:**
- Attends la fin du premier téléchargement
- Augmente le timeout dans les requêtes
- Utilise le mode headless (par défaut)

---

## Sécurité

⚠️ **IMPORTANT - Protège tes credentials:**

### 1. Gitignore configuré ✅

Le fichier `.gitignore` contient déjà:
```
.claude/mcp.json
```

Donc tes tokens ne seront JAMAIS committé sur Git.

### 2. Bonnes pratiques

**GitHub Token:**
- ✅ Utilise des tokens avec scopes minimaux
- ✅ Révoque les tokens non utilisés
- ✅ Renouvelle tous les 6 mois
- ❌ Ne partage JAMAIS ton token

**Supabase Keys:**
- ✅ Utilise l'anon key pour l'app (pas le service key)
- ✅ Configure les Row Level Security (RLS) policies
- ✅ Limite les permissions par rôle
- ❌ Ne commit JAMAIS le service key

**Variables d'environnement:**
```bash
# Dans .env (déjà en .gitignore)
GITHUB_TOKEN=ghp_***
SUPABASE_URL=https://***
SUPABASE_ANON_KEY=eyJ***
```

---

## Désactivation temporaire

Pour désactiver un MCP server sans le désinstaller:

**Option 1 - Commentaire dans JSON:**
```json
{
  "mcpServers": {
    // "github": { ... },  <- Commenté = désactivé
    "supabase": { ... },
    "playwright": { ... }
  }
}
```

**Option 2 - Renommer le fichier:**
```bash
mv .claude/mcp.json .claude/mcp.json.disabled
```

**Option 3 - Supprimer une entrée:**
Édite `.claude/mcp.json` et supprime le serveur.

---

## Mise à jour des MCP servers

Pour mettre à jour vers les dernières versions:

```bash
npm update -g @modelcontextprotocol/server-github
npm update -g @supabase/mcp-server-supabase
npm update -g @ejazullah/mcp-playwright
```

---

## Support & Documentation

**MCP Servers:**
- GitHub MCP: https://github.com/modelcontextprotocol/servers/tree/main/src/github
- Supabase MCP: https://github.com/supabase/mcp-server-supabase
- Playwright MCP: https://github.com/ejazullah/mcp-playwright

**Supabase:**
- Dashboard: https://supabase.com/dashboard/project/vnznhsbjqxufvhasotid
- Docs: https://supabase.com/docs
- API Docs: https://supabase.com/docs/reference/javascript

**GitHub:**
- Personal tokens: https://github.com/settings/tokens
- API Docs: https://docs.github.com/en/rest

---

## Checklist de configuration ✅

- [x] MCP servers installés (npm install -g)
- [x] GitHub token configuré dans mcp.json
- [x] Supabase credentials configurés dans mcp.json
- [x] Playwright prêt (aucune config requise)
- [x] mcp.json ajouté au .gitignore
- [x] Template mcp.json.example créé
- [ ] Claude Code redémarré pour charger les MCP servers

**Prochaine étape:** Redémarre Claude Code pour activer les 3 MCP servers! 🚀

---

**Dernière mise à jour:** 2024-12-24
**Serveurs:** GitHub (v2025.4.8), Supabase (v0.5.10), Playwright (v0.0.49)
**Status:** ✅ Tous configurés - Redémarrage requis
