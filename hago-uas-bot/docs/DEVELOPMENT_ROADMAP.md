# HAGO UAS Intelligence & Support Bot — Development Roadmap

## MVP Definition

The MVP delivers a working AI chat interface for UAV/UAS engineers with:

- User authentication (register + login)
- Streaming AI chat with UAV domain expertise
- PX4 and ArduPilot specialist modes
- Knowledge base with at least one verified technical source
- Flight log upload and basic anomaly detection
- Document upload and semantic search
- Professional dark-mode web UI
- Docker Compose local deployment

**Not in MVP:** Kubernetes, multi-tenancy, billing, mobile app, analytics dashboard.

---

## Phase 1 — Discovery ✅

**Goal:** Establish clear requirements, architecture, and technical decisions before any code.

Deliverables:
- `docs/PROJECT_REQUIREMENTS.md`
- `docs/SYSTEM_ARCHITECTURE.md`
- `docs/TECHNOLOGY_DECISIONS.md`
- `docs/DEVELOPMENT_ROADMAP.md`

---

## Phase 2 — Repository Initialization ✅

**Goal:** Create monorepo skeleton with all tooling configured.

Deliverables:
- Monorepo directory structure
- Root `README.md`
- `.env.example` files for API and web
- `docker-compose.yml` full stack
- ESLint + Prettier (frontend)
- Ruff + mypy (backend)
- `.gitignore` updates
- GitHub Actions workflow skeleton

---

## Phase 3 — Backend Foundation

**Goal:** Running FastAPI application that connects to DB and passes health check.

Deliverables:
- `app/main.py` — FastAPI factory with lifespan
- `app/core/config.py` — typed settings
- `app/core/logging.py` — structured logging
- `app/core/exceptions.py` — global exception handlers
- `app/core/middleware.py` — request ID, CORS, audit
- `app/database.py` — async SQLAlchemy + session management
- `app/api/v1/health.py` — `/health` and `/ready` endpoints
- Alembic initial migration

Test: `GET /api/v1/health` returns `{"status": "ok"}`.

---

## Phase 4 — Authentication

**Goal:** Working user registration, login, JWT issuance, and RBAC.

Deliverables:
- `app/models/user.py`
- `app/schemas/auth.py`
- `app/core/security.py` — bcrypt, JWT create/verify
- `app/services/auth_service.py`
- `app/repositories/user_repository.py`
- `app/api/v1/auth.py` — `/register`, `/login`, `/refresh`, `/me`
- Role dependency injection for protected endpoints

Test: Register → Login → access protected endpoint → refresh token.

---

## Phase 5 — AI Orchestration

**Goal:** Provider-agnostic AI with streaming responses and conversation memory.

Deliverables:
- `app/agents/providers/base_provider.py`
- `app/agents/providers/openai_provider.py`
- `app/agents/providers/anthropic_provider.py`
- `app/agents/ai_router.py`
- `app/agents/conversation_engine.py`
- `app/models/conversation.py`, `message.py`
- `app/api/v1/chat.py` — REST + WebSocket endpoints
- `app/services/chat_service.py`

Test: Send message → receive streamed AI response with UAV context.

---

## Phase 6 — UAV Domain Intelligence

**Goal:** Specialist modes that inject domain-specific context and prompt templates.

Deliverables:
- `app/uav/domain_classifier.py`
- `app/uav/prompt_library.py`
- `app/uav/px4/px4_module.py`
- `app/uav/ardupilot/ardupilot_module.py`
- `app/uav/mavlink/mavlink_module.py`
- `app/uav/ros2/ros2_module.py`
- `app/uav/airframes/airframe_module.py`
- `app/uav/computer_vision/cv_module.py`
- `app/api/v1/uav.py`

Test: Ask a PX4 parameter question → receive PX4-specific structured answer.

---

## Phase 7 — RAG Knowledge System

**Goal:** Upload documents, index them, and use retrieval to ground AI answers.

Deliverables:
- `app/rag/document_ingestion.py`
- `app/rag/chunking.py`
- `app/rag/embeddings.py`
- `app/rag/vector_store.py`
- `app/rag/retriever.py`
- `app/rag/reranker.py`
- `app/models/document.py`, `document_chunk.py`
- `app/api/v1/documents.py`
- `app/api/v1/knowledge.py`
- Background Celery task for ingestion

Test: Upload PX4 parameter reference → ask about a parameter → answer cites the document.

---

## Phase 8 — Flight Log Analysis

**Goal:** Upload flight logs and receive structured diagnostic reports.

Deliverables:
- `app/log_analysis/parsers/ulog_parser.py`
- `app/log_analysis/parsers/dataflash_parser.py`
- `app/log_analysis/parsers/csv_parser.py`
- `app/log_analysis/anomaly_detector.py`
- `app/log_analysis/report_generator.py`
- `app/models/flight_log.py`
- `app/api/v1/flight_logs.py`

Test: Upload sample ULog → receive diagnostic report with GPS/battery/motor checks.

---

## Phase 9 — Frontend

**Goal:** Professional web UI with chat, streaming, file uploads, diagrams.

Deliverables:
- Next.js project scaffold
- Auth pages (login, register)
- Dashboard page
- Chat workspace with streaming + Mermaid + code blocks
- Mode selector (8 specialist modes)
- Document upload page
- Flight log upload + analysis view
- Knowledge base explorer
- Responsive dark-mode design

Test: Full user flow end-to-end in the browser.

---

## Phase 10 — Testing, CI/CD, and Hardening

**Goal:** Automated validation, security hardening, deployment docs.

Deliverables:
- Unit tests for all services and domain modules (≥ 80% coverage)
- Integration tests for all API endpoints
- GitHub Actions: lint → type-check → test → build → Docker push
- Security: rate limiting, input validation, prompt injection tests
- Prometheus `/metrics` endpoint
- `docs/DEPLOYMENT.md`
- `docs/SECURITY.md`
- `docs/API_REFERENCE.md`
- `docs/USER_GUIDE.md`

---

## Production Roadmap (Post-MVP)

| Version | Features |
|---|---|
| v1.1 | Kubernetes Helm chart, Terraform IaC, multi-region |
| v1.2 | Organization accounts, team workspaces, sharing |
| v1.3 | Fine-tuned UAV domain model, custom embeddings |
| v1.4 | Fleet operations assistant (real-time telemetry) |
| v1.5 | AI mission planning assistant |
| v2.0 | Enterprise: SSO, audit compliance, SLA, white-labeling |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AI provider outage | Medium | High | Multi-provider routing + graceful fallback |
| pgvector performance at scale | Low | Medium | HNSW index; Weaviate migration path documented |
| Prompt injection | High | High | Input sanitization, output filtering, system prompt hardening |
| Inaccurate UAV technical answers | Medium | High | RAG grounding + confidence scoring + source citation |
| GDPR / data privacy | Medium | High | Data residency config, PII scrubbing, deletion API |
| API key exposure | Low | Critical | Secret scanning in CI, env-var-only config |
