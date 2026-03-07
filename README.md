## Floramigo Chatbot

Floramigo is a plant-care assistant built around three connected ideas:

- a Python service that stores live plant telemetry and turns it into a health summary
- a chat orchestration layer that can blend sensor facts with LLM guidance
- a local client that sends user questions to the API instead of embedding all logic in one script

This repository now has a working end-to-end path from incoming readings to conversational answers.

## Project layout

- [floramigo/core/config.py](floramigo/core/config.py) centralizes paths, API settings, and serial defaults
- [floramigo/core/phd.py](floramigo/core/phd.py) manages telemetry, alert generation, persistence, and plant status analysis
- [floramigo/core/orchestrator.py](floramigo/core/orchestrator.py) assembles system context, care tips, and optional LLM calls
- [floramigo/core/llm_client.py](floramigo/core/llm_client.py) wraps the OpenAI chat client
- [floramigo/pcd/pcd_snippets.py](floramigo/pcd/pcd_snippets.py) holds lightweight plant-care snippets used during prompt construction
- [api/main.py](api/main.py) exposes the FastAPI application
- [api/routers](api/routers) contains the public API routes for chat, health, monitoring, and telemetry ingestion
- [client/floramigo-chat.py](client/floramigo-chat.py) is the terminal client for asking Floramigo questions

## API surface

- `GET /healthz` and `GET /health` report API availability
- `POST /ask` sends a user message through the orchestration layer
- `POST /ingest/telemetry` stores a reading and refreshes plant status
- `GET /ingest/current` returns the latest normalized reading
- `GET /ingest/alerts` returns recent alert events
- `GET /diagnose` returns the latest computed plant summary
- `POST /monitor/start` and `POST /monitor/stop` control the serial monitor loop

## How the system works

1. Telemetry arrives either from the serial monitor or from `POST /ingest/telemetry`.
2. The health daemon normalizes the reading, saves current and historical data, and checks for threshold breaches.
3. When a user asks a question, the orchestrator adds live plant context and practical care snippets.
4. If `OPENAI_API_KEY` is configured, Floramigo returns a model-backed response; otherwise it falls back to a sensor-based summary.

## Quick start

1. Install dependencies:
	- `pip install -r requirements-core.txt`
	- `pip install -r requirements-api.txt`
	- `pip install -r requirements-client.txt`
2. Export `OPENAI_API_KEY` if you want LLM responses.
3. Start the API: `uvicorn api.main:app --reload`
4. Ingest sample telemetry or start the monitor.
5. Run the client: `python client/floramigo-chat.py`

## Documentation

- [docs/system-architecture.md](docs/system-architecture.md) explains the moving pieces and runtime flow
- [docs/api-contracts.md](docs/api-contracts.md) documents request and response shapes
- [docs/runbook.md](docs/runbook.md) covers local setup, common commands, and troubleshooting
- [dev-guide.md](dev-guide.md) gives a developer-oriented map of the repository
