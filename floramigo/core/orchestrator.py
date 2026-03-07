from __future__ import annotations

from floramigo.core.llm_client import FloramigoLLMClient, build_message
from floramigo.core.phd import format_sensor_context_for_llm, get_plant_status
from floramigo.core.rag_pipeline import retrieve_care_tips


class FloramigoOrchestrator:
	def __init__(self, llm_client: FloramigoLLMClient | None = None):
		self.llm_client = llm_client or FloramigoLLMClient()
		self.history: list[dict[str, str]] = []

	def _system_prompt(self, plant_name: str | None, user_message: str, include_sensor_context: bool) -> str:
		sections = [
			"You are Floramigo, a warm and practical plant-care assistant.",
			"Give clear, encouraging advice and prefer specific next steps over generic commentary.",
			"Use live plant telemetry naturally when it is available.",
		]

		if plant_name:
			sections.append(f"The user is asking about a {plant_name.strip()}.")

		if include_sensor_context:
			sections.append(format_sensor_context_for_llm())

		tips = retrieve_care_tips(user_message, plant_name)
		if tips:
			sections.append("Helpful care tips:\n- " + "\n- ".join(tips))

		return "\n\n".join(sections)

	def chat(self, user_message: str, plant_name: str | None = None, include_sensor_context: bool = True) -> dict:
		messages = [build_message("system", self._system_prompt(plant_name, user_message, include_sensor_context))]
		messages.extend(self.history[-12:])
		messages.append(build_message("user", user_message))

		sensor_status = get_plant_status()

		if not self.llm_client.available:
			response_text = sensor_status["summary"]
			if sensor_status["status"] != "unavailable":
				response_text += " I can give deeper conversational guidance once OPENAI_API_KEY is configured."
		else:
			response_text = self.llm_client.chat(messages)

		self.history.append(build_message("user", user_message))
		self.history.append(build_message("assistant", response_text))
		self.history = self.history[-20:]

		return {
			"response": response_text,
			"sensor_status": sensor_status["status"],
			"sensor_summary": sensor_status["summary"],
			"plant_status": sensor_status,
		}


orchestrator = FloramigoOrchestrator()
