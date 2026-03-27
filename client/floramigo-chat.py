import json
import os
from datetime import datetime

import requests
from dotenv import find_dotenv, load_dotenv


_ = load_dotenv(find_dotenv())

API_BASE_URL = os.getenv("FLORAMIGO_API_URL", "http://127.0.0.1:8000")
OUTPUT_FILE = "model-output.json"


def ask_api(message, plant_name=None, include_sensor_context=True):
    response = requests.post(
        f"{API_BASE_URL}/ask",
        json={
            "message": message,
            "plant_name": plant_name,
            "include_sensor_context": include_sensor_context,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def get_status():
    response = requests.get(f"{API_BASE_URL}/diagnose", timeout=20)
    response.raise_for_status()
    return response.json()

def save_conversation_summary(user_name, plant_name, plant_problem, timestamp):
    new_entry = {
        "user_name": user_name,
        "plant_name": plant_name,
        "plant_problem": plant_problem,
        "date": timestamp.strftime("%Y-%m-%d"),
        "time": timestamp.strftime("%H:%M:%S")
    }

    # Load existing data or start a new list
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]  # In case it was a single object
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new entry and save
    data.append(new_entry)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\nSummary appended to {OUTPUT_FILE}")


def summarize_problem(summary_collector):
    if not summary_collector:
        return "General plant-care conversation."
    excerpt = " ".join(summary_collector[-3:]).strip()
    return excerpt[:180] + ("..." if len(excerpt) > 180 else "")


def start_chat():
    print("Welcome to Floramigo. Let's get started with a few questions.")

    user_name = input("Your name: ").strip()
    plant_name = input("What type of plant are you asking about? ").strip()

    print(f"\nYou can now ask questions about your {plant_name}. Type 'exit' when you're done.")

    summary_collector = []
    timestamp = datetime.now()

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "quit", "bye", "thank you", "thanks", "i'm done"]:
            print("Floramigo: You're welcome. Take care.")
            break

        if user_input.lower() == "status":
            try:
                status = get_status()
                print(f"\nFloramigo: {status['summary']}")
            except requests.RequestException as exc:
                print(f"\nFloramigo: I couldn't fetch plant status from the API: {exc}")
            continue

        try:
            result = ask_api(user_input, plant_name=plant_name)
            print(f"\nFloramigo: {result['response']}")
        except requests.RequestException as exc:
            print(f"\nFloramigo: I couldn't reach the API at {API_BASE_URL}: {exc}")
            continue

        summary_collector.append(user_input)

    plant_problem_summary = summarize_problem(summary_collector)

    save_conversation_summary(user_name, plant_name, plant_problem_summary, timestamp)

if __name__ == "__main__":
    start_chat()
