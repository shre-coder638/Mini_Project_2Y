import os
import speech_recognition as sr
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

eleven_client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

def speech_to_text(audio_path):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except Exception:
        return "Could not transcribe audio."


def text_to_speech(text, output_path="static/output_voice.mp3"):

    audio = eleven_client.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Default Rachel voice
        model_id="eleven_multilingual_v2",
        text=text
    )

    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return output_path
