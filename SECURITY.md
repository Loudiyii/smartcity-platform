# Security & Configuration

## 🔒 Protected Files

The following files contain sensitive credentials and are **NOT tracked** in this repository:

### Backend
- `backend/.env` - Contains:
  - Supabase credentials (URL, keys)
  - API keys (WeatherAPI, AQICN, IDFM)
  - JWT secret key
  - SMTP credentials

### Frontend
- `frontend/.env` - Contains:
  - API base URL configuration

### Claude Code MCP
- `.claude/mcp.json` - Contains:
  - GitHub personal access token
  - Supabase connection credentials
  - MCP server configuration

## ⚙️ Setup Instructions

### 1. Backend Configuration

```bash
cd backend
cp .env.example .env
# Edit .env with your actual credentials
```

Required credentials:
- **Supabase**: Get from https://supabase.com/dashboard
- **WeatherAPI**: Get from https://www.weatherapi.com/
- **AQICN**: Get from https://aqicn.org/data-platform/token/
- **IDFM**: Get from https://prim.iledefrance-mobilites.fr/

### 2. Frontend Configuration

```bash
cd frontend
cp .env.example .env
# Edit if your backend runs on a different port
```

### 3. MCP Configuration (Optional)

```bash
cp .claude/mcp.json.example .claude/mcp.json
# Edit with your tokens
```

MCP servers available:
- **GitHub MCP**: Create token at https://github.com/settings/tokens
- **Supabase MCP**: Use same credentials as backend
- **Playwright MCP**: No configuration needed

## 🚫 Never Commit

**NEVER commit these files:**
- ❌ `backend/.env`
- ❌ `frontend/.env`
- ❌ `.claude/mcp.json`
- ❌ `node_modules/`
- ❌ `__pycache__/`
- ❌ `venv/`

These are already in `.gitignore` for protection.

## 🔐 GitHub Token Scopes

If using GitHub MCP, your token needs:
- `repo` - Full repository access
- `read:org` - Read organization data
- `workflow` - Manage GitHub Actions

## 📦 Dependencies Installation

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## 🗄️ Database Setup

1. Create a Supabase project
2. Run the schema:
   - Go to SQL Editor in Supabase dashboard
   - Copy content of `backend/database/schema.sql`
   - Execute the SQL

## 🚀 Running the Application

See [PHASE1_SETUP.md](PHASE1_SETUP.md) for complete setup instructions.

## 🛡️ Security Best Practices

1. **Rotate tokens regularly** (every 6 months minimum)
2. **Use different credentials** for dev/staging/production
3. **Enable 2FA** on GitHub and Supabase accounts
4. **Review Supabase RLS policies** before production
5. **Never share `.env` files** via email/chat/screenshots

## 📧 Security Issues

If you discover a security vulnerability, please email:
**security@smartcity.local**

Do NOT create a public issue.

---

**Last Updated:** 2024-12-24
**Security Level:** Private Repository
