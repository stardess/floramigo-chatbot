from __future__ import annotations

from typing import Any

from floramigo.core.config import settings

try:
	from openai import OpenAI
except ImportError:
	OpenAI = None


class FloramigoLLMClient:
	def __init__(self, api_key: str | None = None, model: str | None = None):
		self.api_key = api_key or settings.openai_api_key
		self.model = model or settings.openai_model
		self._client = OpenAI(api_key=self.api_key) if OpenAI and self.api_key else None

	@property
	def available(self) -> bool:
		return self._client is not None

	def chat(
		self,
		messages: list[dict[str, str]],
		*,
		temperature: float = 0.7,
		max_tokens: int = 500,
		model: str | None = None,
	) -> str:
		if not self._client:
			raise RuntimeError(
				"OpenAI client is unavailable. Set OPENAI_API_KEY and install `openai`."
			)

		response = self._client.chat.completions.create(
			model=model or self.model,
			messages=messages,
			temperature=temperature,
			max_tokens=max_tokens,
		)
		message = response.choices[0].message.content
		return message.strip() if isinstance(message, str) else ""


def build_message(role: str, content: Any) -> dict[str, str]:
	return {"role": role, "content": str(content)}
