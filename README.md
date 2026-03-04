Mini Project (AIML) 2025-2026

Project overview
----------------
This is a small web application demonstrating text, visual, and voice results using local services.

Repository structure
--------------------
- `app.py` - Flask application entrypoint that serves the web UI.
- `services/` - helper modules for voice and Gemini-related operations (`gemini_service.py`, `voice_service.py`).
- `templates/` - Jinja2 HTML templates for pages and results.
- `static/` - static assets (CSS).

Setup
-----
1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

Run
---
Start the Flask app:

```powershell
python app.py
```

Then open http://127.0.0.1:5000/ in your browser.

Notes
-----
- Update `requirements.txt` if you add packages.
- See `templates/` for available pages: `home.html`, `text.html`, `visual.html`, `voice.html`.
- The services in `services/` are lightweight and meant as examples; review before production use.

Contact
-------
For questions, modify this README or open an issue.
