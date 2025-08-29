# Text-to-Speech adapter module

from gtts import gTTS
import os
import uuid
import pygame

def speak(text):
    tts = gTTS(text)
    filename = f"temp_audio_{uuid.uuid4().hex}.mp3"
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.quit()
    os.remove(filename)
