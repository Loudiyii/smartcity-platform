# Quick Start Guide - Smart City Project

## What You Have Now

Your Smart City project has been scaffolded with a complete **Context Engineering** structure optimized for Claude Code. This setup will help Claude understand and work with your codebase more efficiently.

## Project Structure

```
C:\Users\abder\Bureau\smartcity\
├── .claude/                    # Claude Code Configuration
│   ├── skills/                 # Specialized knowledge modules
│   │   ├── backend-api/        # FastAPI development patterns
│   │   ├── ml-predictions/     # ML model training & predictions
│   │   ├── frontend-dashboard/ # React components & UI
│   │   ├── database-schema/    # Supabase/PostgreSQL queries
│   │   ├── iot-simulation/     # Sensor data generation
│   │   └── external-apis/      # AQICN & OpenWeather integration
│   ├── commands/               # Quick action slash commands
│   │   ├── add-api-route.md
│   │   ├── create-component.md
│   │   ├── run-ml-training.md
│   │   └── test-sensors.md
│   └── CLAUDE.md              # Main project context
│
├── backend/                    # FastAPI backend (ready to code)
├── frontend/                   # React frontend (ready to code)
├── docs/                       # Documentation directory
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
└── QUICK_START.md             # This file
```

## How to Use Skills

Skills are loaded on-demand when you're working on specific tasks. Claude will automatically activate the relevant skill based on your request.

### Example Workflow

1. **Working on Backend API:**
   - Just start asking: "Create a new endpoint for retrieving sensor data"
   - Claude will use the `backend-api` skill automatically

2. **Training ML Model:**
   - Ask: "Help me train the PM2.5 prediction model"
   - The `ml-predictions` skill activates with complete context

3. **Building Frontend:**
   - Request: "Create a KPI card component for displaying air quality"
   - The `frontend-dashboard` skill provides React patterns

## Using Slash Commands

Quick commands for common tasks:

```bash
/add-api-route       # Scaffold a new FastAPI endpoint
/create-component    # Generate a React component
/run-ml-training     # Train the prediction model
/test-sensors        # Test IoT sensor simulation
```

## Next Steps

### 1. Set Up Your Environment

**Backend:**
```bash
cd C:\Users\abder\Bureau\smartcity\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

**Frontend:**
```bash
cd C:\Users\abder\Bureau\smartcity\frontend
npm install
cp .env.example .env
# Edit .env with backend URL
```

### 2. Get API Keys

**AQICN (Air Quality):**
- Visit: https://aqicn.org/api/
- Request free token (instant)

**OpenWeatherMap:**
- Visit: https://openweathermap.org/api
- Sign up and get API key

**Supabase:**
- Visit: https://supabase.com
- Create project
- Get URL and keys from project settings

### 3. Start Developing

#### Option A: Start Backend First
```bash
cd backend
uvicorn app.main:app --reload
```
Then visit: http://localhost:8000/docs

#### Option B: Start Frontend First
```bash
cd frontend
npm run dev
```
Then visit: http://localhost:5173

#### Option C: Ask Claude for Help!
Just ask Claude to help you with any specific task:
- "Help me set up the backend API structure"
- "Create the main dashboard page"
- "Implement the sensor simulator"
- "Set up the Supabase database schema"

## How Context Engineering Helps You

### Traditional Approach (Without Skills)
❌ Claude has to learn your project structure every conversation
❌ Inconsistent coding patterns
❌ Repeated explanations needed
❌ Context overload with large codebases

### With Context Engineering (Your Setup)
✅ Skills loaded on-demand (< 500 lines each)
✅ Consistent patterns enforced
✅ Faster development with less explanation
✅ Efficient context usage
✅ Progressive disclosure of information

## Skills Overview

| Skill | Lines | Purpose | When Activated |
|-------|-------|---------|----------------|
| **backend-api** | ~450 | FastAPI patterns, Pydantic, services | Working on backend routes |
| **ml-predictions** | ~400 | ML training, predictions, anomaly detection | ML-related tasks |
| **frontend-dashboard** | ~460 | React, TypeScript, Chart.js, Leaflet | Frontend development |
| **database-schema** | ~380 | SQL, RLS, indexes, queries | Database work |
| **iot-simulation** | ~350 | Sensor simulation, data generation | Testing, simulation |
| **external-apis** | ~380 | AQICN, OpenWeather integration | API integration |

**Total:** ~2,420 lines of focused, reusable context
**Benefit:** Only relevant context loaded when needed

## Documentation

- **Main Context:** `.claude/CLAUDE.md` - Project overview and standards
- **Technical Specs:** `docs/TECHNICAL.md` - Detailed architecture (from original)
- **Functional Specs:** `docs/fonctionnel.md` - Requirements (from original)
- **README:** `README.md` - Project documentation

## Tips for Working with Claude

1. **Be specific about your task:**
   - ✅ "Create a FastAPI endpoint for air quality history"
   - ❌ "Help me with the backend"

2. **Reference files/skills when needed:**
   - "Using the backend-api skill, add a new route..."
   - "Following the ml-predictions patterns, train a model..."

3. **Use slash commands for speed:**
   - `/add-api-route` instead of explaining the whole process

4. **Let skills guide patterns:**
   - Skills contain best practices and trade-offs
   - Follow the patterns for consistency

## Common Questions

**Q: Do I need to load skills manually?**
A: No! Claude automatically activates relevant skills based on your request.

**Q: Can I modify skills?**
A: Yes! Edit any `.claude/skills/*/SKILL.md` file to customize patterns.

**Q: What if I need new skills?**
A: Create a new folder in `.claude/skills/` with a `SKILL.md` file.

**Q: How do I update the main context?**
A: Edit `.claude/CLAUDE.md` to add project-wide information.

## Getting Help

If you need help:
1. Ask Claude specific questions about your task
2. Reference the skill name if Claude seems off-track
3. Check the SKILL.md files for examples and patterns
4. Review docs/TECHNICAL.md for detailed architecture

## Project Status

- ✅ Project structure created
- ✅ Skills configured
- ✅ Starter files generated
- ⬜ Environment setup (your next step)
- ⬜ Development begins

---

**You're Ready to Build! 🚀**

Start by asking Claude to help you with your first task, whether that's:
- Setting up the backend API
- Creating the database schema
- Building the dashboard UI
- Implementing the ML model
- Simulating IoT sensors

Claude now has all the context needed to help you efficiently!
