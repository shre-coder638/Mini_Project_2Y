# Mini Project (AIML) 2025-2026

-----------------------------------
Project overview
-----------------------------------

The **Visual Localization Module** is a component of the **Automated Content Localization** Platform that adapts visual content for different languages and cultures.It allows users to upload images and generate culturally appropriate captions based on selected language, region, and tone. The system analyzes the image context and extracts embedded text using **OCR**. It then applies **AI-based localization** to produce meaningful and culturally relevant output.

-----------------------------------
Repository structure
-----------------------------------

- `app.py` - Flask application entrypoint that serves the web UI.
- `services/` - helper modules for voice and Gemini-related operations (`gemini_service.py`, `voice_service.py`).
- `templates/` - Jinja2 HTML templates for pages and results.
- `static/` - static assets (CSS).

-----------------------------------
Setup
-----------------------------------

1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

-----------------------------------
Run :-
-----------------------------------
Start the Flask app:

```powershell
python app.py
```

Then open http://127.0.0.1:5000/ in your browser.

-----------------------------------
Notes
-----------------------------------
- Update `requirements.txt` if you add packages.
- See `templates/` for available pages: `home.html`, `text.html`, `visual.html`, `voice.html`.
- The services in `services/` are lightweight and meant as examples; review before production use.

-----------------------------------
FEATURE REQUIREMENTS
-----------------------------------

1. INPUT LAYER (Frontend already exists)
The backend must accept:
- Image file upload
- Optional caption text
- Target language
- Target region / culture
- Tone (Formal / Casual / Professional / Friendly)

-----------------------------------
OUTPUT REQUIREMENTS
-----------------------------------

Return:
- Localized Caption
- Localized UI Text
- Cultural Notes (if any adjustments were made)
- Optional Warning if culturally sensitive

-----------------------------------
TECH STACK
-----------------------------------

Backend: Python (Flask)
AI Integration: OpenAI API or HuggingFace
OCR: pytesseract or easyocr
Image Processing: PIL
Deployment-ready structure

-----------------------------------
FINAL EXPECTED BEHAVIOR
-----------------------------------

User uploads image → 
System generates description → 
Extracts text → 
Combines context → 
AI culturally adapts content → 
Returns localized result in structured JSON

The module must be scalable and API-ready.
