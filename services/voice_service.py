from TTS.api import TTS
import speech_recognition as sr
import uuid
import os
from langdetect import detect, LangDetectException

# Load XTTS model once
tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

LANGUAGE_MAP = {
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "English": "en"
}

# Added broader language support
LANGUAGE_MAP.update({
    "Chinese (Simplified)": "zh",
    "Portuguese": "pt",
    "Russian": "ru",
    "Arabic": "ar",
    "Korean": "ko",
    "Italian": "it",
    "Dutch": "nl",
    "Turkish": "tr",
    "Indonesian": "id"
})

# -------- Speech To Text --------
def speech_to_text(audio_path):
    """Transcribe audio and attempt to auto-detect the source language.

    Returns a tuple: (transcribed_text, detected_language_code)
    """
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
    except Exception as e:
        print("STT Error:", e)
        return "Could not transcribe audio.", None

    # Try language detection on the transcribed text
    try:
        lang_code = detect(text)
    except LangDetectException:
        lang_code = None
    except Exception:
        lang_code = None

    return text, lang_code

# -------- Text To Speech (XTTS v2) --------
def text_to_speech(text, speaker_sample_path, target_language):

    lang_code = LANGUAGE_MAP.get(target_language, "en")

    output_filename = f"output_{uuid.uuid4().hex}.wav"
    output_path = os.path.join("static", output_filename)

    tts_model.tts_to_file(
        text=text,
        speaker_wav=speaker_sample_path,
        language=lang_code,
        file_path=output_path
    )

    return output_path

from pydub import AudioSegment
import os

def convert_to_wav(input_path):
    """Convert any audio format to WAV format with consistent settings"""
    output_path = "temp_converted.wav"
    
    try:
        # Auto-detect format from file extension or content
        audio = AudioSegment.from_file(input_path)
        
        # Convert to mono at 22050 Hz (ideal for speech recognition)
        audio = audio.set_channels(1).set_frame_rate(22050)
        
        # Export as WAV
        audio.export(output_path, format="wav")
        
        print(f"Successfully converted {input_path} to {output_path}")
        
        # Clean up original file if it's not the same as output
        if input_path != output_path and os.path.exists(input_path):
            try:
                os.remove(input_path)
            except:
                pass
        
        return output_path
    except Exception as e:
        print(f"Error converting audio: {str(e)}")
        raise
