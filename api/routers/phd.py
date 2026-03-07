from fastapi import APIRouter

from api.models.command import MonitorResponse
from floramigo.core.phd import get_plant_status, plant_health_daemon


router = APIRouter(tags=["phd"])


@router.get("/diagnose")
def diagnose() -> dict:
	return get_plant_status()


@router.post("/monitor/start", response_model=MonitorResponse)
def start_monitor() -> MonitorResponse:
	plant_health_daemon.start()
	return MonitorResponse(ok=True, detail="Sensor monitor started.", plant_status=get_plant_status())


@router.post("/monitor/stop", response_model=MonitorResponse)
def stop_monitor() -> MonitorResponse:
	plant_health_daemon.stop()
	return MonitorResponse(ok=True, detail="Sensor monitor stopped.", plant_status=get_plant_status())
