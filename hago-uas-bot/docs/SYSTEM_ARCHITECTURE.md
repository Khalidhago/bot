# HAGO UAS Intelligence & Support Bot — System Architecture

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                      │
│  Dashboard │ Chat Workspace │ Flight-Log Analyzer │ KB Explorer │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS / WSS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API GATEWAY (Nginx)                       │
│            Rate Limiting │ TLS Termination │ Load Balancing     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FASTAPI APPLICATION SERVER                      │
│                                                                 │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Auth Layer│  │  REST API    │  │  WebSocket Handler   │   │
│  │  JWT/RBAC  │  │  /api/v1/    │  │  /ws/chat            │   │
│  └────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              AI ORCHESTRATION LAYER                     │   │
│  │  AIRouter → [OpenAI | Anthropic | Google | Local]      │   │
│  │  ConversationEngine │ TokenManager │ StreamingHandler   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            UAV DOMAIN INTELLIGENCE LAYER               │   │
│  │  PX4Module │ ArduPilotModule │ MAVLinkModule           │   │
│  │  ROS2Module │ SensorModule │ AirframeModule            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            RAG KNOWLEDGE RETRIEVAL SYSTEM              │   │
│  │  DocumentIngestion → Chunking → Embeddings → Search   │   │
│  │  Reranker │ SourceTracker │ ConfidenceScoring          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │          FLIGHT-LOG ANALYSIS ENGINE                    │   │
│  │  ULogParser │ DataFlashParser │ AnomalyDetector        │   │
│  │  DiagnosticReport │ ConfidenceLevels                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────────┐
          ▼              ▼                  ▼
   ┌─────────────┐ ┌──────────┐    ┌──────────────┐
   │ PostgreSQL  │ │  Redis   │    │  Object      │
   │ + pgvector  │ │ Cache/PQ │    │  Storage     │
   │ (primary DB)│ │          │    │ (docs/logs)  │
   └─────────────┘ └──────────┘    └──────────────┘
```

---

## 2. Backend Package Structure

```
apps/api/
├── app/
│   ├── main.py                    # FastAPI app factory
│   ├── core/
│   │   ├── config.py              # Settings via pydantic-settings
│   │   ├── security.py            # JWT, password hashing, RBAC
│   │   ├── logging.py             # Structured JSON logging
│   │   ├── exceptions.py          # Custom exception classes
│   │   └── middleware.py          # Request ID, CORS, audit
│   ├── database.py                # Async SQLAlchemy engine & session
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── document.py
│   │   ├── flight_log.py
│   │   ├── knowledge_source.py
│   │   ├── ai_request.py
│   │   └── audit_log.py
│   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── document.py
│   │   ├── flight_log.py
│   │   └── uav.py
│   ├── api/
│   │   └── v1/
│   │       ├── router.py
│   │       ├── auth.py
│   │       ├── chat.py
│   │       ├── conversations.py
│   │       ├── documents.py
│   │       ├── flight_logs.py
│   │       ├── uav.py
│   │       ├── knowledge.py
│   │       └── health.py
│   ├── services/                  # Business logic layer
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── document_service.py
│   │   ├── flight_log_service.py
│   │   └── knowledge_service.py
│   ├── repositories/              # Database access layer
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── conversation_repository.py
│   │   └── document_repository.py
│   ├── agents/                    # AI agent orchestration
│   │   ├── base_agent.py
│   │   ├── ai_router.py
│   │   ├── providers/
│   │   │   ├── base_provider.py
│   │   │   ├── openai_provider.py
│   │   │   ├── anthropic_provider.py
│   │   │   └── google_provider.py
│   │   └── conversation_engine.py
│   ├── rag/                       # RAG system
│   │   ├── document_ingestion.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   └── reranker.py
│   ├── uav/                       # UAV domain intelligence
│   │   ├── domain_classifier.py
│   │   ├── px4/
│   │   ├── ardupilot/
│   │   ├── mavlink/
│   │   ├── ros2/
│   │   ├── airframes/
│   │   └── computer_vision/
│   ├── log_analysis/              # Flight log analysis
│   │   ├── parsers/
│   │   ├── anomaly_detector.py
│   │   └── report_generator.py
│   └── security/                  # Security utilities
│       ├── rate_limiter.py
│       ├── input_validator.py
│       └── prompt_guard.py
├── tests/
├── alembic/
├── requirements.txt
└── Dockerfile
```

---

## 3. AI Orchestration Architecture

```
User Message
     │
     ▼
