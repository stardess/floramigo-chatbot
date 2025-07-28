import os
import json
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

from stt_method import get_voice_input
from tts_method import speak

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

if __name__ == "__main__":
    start_chat()
