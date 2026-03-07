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
## Developer guide

This file is a contributor-facing map of the current Floramigo codebase.

### Main folders

- `api/` holds the FastAPI application, routers, and request/response models
- `client/` contains local chat scripts and side experiments
- `floramigo/` is the main package for telemetry logic, orchestration, prompt helpers, and voice utilities
- `data/` contains generated sensor snapshots and alert output during local runs
- `docs/` contains human-readable documentation for architecture and operation

### Key implementation files

- `floramigo/core/config.py` defines runtime settings and shared paths
- `floramigo/core/phd.py` owns reading ingestion, threshold checks, storage, and plant summaries
- `floramigo/core/orchestrator.py` combines user prompts with plant context and care hints
- `floramigo/core/llm_client.py` isolates the model provider integration
- `floramigo/core/rag_pipeline.py` is currently a compact prompt helper, not a full retrieval stack
- `api/main.py` constructs the API app and registers routes
- `api/models/command.py` defines the current Pydantic schemas
- `client/floramigo-chat.py` is the preferred CLI entrypoint for end-to-end testing

### Expected workflows

- use the API routes for chat and telemetry instead of wiring more logic directly into the client
- add new sensor analysis rules in `floramigo/core/phd.py`
- extend prompt behavior in `floramigo/core/orchestrator.py` and `floramigo/pcd/pcd_snippets.py`
- keep generated files and extracted reference material out of source control

### Environment variables

- `OPENAI_API_KEY` enables model-backed answers
- `FLORAMIGO_OPENAI_MODEL` changes the default model name
- `FLORAMIGO_API_HOST` and `FLORAMIGO_API_PORT` affect API binding
- `FLORAMIGO_API_URL` tells the CLI client where to send requests
- `FLORAMIGO_SERIAL_PORT` and `FLORAMIGO_BAUD_RATE` configure serial monitoring