┌────────────────────────────────────────┐
│           Domain Classifier            │
│  Detect: general / technical / code /  │
│  log-analysis / document / vision      │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│              AI Router                 │
│                                        │
│  General Question    → GPT-4o-mini     │
│  Technical UAV       → GPT-4o          │
│  Code Generation     → GPT-4o / Claude │
│  Log Analysis        → GPT-4o          │
│  Document Q&A        → Claude 3 Haiku  │
│  Vision Analysis     → GPT-4o-vision   │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│         Context Builder                │
│  Conversation History                  │
│  RAG Retrieved Chunks                  │
│  UAV Domain Prompt Templates           │
│  System Prompt (mode-specific)         │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│         AI Provider                    │
│  Streaming response via SSE/WebSocket  │
└────────────────────────────────────────┘
```

---

## 4. RAG Architecture

```
┌──────────────┐
│  PDF / Doc   │
│  Upload      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│  Document Ingestion Pipeline │
│  ├── Type detection          │
│  ├── Text extraction         │
│  │   ├── PDF → PyMuPDF       │
│  │   ├── DOCX → python-docx  │
│  │   └── TXT → direct        │
│  ├── Metadata extraction     │
│  └── Quality filter          │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Chunking Strategy           │
│  ├── Semantic chunking       │
│  ├── Chunk size: 512 tokens  │
│  └── Overlap: 64 tokens      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Embedding Generation        │
│  ├── OpenAI text-embedding-3 │
│  └── Stored in pgvector      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Vector Store (pgvector)     │
│  ├── HNSW index              │
│  └── Metadata filter support │
└──────────────┬───────────────┘
               │
       Query ──┘
               │
               ▼
┌──────────────────────────────┐
│  Semantic Search             │
│  ├── Top-K candidates        │
│  └── MMR diversity filter    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Reranker (cross-encoder)    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Context Window Assembly     │
│  ├── Source attribution      │
│  └── Confidence scoring      │
└──────────────────────────────┘
```

---

## 5. Database Schema (Logical)

```
users
  id, email, hashed_password, full_name, role,
  is_active, api_key_hash, created_at, updated_at

organizations
  id, name, slug, plan, created_at

conversations
  id, user_id, title, mode, created_at, updated_at

messages
  id, conversation_id, role, content, sources (jsonb),
  tokens_used, model_used, created_at

documents
  id, user_id, filename, file_path, mime_type,
  status, chunk_count, ingested_at, metadata (jsonb)

document_chunks
  id, document_id, content, embedding (vector 1536),
  chunk_index, metadata (jsonb)

flight_logs
  id, user_id, filename, file_path, log_type,
  status, analysis_result (jsonb), created_at

knowledge_sources
  id, title, source_url, document_type, verified,
  created_at

ai_requests
  id, user_id, model, prompt_tokens, completion_tokens,
  latency_ms, created_at

audit_logs
  id, user_id, action, resource, detail (jsonb),
  ip_address, created_at
```

---

## 6. Frontend Architecture

```
apps/web/src/
├── app/                           # Next.js App Router
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── page.tsx               # Main dashboard
│   │   ├── chat/
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── documents/page.tsx
│   │   ├── flight-logs/page.tsx
│   │   └── knowledge/page.tsx
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── StreamingMessage.tsx
│   │   ├── ModeSelector.tsx
│   │   ├── FileUploadDropzone.tsx
│   │   └── SourceReferences.tsx
│   ├── dashboard/
│   │   ├── StatsCard.tsx
│   │   ├── ConversationList.tsx
│   │   └── SystemHealth.tsx
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── MermaidDiagram.tsx
│   └── ui/                        # shadcn/ui components
├── lib/
│   ├── api.ts                     # API client
│   ├── websocket.ts               # WebSocket client
│   ├── auth.ts                    # Auth helpers
│   └── utils.ts
└── types/
    └── index.ts
```

---

## 7. Deployment Architecture

```
Internet
    │
    ▼
Cloudflare (WAF + CDN)
    │
    ▼
Load Balancer (Nginx / Traefik)
    │
    ├──► Next.js (multiple replicas)
    │
    └──► FastAPI (multiple replicas)
              │
              ├──► PostgreSQL (primary + replica)
              │
              ├──► Redis Cluster
              │
              └──► Object Storage (S3-compatible)
```

---

## 8. Security Architecture

- **Authentication**: JWT (15 min access, 7 day refresh) + API keys
- **Authorization**: RBAC with roles: `admin`, `engineer`, `operator`, `viewer`
- **Transport**: TLS 1.3 everywhere
- **Secrets**: Environment variables only, never committed
- **Prompt injection**: Input sanitization, output filtering, guardrails
- **File uploads**: MIME validation, size limits, malware scan stub
- **Rate limiting**: Per-user and per-IP via Redis sliding window
- **Audit logging**: All auth events, AI requests, file operations
