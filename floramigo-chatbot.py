import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# Load API key from .env
_ = load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Output file name
OUTPUT_FILE = "model-output.json"

# Initial system message for the assistant
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

        messages.append({"role": "user", "content": user_input})
        assistant_response = get_completion_from_messages(messages)
        messages.append({"role": "assistant", "content": assistant_response})

        print(f"\nFloramigo: {assistant_response}")
        summary_collector.append(user_input)

    # Summarize plant problem
    problem_prompt = [
        {"role": "system", "content": "Summarize this user's plant issue in one short sentence."},
        {"role": "user", "content": " ".join(summary_collector)}
    ]
    plant_problem_summary = get_completion_from_messages(problem_prompt)

    save_conversation_summary(user_name, plant_name, plant_problem_summary, timestamp)

if __name__ == "__main__":
    start_chat()
