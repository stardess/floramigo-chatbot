from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
	message: str = Field(..., min_length=1)
	plant_name: str | None = None
	include_sensor_context: bool = True


class AskResponse(BaseModel):
	response: str
	sensor_status: str
	sensor_summary: str
	plant_status: dict[str, Any]


class TelemetryRequest(BaseModel):
	temperature: float
	humidity: float
	moisture_pct: int | None = None
	moisture: int | None = None
	moisture_raw: int | None = None
	light_raw: int | None = None
	light: int | None = None
	timestamp: str | None = None


class TelemetryResponse(BaseModel):
	accepted: bool
	reading: dict[str, Any]
	plant_status: dict[str, Any]


class HealthResponse(BaseModel):
	status: str
	api: str
	sensor_monitor_running: bool


class MonitorResponse(BaseModel):
	ok: bool
	detail: str
	plant_status: dict[str, Any]
