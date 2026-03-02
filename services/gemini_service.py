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
     You are a localization engine.
     
     Translate the content into {target_language}
     for {target_region}.
     
     IMPORTANT:
     - Preserve the emotional tone of the original speaker.
     - Do not exaggerate or rephrase unnecessarily.
     - Maintain similar sentence length and intensity.
     - Keep speech natural for spoken delivery.
     - Maintain {tone} tone without changing speaker personality.
     
     Content:
     "{original_text}"
     
     Return only the localized text.
    """

    response = model.generate_content(prompt)

    return response.text
