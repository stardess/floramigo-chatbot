# API contracts

This document summarizes the current HTTP interface exposed by Floramigo.

## Health

### `GET /healthz`
### `GET /health`

Returns basic service information.

Example response:

```json
{
  "status": "ok",
  "api": "floramigo",
  "sensor_monitor_running": false
}
```

## Chat

### `POST /ask`

Request body:

```json
{
  "message": "How is my pothos doing?",
  "plant_name": "pothos",
  "include_sensor_context": true
}
```

Response body:

```json
{
  "response": "Your plant looks fairly comfortable right now...",
  "sensor_status": "good",
  "sensor_summary": "Your plant is mostly doing well...",
  "plant_status": {
    "status": "good",
    "summary": "Your plant is mostly doing well...",
    "issues": [],
    "good_points": [],
    "data": {},
    "recent_alerts": []
  }
}
```

## Telemetry ingestion

### `POST /ingest/telemetry`

Accepted fields:

- `temperature` required
- `humidity` required
- `moisture_pct` or `moisture` required in practice for meaningful watering advice
- `light_raw` or `light` optional
- `moisture_raw` optional
- `timestamp` optional

Example request:

```json
{
  "temperature": 24.8,
  "humidity": 45.2,
  "moisture_pct": 39,
  "light_raw": 210,
  "timestamp": "2026-03-06T10:30:00"
}
```

Example response:

```json
{
  "accepted": true,
  "reading": {
    "timestamp": "2026-03-06T10:30:00",
    "temperature": 24.8,
    "humidity": 45.2,
    "moisture_pct": 39,
    "moisture_raw": null,
    "light_raw": 210,
    "status": "ok",
    "source": "api"
  },
  "plant_status": {
    "status": "excellent",
    "summary": "Your plant is doing great. Current conditions look healthy.",
    "issues": [],
    "good_points": [],
    "data": {},
    "recent_alerts": []
  }
}
```

## Telemetry lookup

### `GET /ingest/current`

Returns the latest normalized reading.

### `GET /ingest/alerts`

Returns recent alert entries recorded by the daemon.

## Diagnosis and monitor control

### `GET /diagnose`

Returns the current computed plant status.

### `POST /monitor/start`

Starts the background serial monitor.

### `POST /monitor/stop`

Stops the background serial monitor.
