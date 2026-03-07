from fastapi import APIRouter

from api.models.command import HealthResponse
from floramigo.core.phd import plant_health_daemon


router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
	return HealthResponse(
		status="ok",
		api="floramigo",
		sensor_monitor_running=plant_health_daemon.running,
	)
