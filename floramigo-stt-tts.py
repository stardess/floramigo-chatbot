import os
import json
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

from stt_method import get_voice_input
from tts_method import speak
from sensor_monitor import MultiSensorMonitor
from csv_logger import CSVLogger
import asyncio
import threading
import random

# Load OpenAI key
_ = load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OUTPUT_FILE = "model-output.json"

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0.7):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

def save_conversation_summary(user_name, plant_name, plant_problem, timestamp):
    new_entry = {
        "user_name": user_name,
        "plant_name": plant_name,
        "plant_problem": plant_problem,
        "date": timestamp.strftime("%Y-%m-%d"),
        "time": timestamp.strftime("%H:%M:%S")
    }

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(new_entry)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\nSummary appended to {OUTPUT_FILE}")

async def sensor_reader_simulated() -> dict:
    """
    Simulated sensor readings. Replace with real hardware reads.
    Returns a dict with keys matching the CSV column names expected.
    """
    # Example sensors: soil moisture (%), temperature (C), humidity (%), light (lux)
    return {
        "soil_moisture": 40 + random.uniform(-5, 5),
        "temperature_c": 24 + random.uniform(-1.5, 1.5),
        "humidity_pct": 55 + random.uniform(-4, 4),
        "light_lux": 300 + random.uniform(-50, 50),
    }


async def run_sensor_loop(thresholds: dict, llm_alert: callable, csv_path: str = "floramigo_datalog.csv", stop_event: threading.Event = None):
    field_order = list(thresholds.keys())
    logger = CSVLogger(csv_path, field_order)

    def on_event(sensor_name: str, event_type: str, value: float):
        # Build a concise message per event
        if event_type.startswith("enter_"):
            direction = "low" if event_type.endswith("low") else "high"
            msg = f"Alert: {sensor_name.replace('_', ' ')} is {direction} at {value:.2f}."
        else:
            direction = "low" if event_type.endswith("low") else "high"
            msg = f"Recovered: {sensor_name.replace('_', ' ')} exited {direction} at {value:.2f}."
        llm_alert(msg)

    monitor = MultiSensorMonitor(
        thresholds,
        smoothing_alpha=0.25,
        min_duration_s=0.5,
        cooldown_s=3.0,
        on_event=on_event,
    )

    while (stop_event is None) or (not stop_event.is_set()):
        readings = await sensor_reader_simulated()
        monitor.update(readings)
        logger.log(readings)
        await asyncio.sleep(1.0)


def start_sensor_background(thresholds: dict, llm_alert: callable, csv_path: str = "floramigo_datalog.csv"):
    stop_event = threading.Event()

    def _runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_sensor_loop(thresholds, llm_alert, csv_path, stop_event))
        finally:
            loop.close()

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    return stop_event, thread


def start_chat():
    print("Welcome to Floramigo. Let’s begin.")
    speak("Welcome to Floramigo. Let’s begin.")

    user_name = input("Your name: ").strip()
    plant_name = input("What type of plant are you asking about? ").strip()

    # Choose interaction mode
    print("\nWould you prefer to speak or type your questions?")
    speak("Would you prefer to speak or type your questions?")
    mode = input("Enter 'voice' for vocal interaction or 'text' to type: ").strip().lower()

    while mode not in ["voice", "text"]:
        print("Please enter either 'voice' or 'text'.")
        mode = input("Enter 'voice' or 'text': ").strip().lower()

    use_voice = (mode == "voice")

    if use_voice:
        speak(f"Great. You can now ask questions about your {plant_name}. Speak when you're ready.")
    else:
        print(f"\nYou can now type questions about your {plant_name}.")

    messages = [
        {
            "role": "system",
            "content": (
                "You are Floramigo, a friendly and plant-savvy AI assistant. "
                "Help users with plant care advice in a warm, encouraging tone. "
                "Keep answers clear and actionable."
            )
        }
    ]

    summary_collector = []
    timestamp = datetime.now()

    # Define plant-specific thresholds (examples; adjust per plant)
    # For each sensor: provide low/high and hysteresis for stability
    plant_thresholds = {
        "soil_moisture": {"low": 35.0, "high": 80.0, "hysteresis": 2.0},
        "temperature_c": {"low": 18.0, "high": 30.0, "hysteresis": 0.5},
        "humidity_pct": {"low": 40.0, "high": 75.0, "hysteresis": 2.0},
        "light_lux": {"low": 100.0, "high": 2000.0, "hysteresis": 50.0},
    }

    # Define LLM+TTS alert function
    def llm_alert(message: str):
        alert_prompt = [
            {"role": "system", "content": "Rephrase alerts briefly and kindly for a plant care assistant."},
            {"role": "user", "content": message},
        ]
        try:
            alert_text = get_completion_from_messages(alert_prompt)
        except Exception:
            alert_text = message
        print(f"\nFloramigo Alert: {alert_text}")
        speak(alert_text)

    # Start background sensor loop in a separate thread to avoid blocking input/voice
    stop_event, sensor_thread = start_sensor_background(plant_thresholds, llm_alert)

    while True:
        if use_voice:
            user_input = get_voice_input()
        else:
            user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "bye", "thank you", "thanks", "i'm done"]:
            print("Floramigo: You're welcome. Take care.")
            speak("You're welcome. Take care.")
            break

        messages.append({"role": "user", "content": user_input})
        assistant_response = get_completion_from_messages(messages)
        messages.append({"role": "assistant", "content": assistant_response})

        print(f"\nFloramigo: {assistant_response}")
        speak(assistant_response)
        summary_collector.append(user_input)

    # Summarize issue
    problem_prompt = [
        {"role": "system", "content": "Summarize this user's plant issue in one short sentence."},
        {"role": "user", "content": " ".join(summary_collector)}
    ]
    plant_problem_summary = get_completion_from_messages(problem_prompt)

    save_conversation_summary(user_name, plant_name, plant_problem_summary, timestamp)
    try:
        stop_event.set()
        sensor_thread.join(timeout=2.0)
    except Exception:
        pass

if __name__ == "__main__":
    start_chat()
