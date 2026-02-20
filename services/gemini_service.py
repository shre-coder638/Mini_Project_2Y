import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-flash-latest")



def localize_text(original_text, target_language, target_region, tone):
    """
    Context-aware localization using Gemini
    """

    prompt = f"""
    You are an expert multilingual localization engine.

    Task:
    1. Understand the intent and tone of the content.
    2. Translate it into {target_language}.
    3. Adapt it culturally for {target_region}.
    4. Maintain a {tone} tone.
    5. Replace idioms, metaphors, and cultural references appropriately.
    6. Preserve meaning, not word-by-word translation.

    Content:
    "{original_text}"

    Provide only the localized output.
    """

    response = model.generate_content(prompt)

    return response.text
