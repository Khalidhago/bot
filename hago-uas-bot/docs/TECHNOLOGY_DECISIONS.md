# HAGO UAS Intelligence & Support Bot — Technology Decisions

## Backend

| Decision | Choice | Rationale |
|---|---|---|
| Language | Python 3.11 | Mature AI/ML ecosystem, async support, rapid iteration |
| Web framework | FastAPI | Async-native, auto OpenAPI, type-safe with Pydantic, WebSocket support |
| ORM | SQLAlchemy 2 async | Type-safe, supports async, battle-tested, excellent migration tooling |
| Database | PostgreSQL 15 + pgvector | Full SQL, JSON, vector search in one DB; avoids separate vector DB |
| Cache / broker | Redis 7 | Session cache, rate limiting, Pub/Sub for streaming, task queue |
| Password hashing | bcrypt via passlib | Industry standard; argon2 considered but bcrypt sufficient for v1 |
| JWT library | python-jose | JOSE standard; HS256 for simplicity, RS256 planned for multi-service |
| Task queue | Celery + Redis broker | Mature, async task support, retries, monitoring via Flower |
| PDF parsing | PyMuPDF (fitz) | Fast, accurate layout-aware extraction; pdfplumber as fallback |
| Embeddings | OpenAI text-embedding-3-small | Best quality/cost trade-off; abstracted for easy swap |
| Vector search | pgvector + HNSW index | Colocated with main DB; avoids operational complexity of Pinecone/Weaviate |
| AI SDK | openai + anthropic + google-generativeai | Official SDKs; abstracted behind provider interface |
| Validation | Pydantic v2 | Fast, Rust-backed validation; integral to FastAPI |
| Migrations | Alembic | Standard for SQLAlchemy; autogenerate support |
| Testing | pytest + httpx + pytest-asyncio | Async-native testing; httpx for async HTTP |
| Logging | structlog | Structured JSON logging; correlation IDs |
| Config | pydantic-settings | Typed env-var config; `.env` support |

## Frontend

| Decision | Choice | Rationale |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR/SSG, streaming, RSC; best React meta-framework |
| Language | TypeScript 5 | Type safety across frontend; catches bugs early |
| Styling | Tailwind CSS 3 | Utility-first; consistent design system; no CSS-in-JS overhead |
| Components | shadcn/ui | Accessible, customizable, no dependency lock-in |
| Icons | Lucide React | Clean, consistent icon set used by shadcn/ui |
| Diagrams | Mermaid.js | Standard for architecture diagrams; renders in chat |
| Markdown | react-markdown + remark-gfm | Full GFM support; syntax highlighting via Prism |
| Syntax highlight | Prism.js (via react-syntax-highlighter) | Wide language support; matches engineering needs |
| WebSocket | native browser WebSocket | No extra library needed for standard WS |
| HTTP client | fetch (native) + typed wrappers | No additional library; leverages Next.js fetch extensions |
| Form handling | react-hook-form + zod | Type-safe forms with validation |
| State management | Zustand | Lightweight; no boilerplate; async-friendly |
| Auth | next-auth v5 (optional) / custom JWT | Custom JWT chosen for full control over token refresh |

## Infrastructure

| Decision | Choice | Rationale |
|---|---|---|
| Containerization | Docker + Docker Compose | Standard; works on any machine |
| Reverse proxy | Nginx (dev) / Traefik (prod) | Traefik: automatic SSL, service discovery |
| CI/CD | GitHub Actions | Native to repo; no external service required |
| Object storage | MinIO (local) / S3 (prod) | S3-compatible; easy swap |
| Secrets | `.env` files (local) / GitHub Secrets + K8s Secrets (prod) | Never commit secrets |
| Orchestration | Docker Compose (dev) / Kubernetes (prod) | K8s manifests provided; Helm chart planned |
| Monitoring | Prometheus + Grafana (stub) | Industry standard; FastAPI exposes `/metrics` |
| Log aggregation | stdout JSON → ELK / Loki (prod) | Cloud-agnostic |

## AI Provider Strategy

```
AIProvider (abstract)
├── OpenAIProvider        ← default; GPT-4o + embeddings
├── AnthropicProvider     ← Claude 3.5 Sonnet for long context
├── GoogleProvider        ← Gemini Pro for multimodal
└── LocalModelProvider    ← Ollama for air-gapped / private deployments
```

**Model routing by task:**

| Task | Default Model | Fallback |
|---|---|---|
| General UAV Q&A | gpt-4o-mini | claude-3-haiku |
| Deep technical | gpt-4o | claude-3-5-sonnet |
| Code generation | gpt-4o | claude-3-5-sonnet |
| Log analysis | gpt-4o | gpt-4-turbo |
| Document Q&A | gpt-4o-mini | claude-3-haiku |
| Vision analysis | gpt-4o | gemini-pro-vision |

## Decisions Deferred to v2

- Dedicated vector database (Weaviate / Pinecone) — pgvector sufficient for v1 scale
- Multi-tenancy / organization isolation — added after single-tenant validation
- Real-time collaboration — single-user sessions in v1
- Native mobile app — PWA covers initial mobile needs
- Fine-tuned domain model — RAG + prompting first; fine-tuning when data is available
