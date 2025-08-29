```text

floramigo-code/                               # Root project directory
├─ 📁 floramigo/                         # Core Python package (domain logic)
│  ├─ 📁 core/                           # Rules, orchestration, LLM, RAG
│  ├─ 📁 voice/                          # STT/TTS adapters (your files live here)
│  ├─ 📁 devices/                        # Device/command contracts & simulators
│  ├─ 📁 pcd/                            # Plant Care Database (thresholds/snippets)
│  ├─ 📁 utils/                          # Config, security, helpers
│  └─ __init__.py
├─ 📁 api/                               # FastAPI service (public endpoints)
│  ├─ 📁 routers/                        # Route definitions
│  ├─ 📁 models/                         # DB & Pydantic models/schemas
│  ├─ 📁 middleware/                     # Auth, logging, CORS
│  ├─ database.py                        # DB config (SQLite/Postgres)
│  └─ main.py                            # API entry point
├─ 📁 client/                            # Local client (your chat app)
│  ├─ floramigo_chat.py                  # (renamed) your floramigo-chatbot-tts-stt.py
│  ├─ stt_method.py                      # your STT file
│  ├─ tts_method.py                      # your TTS file
│  ├─ edge_uploader.py                   # CSV → POST /ingest/telemetry
│  └─ config.py
├─ 📁 docker/                            # Docker configuration
│  ├─ Dockerfile.api                     # API container
│  ├─ Dockerfile.client                  # (optional) client container
│  ├─ Dockerfile.worker                  # (optional) background jobs
│  ├─ build.sh                           # Build script
│  └─ run.sh                             # Dev runner
├─ 📁 tests/                             # Unit/integration tests
│  ├─ test_rules.py
│  ├─ test_orchestrator.py
│  └─ test_api.py
├─ 📁 docs/                              # Documentation
│  ├─ system-architecture.md
│  ├─ api-contracts.md
│  └─ runbook.md
├─ 📁 models/                            # (optional) local STT/TTS or tiny LLMs
├─ 📁 data/                              # Sample CSVs, fixtures
├─ 📁 logs/                              # App logs (gitignored)
├─ docker-compose.yml                    # Multi-service orchestration
├─ requirements-api.txt                  # API deps (fastapi, asyncpg/sqlalchemy, pydantic)
├─ requirements-core.txt                 # Core deps (openai, numpy, etc.)
├─ requirements-client.txt               # Client deps (sounddevice, requests, etc.)
└─ dev-guide.md                          # How to run, env vars, workflows

floramigo/core/

orchestrator.py   # Build prompt, pick PCD tips, call LLM, parse command
phd.py            # PHD v1: latest telemetry → statuses + safe actions
llm_client.py     # OpenAI/Phi client wrapper
rag_pipeline.py   # v0 snippets (later: embeddings/vector search)
embeddings.py     # (later) embedding utilities
config.py         # Core service settings

api/routers/

health.py   # GET /healthz
ingest.py   # POST /ingest/telemetry
ask.py      # POST /ask
phd.py      # GET /diagnose (optional: PHD-only output for debugging)

floramigo/pcd/

thresholds.yaml   # Per-plant ranges
pcd_snippets.json # Short care tips keyed by plant + tag