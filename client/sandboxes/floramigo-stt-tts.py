import os
import json
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

from floramigo.voice.stt_method import get_voice_input
from floramigo.voice.tts_method import speak


# --- voice_io.py-ish helpers (inline) ---
import time
import speech_recognition as sr
# from floramigo.voice.stt_method import get_voice_input
# from floramigo.voice.tts_method import speak

# Load OpenAI key
_ = load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OUTPUT_FILE = "model-output.json"


MIC_INDEX = 1  # set to your USB mic index from earlier
LISTEN_TIMEOUT = 10
PHRASE_LIMIT = 8

def listen_once(prompt=None):
    """Speak a prompt, then capture a single utterance with SR."""
    if prompt:
        speak(prompt)
        time.sleep(0.2)
    r = sr.Recognizer()
    with sr.Microphone(device_index=MIC_INDEX) as source:
        # keep energy threshold stable to reduce timeouts
        r.dynamic_energy_threshold = False
        r.energy_threshold = 150
        r.pause_threshold = 0.6
        audio = r.listen(source, timeout=LISTEN_TIMEOUT, phrase_time_limit=PHRASE_LIMIT)
    try:
        return r.recognize_google(audio)
    except Exception:
        return None

def ask_until_understood(prompt, retries=3, confirm=False):
    """Ask a question by voice, retry politely, and (optionally) confirm the result."""
    for attempt in range(retries):
        text = listen_once(prompt if attempt == 0 else "Sorry, could you repeat that?")
        if text:
            if confirm:
                speak(f"Did you say: {text}? Please say yes or no.")
                ans = listen_once()
                if ans and ans.lower().startswith("y"):
                    return text
                else:
                    continue
            return text
    speak("I couldn't understand. Let's try again later.")
    return None

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

    # user_name = input("Your name: ").strip()
    user_name = ask_until_understood("Hello, What's your name?", retries=3, confirm=True)
    if not user_name:
        # fallback so the app can continue headless
        user_name = "Friend"
    speak(f"Hi {user_name}. How can I help you?")

    # plant_name = input("What type of plant are you asking about? ").strip()
    plant_name = ask_until_understood("What type of plant are you asking about?", retries=3, confirm=True)
    if not plant_name:
        # fallback so the app can continue headless
        plant_name = "plant"
    speak(f"Great. You can now ask questions about your {plant_name}. Speak when you're ready.")

    # Choose interaction mode
    # print("\nWould you prefer to speak or type your questions?")
    # speak("Would you prefer to speak or type your questions?")
    # mode = input("Enter 'voice' for vocal interaction or 'text' to type: ").strip().lower()
    
    # while mode not in ["voice", "text"]:
    #     print("Please enter either 'voice' or 'text'.")
    #     mode = input("Enter 'voice' or 'text': ").strip().lower()


    mode = "voice"  # for testing, default to voice
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
        # else:
        #     user_input = input("\nYou: ").strip()

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
