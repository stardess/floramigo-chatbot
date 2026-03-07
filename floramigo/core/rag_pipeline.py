from __future__ import annotations

from floramigo.pcd.pcd_snippets import get_relevant_snippets


def retrieve_care_tips(message: str, plant_name: str | None = None) -> list[str]:
	return get_relevant_snippets(message, plant_name)
