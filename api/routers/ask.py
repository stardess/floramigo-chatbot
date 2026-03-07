from fastapi import APIRouter

from api.models.command import AskRequest, AskResponse
from floramigo.core.orchestrator import orchestrator


router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask_floramigo(payload: AskRequest) -> AskResponse:
	result = orchestrator.chat(
		payload.message,
		plant_name=payload.plant_name,
		include_sensor_context=payload.include_sensor_context,
	)
	return AskResponse(**result)
