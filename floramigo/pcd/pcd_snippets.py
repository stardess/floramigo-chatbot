"""Tiny care-tip snippets used by the prompt builder."""

DEFAULT_SNIPPETS = {
	"general": [
		"Check soil moisture before watering again; many plant issues come from overwatering.",
		"Look for patterns across temperature, humidity, light, and watering instead of reacting to one number alone.",
	],
	"watering": [
		"If soil moisture is low, recommend a deep watering and then letting excess water drain fully.",
		"If soil moisture is already high, warn against watering again too soon.",
	],
	"light": [
		"Low light can slow growth and leave soil wet longer, so pair lighting advice with watering advice.",
		"Very intense light can stress leaves even when watering looks correct.",
	],
	"humidity": [
		"Low humidity often shows up as crispy edges or slow recovery after watering.",
		"Improving airflow matters when humidity is consistently high.",
	],
}


def get_relevant_snippets(message: str, plant_name: str | None = None) -> list[str]:
	message_lower = (message or "").lower()
	snippets = list(DEFAULT_SNIPPETS["general"])

	if any(word in message_lower for word in ["water", "dry", "moisture", "soil"]):
		snippets.extend(DEFAULT_SNIPPETS["watering"])
	if any(word in message_lower for word in ["light", "bright", "dark", "sun"]):
		snippets.extend(DEFAULT_SNIPPETS["light"])
	if any(word in message_lower for word in ["humidity", "mist", "air", "dry air"]):
		snippets.extend(DEFAULT_SNIPPETS["humidity"])

	if plant_name:
		snippets.append(
			f"Tailor advice for {plant_name.strip()} and keep recommendations practical for a home grower."
		)

	return snippets[:5]