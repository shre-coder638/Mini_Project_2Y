import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
import logging

try:
    import grpc
except Exception:
    grpc = None

load_dotenv()

genai.configure(api_key=(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv('API_KEY') or os.getenv('OPENAI_API_KEY')))

model = genai.GenerativeModel("gemini-flash-latest")


def _generate_with_retries(prompt, max_attempts=3, initial_backoff=1.0):
    attempt = 0
    backoff = initial_backoff
    last_exc = None
    while attempt < max_attempts:
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            last_exc = e
            attempt += 1
            # If gRPC is available, try to detect deadline exceeded specifically
            if grpc and hasattr(e, 'code'):
                try:
                    code = e.code()
                    if code == grpc.StatusCode.DEADLINE_EXCEEDED:
                        logging.warning(f"Gemini call deadline exceeded on attempt {attempt}")
                except Exception:
                    pass
            logging.warning(f"Gemini generate attempt {attempt} failed: {e}. Retrying in {backoff}s...")
            time.sleep(backoff)
            backoff *= 2

    # All attempts failed
    raise last_exc


def localize_text(original_text, target_language, target_region, tone=None, source_language=None):
    tone_analysis = detect_tone(original_text)

    tone_instruction = f"Desired tone: {tone}\n" if tone else ""

    source_lang_line = f"Source language: {source_language}\n" if source_language else ""

    prompt = f"""
    You are a professional localization engine.

    Target language: {target_language}
    Target region: {target_region}

    {source_lang_line}
    {tone_instruction}
    The original tone analysis:
    {tone_analysis}

    IMPORTANT:
    - Preserve the same tone and emotional intensity unless a different desired tone is specified.
    - Do not exaggerate.
    - Maintain sentence structure for spoken delivery.
    - Keep emotional level consistent.

    Original text:
    "{original_text}"

    Return only the localized version.
    """

    response = _generate_with_retries(prompt)
    return response.text.strip()


def detect_tone(text):
    prompt = f"""
    Analyze the tone of the following text.

    Identify:
    - Primary tone (formal, casual, marketing, emotional, urgent, friendly, neutral, etc.)
    - Emotional intensity (low, medium, high)

    Text:
    "{text}"

    Return only:
    Tone: <tone>
    Intensity: <level>
    """

    response = _generate_with_retries(prompt)
    return response.text.strip()