from __future__ import annotations

import json
import time
from datetime import datetime
from threading import Lock, Thread
from typing import Callable

from floramigo.core.config import settings

try:
	import serial
except ImportError:
	serial = None


THRESHOLDS = {
	"temperature_low": 15.0,
	"temperature_high": 35.0,
	"humidity_low": 20.0,
	"humidity_high": 80.0,
	"moisture_low": 20.0,
	"moisture_critical": 10.0,
	"light_low": 50,
	"drop_threshold": 20.0,
}


class PlantHealthDaemon:
	def __init__(self, port: str | None = None, baud_rate: int | None = None):
		self.port = port or settings.serial_port
		self.baud_rate = baud_rate or settings.serial_baud_rate
		self.serial_conn = None
		self.running = False
		self.lock = Lock()
		self.thread: Thread | None = None
		self.current_data = {
			"timestamp": None,
			"temperature": None,
			"humidity": None,
			"moisture_pct": None,
			"moisture_raw": None,
			"light_raw": None,
			"status": "disconnected",
			"source": "unknown",
		}
		self.history = self._load_json(settings.sensor_history_file, default=[])
		self.max_history = 1440
		self.last_history_save: datetime | None = None
		self.alerts = self._load_json(settings.alerts_file, default=[])
		self.alert_callbacks: list[Callable[[dict], None]] = []

	def _load_json(self, path, default):
		try:
			with open(path, "r", encoding="utf-8") as handle:
				return json.load(handle)
		except (FileNotFoundError, json.JSONDecodeError):
			return default

	def _save_json(self, path, payload) -> None:
		with open(path, "w", encoding="utf-8") as handle:
			json.dump(payload, handle, indent=2)

	def connect(self) -> bool:
		if serial is None:
			self.current_data["status"] = "serial_unavailable"
			return False

		try:
			self.serial_conn = serial.Serial(self.port, self.baud_rate, timeout=2)
			time.sleep(2)
			self.serial_conn.reset_input_buffer()
			self.current_data["status"] = "connected"
			return True
		except Exception:
			self.current_data["status"] = "disconnected"
			self.serial_conn = None
			return False

	def disconnect(self) -> None:
		if self.serial_conn:
			self.serial_conn.close()
			self.serial_conn = None
		self.current_data["status"] = "disconnected"

	def parse_reading(self, line: str) -> dict | None:
		try:
			if "TEMP:" not in line:
				return None

			parts = line.split(",")
			return {
				"timestamp": datetime.now().isoformat(),
				"temperature": float(parts[0].split(":")[1]),
				"humidity": float(parts[1].split(":")[1]),
				"moisture_pct": int(parts[2].split(":")[1].rstrip("%")),
				"moisture_raw": int(parts[3].split(":")[1]),
				"light_raw": int(parts[4].split(":")[1]),
				"status": "ok",
				"source": "serial",
			}
		except (IndexError, ValueError):
			return None

	def ingest_reading(self, reading: dict, source: str = "api") -> dict:
		normalized = {
			"timestamp": reading.get("timestamp") or datetime.now().isoformat(),
			"temperature": float(reading["temperature"]),
			"humidity": float(reading["humidity"]),
			"moisture_pct": int(reading.get("moisture_pct", reading.get("moisture"))),
			"moisture_raw": reading.get("moisture_raw"),
			"light_raw": int(reading.get("light_raw", reading.get("light", 0))),
			"status": "ok",
			"source": source,
		}
		self._update_reading(normalized)
		return normalized

	def _update_reading(self, data: dict) -> None:
		with self.lock:
			self.current_data = data
			now = datetime.now()
			should_save_history = (
				self.last_history_save is None
				or (now - self.last_history_save).total_seconds() >= 60
			)
			if should_save_history:
				self.history.append(data)
				self.last_history_save = now
				if len(self.history) > self.max_history:
					self.history = self.history[-self.max_history :]
				self._save_json(settings.sensor_history_file, self.history)

		self._save_json(settings.sensor_data_file, self.current_data)
		self._check_alerts(data)

	def _check_alerts(self, data: dict) -> None:
		new_alerts: list[dict] = []

		if data["temperature"] < THRESHOLDS["temperature_low"]:
			new_alerts.append(self._build_alert("temperature_low", "warning", f"🥶 Temperature is low ({data['temperature']}°C)."))
		elif data["temperature"] > THRESHOLDS["temperature_high"]:
			new_alerts.append(self._build_alert("temperature_high", "warning", f"🥵 Temperature is high ({data['temperature']}°C)."))

		if data["moisture_pct"] < THRESHOLDS["moisture_critical"]:
			new_alerts.append(self._build_alert("moisture_critical", "critical", f"🚨 Soil is critically dry ({data['moisture_pct']}%). Water urgently."))
		elif data["moisture_pct"] < THRESHOLDS["moisture_low"]:
			new_alerts.append(self._build_alert("moisture_low", "warning", f"💧 Soil moisture is low ({data['moisture_pct']}%)."))

		if data["humidity"] < THRESHOLDS["humidity_low"]:
			new_alerts.append(self._build_alert("humidity_low", "info", f"🏜️ Air humidity is low ({data['humidity']}%)."))
		elif data["humidity"] > THRESHOLDS["humidity_high"]:
			new_alerts.append(self._build_alert("humidity_high", "info", f"💦 Air humidity is high ({data['humidity']}%)."))

		if len(self.history) >= 5:
			recent_avg = sum(entry["moisture_pct"] for entry in self.history[-5:]) / 5
			if recent_avg - data["moisture_pct"] > THRESHOLDS["drop_threshold"]:
				new_alerts.append(
					self._build_alert(
						"moisture_drop",
						"warning",
						f"📉 Sudden moisture drop detected: {recent_avg:.0f}% to {data['moisture_pct']}%.",
					)
				)

		if not new_alerts:
			return

		with self.lock:
			for alert in new_alerts:
				self.alerts.append(alert)
				if len(self.alerts) > 50:
					self.alerts = self.alerts[-50:]
				for callback in self.alert_callbacks:
					try:
						callback(alert)
					except Exception:
						continue

		self._save_json(settings.alerts_file, self.alerts)

	def _build_alert(self, alert_type: str, severity: str, message: str) -> dict:
		return {
			"type": alert_type,
			"severity": severity,
			"message": message,
			"timestamp": datetime.now().isoformat(),
		}

	def get_plant_status(self) -> dict:
		with self.lock:
			data = dict(self.current_data)

		if data["status"] != "ok" or data["temperature"] is None:
			file_data = self._load_json(settings.sensor_data_file, default={})
			if file_data.get("status") == "ok":
				data = file_data
			else:
				return {
					"status": "unavailable",
					"summary": "Sensor data not available. Please check the connection or ingest telemetry.",
					"message": "Sensor data not available. Please check the connection or ingest telemetry.",
					"data": None,
					"issues": [],
					"good_points": [],
					"recent_alerts": self.alerts[-5:],
				}

		issues: list[str] = []
		good_points: list[str] = []

		if data["temperature"] < THRESHOLDS["temperature_low"]:
			issues.append(f"Temperature is low at {data['temperature']}°C")
		elif data["temperature"] > THRESHOLDS["temperature_high"]:
			issues.append(f"Temperature is high at {data['temperature']}°C")
		else:
			good_points.append(f"Temperature is comfortable at {data['temperature']}°C")

		if data["moisture_pct"] < THRESHOLDS["moisture_critical"]:
			issues.append(f"Soil is critically dry at {data['moisture_pct']}%")
		elif data["moisture_pct"] < THRESHOLDS["moisture_low"]:
			issues.append(f"Soil moisture is low at {data['moisture_pct']}%")
		elif data["moisture_pct"] > 80:
			issues.append(f"Soil is very wet at {data['moisture_pct']}%")
		else:
			good_points.append(f"Soil moisture is healthy at {data['moisture_pct']}%")

		if data["humidity"] < THRESHOLDS["humidity_low"]:
			issues.append(f"Air humidity is low at {data['humidity']}%")
		elif data["humidity"] > THRESHOLDS["humidity_high"]:
			issues.append(f"Air humidity is high at {data['humidity']}%")
		else:
			good_points.append(f"Air humidity is comfortable at {data['humidity']}%")

		if data["light_raw"] < THRESHOLDS["light_low"]:
			issues.append("Light is low and the plant may need a brighter spot")
		else:
			good_points.append("Light levels look usable")

		if not issues:
			overall = "excellent"
			summary = "Your plant is doing great. Current conditions look healthy."
		elif any("critically" in issue for issue in issues):
			overall = "needs_attention"
			summary = "Your plant needs attention: " + "; ".join(issues)
		elif len(issues) == 1:
			overall = "good"
			summary = "Your plant is mostly doing well, but " + issues[0].lower() + "."
		else:
			overall = "fair"
			summary = "Your plant could use some care: " + "; ".join(issues)

		return {
			"status": overall,
			"summary": summary,
			"issues": issues,
			"good_points": good_points,
			"data": {
				"temperature": data["temperature"],
				"humidity": data["humidity"],
				"moisture": data["moisture_pct"],
				"light": data["light_raw"],
				"timestamp": data["timestamp"],
				"source": data.get("source", "unknown"),
			},
			"recent_alerts": self.alerts[-5:],
		}

	def get_current_readings(self) -> dict:
		with self.lock:
			return dict(self.current_data)

	def get_alerts(self) -> list[dict]:
		with self.lock:
			return list(self.alerts)

	def sensor_context(self) -> str:
		status = self.get_plant_status()
		if status["status"] == "unavailable":
			return (
				"[SENSOR STATUS: Unavailable]\n"
				"If the user asks about live conditions, explain that no recent telemetry is available."
			)

		data = status["data"]
		lines = [
			f"[CURRENT PLANT SENSOR DATA - {data['timestamp']}]",
			f"Temperature: {data['temperature']}°C",
			f"Humidity: {data['humidity']}%",
			f"Soil Moisture: {data['moisture']}%",
			f"Light Level: {data['light']} (raw)",
			f"Plant Status: {status['status'].upper()} - {status['summary']}",
		]
		if status["issues"]:
			lines.append("Issues: " + "; ".join(status["issues"]))
		if status["good_points"]:
			lines.append("Positive Conditions: " + "; ".join(status["good_points"]))
		if status["recent_alerts"]:
			lines.append(
				"Recent Alerts: "
				+ "; ".join(alert["message"] for alert in status["recent_alerts"][-3:])
			)
		return "\n".join(lines)

	def on_alert(self, callback: Callable[[dict], None]) -> None:
		self.alert_callbacks.append(callback)

	def _monitor_loop(self) -> None:
		while self.running:
			if not self.serial_conn and not self.connect():
				time.sleep(5)
				continue

			try:
				if self.serial_conn and self.serial_conn.in_waiting > 0:
					line = self.serial_conn.readline().decode("utf-8", errors="ignore").strip()
					data = self.parse_reading(line)
					if data:
						self._update_reading(data)
			except Exception:
				self.disconnect()
				time.sleep(2)

			time.sleep(0.1)

	def start(self) -> bool:
		if self.running:
			return True
		self.running = True
		self.thread = Thread(target=self._monitor_loop, daemon=True)
		self.thread.start()
		return True

	def stop(self) -> None:
		self.running = False
		self.disconnect()


plant_health_daemon = PlantHealthDaemon()


def get_plant_status() -> dict:
	return plant_health_daemon.get_plant_status()


def get_current_readings() -> dict:
	return plant_health_daemon.get_current_readings()


def get_alerts() -> list[dict]:
	return plant_health_daemon.get_alerts()


def format_sensor_context_for_llm() -> str:
	return plant_health_daemon.sensor_context()
