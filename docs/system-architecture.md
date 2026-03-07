# System architecture

Floramigo is organized as a small service-oriented Python application with a thin client on top.

## Core layers

### 1. Telemetry layer

The telemetry layer lives in [floramigo/core/phd.py](../floramigo/core/phd.py).

Its responsibilities are:

- receive plant readings from a serial connection or HTTP ingestion
- normalize incoming payloads into one internal structure
- persist the latest reading, alert history, and coarse-grained historical data
- convert raw values into a plant status summary that the rest of the app can consume

### 2. Orchestration layer

The orchestration layer lives in [floramigo/core/orchestrator.py](../floramigo/core/orchestrator.py).

It is responsible for:

- deciding what context should be added to a conversation
- requesting live plant status when available
- adding short care hints from the prompt data collection in [floramigo/pcd/pcd_snippets.py](../floramigo/pcd/pcd_snippets.py)
- calling the model client when an API key is configured
- falling back to a deterministic plant summary when no model is available

### 3. API layer

The API layer begins at [api/main.py](../api/main.py) and exposes the application over HTTP.

Key route groups:

- chat requests in [api/routers/ask.py](../api/routers/ask.py)
- health and readiness checks in [api/routers/health.py](../api/routers/health.py)
- telemetry ingestion and lookup in [api/routers/ingest.py](../api/routers/ingest.py)
- plant diagnosis and monitor controls in [api/routers/phd.py](../api/routers/phd.py)

### 4. Client layer

The terminal client in [client/floramigo-chat.py](../client/floramigo-chat.py) is intentionally small.

It prompts the user for a plant name, sends questions to the API, and saves a brief local conversation summary.

## Data flow

1. A reading arrives through serial input or `POST /ingest/telemetry`.
2. The health daemon writes the current snapshot to `data/current_readings.json` and appends minute-level history when appropriate.
3. The daemon evaluates thresholds and records recent alerts.
4. A user question reaches `POST /ask`.
5. The orchestrator builds a system prompt with live plant context and care snippets.
6. The response is produced either by the OpenAI client or by the fallback sensor summary.

## Design choices

- **Single source of truth for plant state**: the health daemon owns normalization and status calculation.
- **Thin client**: the CLI stays simple and delegates reasoning to the API.
- **Graceful degradation**: the app remains useful without model access.
- **Incremental prompt retrieval**: a small snippet library keeps prompt construction understandable while the project evolves.
