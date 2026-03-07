from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"


@dataclass(frozen=True)
class Settings:
	openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
	openai_model: str = os.getenv("FLORAMIGO_OPENAI_MODEL", "gpt-4o-mini")
	api_host: str = os.getenv("FLORAMIGO_API_HOST", "127.0.0.1")
	api_port: int = int(os.getenv("FLORAMIGO_API_PORT", "8000"))
	serial_port: str = os.getenv("FLORAMIGO_SERIAL_PORT", "/dev/ttyUSB0")
	serial_baud_rate: int = int(os.getenv("FLORAMIGO_BAUD_RATE", "115200"))
	sensor_data_file: Path = DATA_DIR / "current_readings.json"
	sensor_history_file: Path = DATA_DIR / "readings_history.json"
	alerts_file: Path = DATA_DIR / "alerts.json"

	@property
	def api_base_url(self) -> str:
		return f"http://{self.api_host}:{self.api_port}"


settings = Settings()

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
