from gtts import gTTS
import speech_recognition as sr
import os

LANGUAGE_MAP = {
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "English": "en"
}

def text_to_speech(text, target_language, output_path="static/output_voice.mp3"):
    try:
        lang_code = LANGUAGE_MAP.get(target_language, "en")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        tts = gTTS(
            text=text,
            lang=lang_code,
            slow=False
        )

        tts.save(output_path)
        return output_path

    except Exception as e:
        print("gTTS Error:", e)
        return None


def speech_to_text(audio_path):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)

        return recognizer.recognize_google(audio_data)

    except sr.UnknownValueError:
        return ""
    except Exception as e:
        print("Speech Recognition Error:", e)
        return ""