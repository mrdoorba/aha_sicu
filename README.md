# Store ICU

Brand health evaluation system for assessing store performance and potential.

## Project Structure

```
store_health_bmad/
├── backend/          # FastAPI backend (Python)
├── frontend/         # React frontend (TypeScript)
├── infrastructure/   # Terraform IaC
└── .github/          # CI/CD workflows
```

## Getting Started

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Visit http://localhost:8000/health to verify.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173 to view the app.

## Tech Stack

- **Backend**: Python 3.14, FastAPI, UV
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **Database**: Neon PostgreSQL (asyncpg)
- **Auth**: Firebase Authentication
- **Infrastructure**: Google Cloud Run, Firebase Hosting, Terraform
