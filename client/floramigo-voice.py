#!/usr/bin/env python3
"""
Floramigo Voice Chatbot with Wake Word Detection

Features:
- Wake word detection ("Hey Floramigo", "Hey Flora")
- Speech-to-text using OpenAI Whisper
- LLM-powered responses
- Text-to-speech using OpenAI TTS
- Integration with plant sensor data via API
- Multi-turn conversation support
"""

import os
import sys
import time
import wave
import json
import pyaudio
import requests
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import difflib

try:
    from openai import OpenAI
    import numpy as np
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install openai numpy pyaudio")
    sys.exit(1)


class WakeWordDetector:
    """Detects wake words using fuzzy string matching."""
    
    def __init__(self, wake_words: List[str] = None, threshold: float = 0.75):
        """
        Initialize wake word detector.
        
        Args:
            wake_words: List of wake phrases to detect
            threshold: Similarity threshold (0.0-1.0) for matching
        """
        self.wake_words = wake_words or [
            "hey floramigo",
            "hey flora",
            "floramigo",
            "hey plant",
            "ok floramigo"
        ]
        self.threshold = threshold
        self.last_detection_time = 0
        self.cooldown_seconds = 2  # Prevent rapid re-triggering
        
        print(f"🔊 Wake word detector initialized")
        print(f"   Wake phrases: {', '.join(self.wake_words)}")
        print(f"   Similarity threshold: {threshold * 100}%")
    
    def detect(self, text: str) -> bool:
        """
        Check if text contains a wake word.
        
        Args:
            text: Transcribed text to check
            
        Returns:
            True if wake word detected, False otherwise
        """
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_detection_time < self.cooldown_seconds:
            return False
        
        text_lower = text.lower().strip()
        
        # Check for exact matches first
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                self.last_detection_time = current_time
                print(f"✓ Wake word detected (exact): '{wake_word}'")
                return True
        
        # Check for fuzzy matches
        for wake_word in self.wake_words:
            similarity = difflib.SequenceMatcher(None, wake_word, text_lower).ratio()
            if similarity >= self.threshold:
                self.last_detection_time = current_time
                print(f"✓ Wake word detected (fuzzy {similarity*100:.0f}%): '{text}'")
                return True
        
        return False


