from fastapi import APIRouter

from api.models.command import TelemetryRequest, TelemetryResponse
from floramigo.core.phd import get_alerts, get_current_readings, plant_health_daemon


router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/telemetry", response_model=TelemetryResponse)
def ingest_telemetry(payload: TelemetryRequest) -> TelemetryResponse:
	reading = plant_health_daemon.ingest_reading(payload.model_dump(exclude_none=True))
	return TelemetryResponse(
		accepted=True,
		reading=reading,
		plant_status=plant_health_daemon.get_plant_status(),
	)


@router.get("/current")
def current_readings() -> dict:
	return get_current_readings()


@router.get("/alerts")
def recent_alerts() -> list[dict]:
	return get_alerts()
