# Runbook

This runbook is intended for local development and quick manual checks.

## Setup

1. Activate your virtual environment.
2. Install dependencies from the three requirements files.
3. Export `OPENAI_API_KEY` if model-backed answers are needed.

Recommended install sequence:

```bash
pip install -r requirements-core.txt
pip install -r requirements-api.txt
pip install -r requirements-client.txt
```

## Start the service

```bash
uvicorn api.main:app --reload
```

The API should become available on `http://127.0.0.1:8000` unless overridden by environment variables.

## Feed a sample reading

```bash
curl -X POST http://127.0.0.1:8000/ingest/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 24.5,
    "humidity": 42,
    "moisture_pct": 36,
    "light_raw": 180
  }'
```

## Ask Floramigo a question

```bash
python client/floramigo-chat.py
```

Inside the client:

- type a normal plant-care question to hit `/ask`
- type `status` to fetch the latest diagnosis
- type `exit` to finish the session

## Monitor serial input

If a supported sensor board is connected and the serial settings are correct:

```bash
curl -X POST http://127.0.0.1:8000/monitor/start
```

To stop it:

```bash
curl -X POST http://127.0.0.1:8000/monitor/stop
```

## Troubleshooting

- If `/ask` returns a fallback summary, verify `OPENAI_API_KEY` is set.
- If sensor data stays unavailable, post a reading manually to confirm the ingestion path works.
- If serial monitoring does not start, check `FLORAMIGO_SERIAL_PORT`, board connectivity, and whether `pyserial` is installed.
- If the client cannot connect, verify the API URL in `FLORAMIGO_API_URL`.