class AudioEngine:
    """Handles audio recording and playback."""
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        """Initialize audio engine."""
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        
        print(f"🎤 Audio engine initialized ({sample_rate}Hz)")
    
    def record_audio(self, duration: float = 5.0, silence_threshold: int = 500, 
                    silence_duration: float = 2.0) -> str:
        """
        Record audio to a temporary file.
        
        Args:
            duration: Maximum recording duration in seconds
            silence_threshold: Amplitude threshold to detect silence
            silence_duration: Seconds of silence before stopping
            
        Returns:
            Path to recorded WAV file
        """
        print(f"🎙️  Recording... (speak now, {duration}s max)")
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        frames = []
        silent_chunks = 0
        silence_chunks_limit = int((self.sample_rate / self.chunk_size) * silence_duration)
        max_chunks = int((self.sample_rate / self.chunk_size) * duration)
        
        self.is_recording = True
        
        try:
            for _ in range(max_chunks):
                if not self.is_recording:
                    break
                
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Check for silence
                audio_data = np.frombuffer(data, dtype=np.int16)
                if np.abs(audio_data).mean() < silence_threshold:
                    silent_chunks += 1
                    if silent_chunks > silence_chunks_limit:
                        print("   (silence detected, stopping)")
                        break
                else:
                    silent_chunks = 0
        
        finally:
            stream.stop_stream()
            stream.close()
            self.is_recording = False
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()
        
        with wave.open(temp_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
        
        print(f"✓ Recording complete ({len(frames)} chunks)")
        return temp_path
    
    def play_audio(self, audio_file: str):
        """Play audio file through speakers."""
        print(f"🔊 Playing audio...")
        
        try:
            with wave.open(audio_file, 'rb') as wf:
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                data = wf.readframes(self.chunk_size)
                while data:
                    stream.write(data)
                    data = wf.readframes(self.chunk_size)
                
                stream.stop_stream()
                stream.close()
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def cleanup(self):
        """Clean up audio resources."""
        self.audio.terminate()


class VoiceChatbot:
    """Main voice chatbot orchestrator."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Initialize voice chatbot.
        
        Args:
            api_url: Base URL for Floramigo API
        """
        # Initialize components
        self.api_url = api_url
        self.wake_detector = WakeWordDetector()
        self.audio_engine = AudioEngine()
        
        # OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  Warning: OPENAI_API_KEY not set. Voice features limited.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
            print("✓ OpenAI client initialized")
        
        # State
        self.conversation_history = []
        self.plant_name = os.getenv("PLANT_NAME", "your plant")
        self.is_running = False
        
        print(f"✓ Floramigo Voice Chatbot initialized")
        print(f"   API URL: {api_url}")
        print(f"   Plant: {self.plant_name}")
    
    def fetch_sensor_data(self) -> Optional[Dict]:
        """Fetch current sensor data from API."""
        try:
            response = requests.get(f"{self.api_url}/ingest/current", timeout=2)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Note: Could not fetch sensor data: {e}")
        return None
    
    def speech_to_text(self, audio_file: str) -> Optional[str]:
        """
        Convert speech to text using OpenAI Whisper.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.client:
            print("Error: OpenAI client not configured")
            return None
        
        try:
            print("🔄 Transcribing speech...")
            with open(audio_file, 'rb') as audio:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )
            
            text = transcript.strip() if isinstance(transcript, str) else transcript.text.strip()
            print(f"📝 You said: \"{text}\"")
            return text
        
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None
    
    def get_ai_response(self, message: str) -> Optional[str]:
        """
        Get AI response via Floramigo API.
        
        Args:
            message: User message
            
        Returns:
            AI response text
        """
        try:
            # Try API first
            response = requests.post(
                f"{self.api_url}/ask",
                json={"message": message, "plant_name": self.plant_name},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "I'm not sure how to respond to that.")
        
        except Exception as e:
            print(f"API error: {e}")
        
        # Fallback to direct OpenAI
        if self.client:
            try:
                sensor_data = self.fetch_sensor_data()
                context = f"Current sensor readings: {sensor_data}" if sensor_data else ""
                
                messages = [
                    {"role": "system", "content": f"You are Floramigo, a friendly plant care assistant. {context}"},
                    *self.conversation_history[-6:],  # Include recent history
                    {"role": "user", "content": message}
                ]
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=150
                )
                
                return response.choices[0].message.content.strip()
            
            except Exception as e:
                print(f"LLM error: {e}")
        
        return "I'm having trouble connecting right now. Please check if the API is running."
    
    def text_to_speech(self, text: str) -> Optional[str]:
        """
        Convert text to speech using OpenAI TTS.
        
        Args:
            text: Text to convert
            
        Returns:
            Path to audio file or None
        """
        if not self.client:
            return None
        
        try:
            print("🔄 Generating speech...")
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",  # Warm, friendly voice
                input=text
            )
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_path = temp_file.name
            
            response.stream_to_file(temp_path)
            
            print(f"✓ Speech generated")
            return temp_path
        
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
    
    def listen_for_wake_word(self):
        """Continuously listen for wake word."""
        print("\n🌿 Floramigo is ready!")
        print(f"   Say '{self.wake_detector.wake_words[0]}' to start")
        print("   Press Ctrl+C to exit\n")
        
        while self.is_running:
            try:
                # Record short audio clip
                audio_file = self.audio_engine.record_audio(duration=3.0)
                
                # Transcribe
                text = self.speech_to_text(audio_file)
                
                # Clean up
                try:
                    os.unlink(audio_file)
                except:
                    pass
                
                if text and self.wake_detector.detect(text):
                    # Wake word detected!
                    print("\n🌿 Floramigo: I'm listening! What would you like to know?\n")
                    self.handle_conversation()
                    print(f"\n   Say '{self.wake_detector.wake_words[0]}' when you need me again\n")
            
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(0.5)
    
    def handle_conversation(self):
        """Handle a single conversation turn."""
        # Record user question
        audio_file = self.audio_engine.record_audio(duration=10.0, silence_duration=2.5)
        
        # Transcribe
        user_message = self.speech_to_text(audio_file)
        os.unlink(audio_file)
        
        if not user_message or len(user_message.strip()) < 3:
            print("   (no speech detected)")
            return
        
        # Check for exit commands
        if any(word in user_message.lower() for word in ["goodbye", "bye", "exit", "stop", "nevermind"]):
            print("🌿 Floramigo: Goodbye! I'll be here if you need me.")
            farewell_audio = self.text_to_speech("Goodbye! I'll be here if you need me.")
            if farewell_audio:
                self.audio_engine.play_audio(farewell_audio)
                os.unlink(farewell_audio)
            return
        
        # Get AI response
        ai_response = self.get_ai_response(user_message)
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        # Display response
        print(f"\n🌿 Floramigo: {ai_response}\n")
        
        # Speak response
        audio_file = self.text_to_speech(ai_response)
        if audio_file:
            self.audio_engine.play_audio(audio_file)
            os.unlink(audio_file)
    
    def interactive_mode(self):
        """Run in interactive wake word listening mode."""
        self.is_running = True
        
        try:
            self.listen_for_wake_word()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        finally:
            self.cleanup()
    
    def single_question_mode(self):
        """Handle a single question without wake word."""
        print("\n🌿 Floramigo Voice Chat")
        print("   Speak your question after the beep...\n")
        
        try:
            self.handle_conversation()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.is_running = False
        self.audio_engine.cleanup()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Floramigo Voice Chatbot")
    parser.add_argument("--api-url", default="http://localhost:8000",
                       help="Floramigo API URL")
    parser.add_argument("--single", action="store_true",
                       help="Single question mode (no wake word)")
    parser.add_argument("--plant-name", default="your plant",
                       help="Name of your plant")
    parser.add_argument("--test-audio", action="store_true",
                       help="Test audio recording and playback")
    
    args = parser.parse_args()
    
    # Set environment variable
    if args.plant_name:
        os.environ["PLANT_NAME"] = args.plant_name
    
    # Test mode
    if args.test_audio:
        print("🎤 Testing audio system...")
        engine = AudioEngine()
        print("   Recording 3 seconds...")
        audio_file = engine.record_audio(duration=3.0)
        print(f"   Playing back...")
        engine.play_audio(audio_file)
        os.unlink(audio_file)
        engine.cleanup()
        print("✓ Audio test complete")
        return
    
    # Create chatbot
    bot = VoiceChatbot(api_url=args.api_url)
    
    # Run appropriate mode
    if args.single:
        bot.single_question_mode()
    else:
        bot.interactive_mode()


if __name__ == "__main__":
    main()
