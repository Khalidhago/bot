# HAGO UAS Intelligence & Support Bot

> An AI-powered technical support platform for UAV/UAS engineers, operators, and developers.

Built by [Hago Drone Consulting Services](https://github.com/Khalidhago).

---

## Overview

HAGO UAS Intelligence & Support Bot is a production-grade AI platform that provides:

- **Expert technical support** for PX4, ArduPilot, MAVLink, MAVSDK, and ROS 2
- **RAG-powered knowledge retrieval** from verified UAV/UAS documentation
- **Flight log analysis** for PX4 ULog and ArduPilot DataFlash logs
- **Code generation** in Python, C++, TypeScript, YAML, and Bash
- **Architecture diagrams** rendered in Mermaid
- **8 specialist modes**: General UAV Engineer, PX4 Specialist, ArduPilot Specialist, ROS 2 Engineer, AI/ML Engineer, Flight Log Analyst, System Architect, Hardware Integration Engineer

---

## Architecture

```
Frontend (Next.js)
        ↓
API Gateway (Nginx)
        ↓
FastAPI Application
  ├── Authentication (JWT + RBAC)
  ├── AI Orchestration (OpenAI / Anthropic / Google / Local)
  ├── UAV Domain Intelligence (PX4, ArduPilot, MAVLink, ROS 2)
  ├── RAG Knowledge System (pgvector)
  └── Flight Log Analysis Engine
        ↓
PostgreSQL + pgvector | Redis | Object Storage
```

---

## Quick Start

### Prerequisites

- Docker ≥ 24
- Docker Compose v2

### 1. Clone and configure

```bash
git clone https://github.com/Khalidhago/bot.git
cd bot/hago-uas-bot
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

Edit `apps/api/.env` and set at minimum:

```env
OPENAI_API_KEY=sk-...
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
```

### 2. Start all services

```bash
docker compose up --build
```

Services started:

| Service | URL |
|---|---|
| Web UI | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| PgAdmin | http://localhost:5050 |
| Redis | localhost:6379 |

### 3. Create admin user

```bash
docker compose exec api python -m app.cli create-admin \
  --email admin@example.com \
  --password changeme123
```

### 4. Ingest knowledge base

```bash
# Place PDF documents in docs/knowledge/
docker compose exec api python -m app.cli ingest-docs \
  --directory /app/knowledge
```

---

## Development (without Docker)

### Backend

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # configure your .env

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd apps/web
npm install
cp .env.example .env.local  # configure your .env.local
npm run dev
```

---

## Project Structure

```
hago-uas-bot/
├── apps/
│   ├── api/                    # FastAPI backend
│   └── web/                    # Next.js frontend
├── packages/
│   ├── shared-types/           # Shared TypeScript types
│   └── config/                 # Shared config schemas
├── infrastructure/
│   ├── docker/                 # Docker configs
│   └── kubernetes/             # K8s manifests
├── docs/                       # Architecture and guides
└── docker-compose.yml          # Full-stack local dev
```

---

## API Reference

Full OpenAPI documentation is available at `http://localhost:8000/docs` when running locally.

Key endpoints:

```
POST /api/v1/auth/register       Register a new user
POST /api/v1/auth/login          Login and get JWT tokens
POST /api/v1/chat                Send a chat message
GET  /api/v1/conversations       List conversations
POST /api/v1/documents/upload    Upload a knowledge document
POST /api/v1/flight-logs/analyze Analyze a flight log
GET  /api/v1/knowledge/search    Semantic search
GET  /api/v1/health              Health check
```

---

## Running Tests

### Backend

```bash
cd apps/api
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Frontend

```bash
cd apps/web
npm run test
```

---

## Documentation

| Document | Description |
|---|---|
| [Project Requirements](docs/PROJECT_REQUIREMENTS.md) | Functional and non-functional requirements |
| [System Architecture](docs/SYSTEM_ARCHITECTURE.md) | Architecture diagrams and component design |
| [Technology Decisions](docs/TECHNOLOGY_DECISIONS.md) | Stack choices and rationale |
| [Development Roadmap](docs/DEVELOPMENT_ROADMAP.md) | Phase plan and risk register |

---

## License

[MIT](../LICENSE)
