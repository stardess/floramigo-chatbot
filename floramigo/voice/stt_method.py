# Speech-to-Text adapter module 


import speech_recognition as sr
from floramigo.voice.tts_method import speak

def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, I didn’t catch that.")
        speak("Sorry, I didn’t catch that.")
        return None
    except sr.RequestError as e:
        print(f"STT error: {e}")
        speak("I'm having trouble accessing speech services.")
        return None
