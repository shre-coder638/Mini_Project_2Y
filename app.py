from flask import Flask, render_template, request, redirect, url_for, session
from services.voice_service import speech_to_text, text_to_speech
from langdetect import detect, LangDetectException
import os
from services.gemini_service import localize_text
from services.visual_service import get_visual_localization_service
from services.utils import validate_file, get_config
from werkzeug.utils import secure_filename
import time
import uuid
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# If a single API key is provided in .env (e.g., GOOGLE_API_KEY), prefer it
_env_key = os.getenv('GOOGLE_API_KEY') or os.getenv('API_KEY')
if _env_key:
    os.environ.setdefault('OPENAI_API_KEY', _env_key)
    os.environ.setdefault('GOOGLE_API_KEY', _env_key)
    os.environ.setdefault('GEMINI_API_KEY', _env_key)
    os.environ.setdefault('API_KEY', _env_key)


app = Flask(__name__)
app.secret_key = "your_secret_key_here_change_in_production"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/process", methods=["POST"])
def process():
    content_type = request.form.get("content_type")

    if content_type == "text":
        return redirect(url_for("text_localization"))

    elif content_type == "audio":
        return redirect(url_for("voice_localization"))

    elif content_type == "visual":
        return redirect(url_for("visual_localization"))

    return "Module coming soon!"


@app.route("/text")
def text_localization():
    return render_template("text.html")


@app.route("/generate", methods=["POST"])
def generate():
    original_text = request.form.get("original_text")
    target_language = request.form.get("target_language")
    target_region = request.form.get("target_region")
    tone = request.form.get("tone")

    # Auto-detect source language for text input
    try:
        source_lang = None
        if original_text and original_text.strip():
            try:
                source_lang = detect(original_text)
            except LangDetectException:
                source_lang = None

        localized_output = localize_text(
            original_text, target_language, target_region, tone, source_language=source_lang
        )
    except Exception as e:
        localized_output = f"Error: {str(e)}"

    return render_template(
        "result_text.html",
        original_text=original_text,
        localized_output=localized_output,
        target_language=target_language,
        target_region=target_region,
        tone=tone,
    )


@app.route("/voice")
def voice_localization():
    return render_template("voice.html")


@app.route("/process_voice", methods=["POST"])
def process_voice():
    # Debug logging: show incoming files and form keys
    print("/process_voice called")
    print("Form keys:", list(request.form.keys()))
    print("Files keys:", list(request.files.keys()))

    audio_file = request.files.get("audio_file")
    target_language = request.form.get("target_language")
    target_region = request.form.get("target_region")
    tone = request.form.get("tone")

    if not audio_file:
        print("No audio_file in request.files")
        return "Error: No audio file provided", 400

    try:
        # Log some metadata about the uploaded file
        try:
            print(f"Uploaded file: filename={audio_file.filename}, content_type={getattr(audio_file, 'content_type', None)}")
        except Exception as mderr:
            print("Could not read file metadata:", mderr)

        # Save uploaded file with correct extension
        filename = audio_file.filename
        if not filename:
            filename = "recorded.webm"

        audio_path = f"temp_{filename}"
        audio_file.save(audio_path)

        # Print saved file size
        try:
            size = os.path.getsize(audio_path)
            print(f"Saved audio file: {audio_path} ({size} bytes)")
        except Exception:
            print(f"Saved audio file: {audio_path} (size unknown)")

        # Convert to clean WAV
        from services.voice_service import convert_to_wav
        audio_path = convert_to_wav(audio_path)
        print(f"Converted to WAV: {audio_path}")

        # Speech to Text (returns text and detected language code)
        transcribed_text, detected_source_lang = speech_to_text(audio_path)
        print(f"Transcribed: {transcribed_text} (detected: {detected_source_lang})")

        # Localization (pass detected source language where available)
        localized_text = localize_text(
            transcribed_text, target_language, target_region, tone, source_language=detected_source_lang
        )
        print(f"Localized: {localized_text}")

        # Text to Speech (XTTS v2)
        output_audio_path = text_to_speech(
            localized_text,
            audio_path,          # original uploaded voice
            target_language
        )
        # Ensure a web-friendly URL to the static audio file (handle Windows backslashes)
        if output_audio_path:
            audio_filename = os.path.basename(output_audio_path)
            audio_url = url_for('static', filename=audio_filename)
        else:
            audio_url = None
        print(f"Audio output: {audio_url}")

        # Store results in session
        session["voice_results"] = {
            "transcribed_text": transcribed_text,
            "localized_output": localized_text,
            "audio_url": audio_url,
            "target_language": target_language,
            "target_region": target_region,
            "tone": tone,
        }

        return "Success", 200
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"Error in process_voice: {str(e)}")
        print(tb)
        # Return traceback in response to aid debugging during development
        return f"Error processing audio: {str(e)}\n\nTraceback:\n{tb}", 500


@app.route("/voice_results")
def voice_results():
    """Display the voice localization results from session"""
    results = session.pop("voice_results", None)
    
    if not results:
        return redirect(url_for("voice_localization"))
    
    return render_template(
        "result_voice.html",
        transcribed_text=results.get("transcribed_text"),
        localized_output=results.get("localized_output"),
        audio_url=results.get("audio_url"),
        target_language=results.get("target_language"),
        target_region=results.get("target_region"),
        tone=results.get("tone"),
    )


@app.route("/visual")
def visual_localization():
    return render_template("visual.html")


@app.route("/process_visual", methods=["POST"])
def process_visual():
    image = request.files.get("image_file")
    caption = request.form.get("caption_text")
    target_language = request.form.get("target_language")
    target_region = request.form.get("target_region")
    tone = request.form.get("tone")
    ocr_language = request.form.get("ocr_language") or 'en'

    if not image:
        return redirect(url_for("visual_localization"))

    # Validate uploaded file (size + extension)
    is_valid, err = validate_file(image)
    if not is_valid:
        return render_template(
            'result_visual.html',
            target_language=target_language,
            target_region=target_region,
            tone=tone,
            extracted_text='',
            localized_output='',
            error_message=err,
            filename=getattr(image, 'filename', 'uploaded'),
            image_url=None,
            cultural_notes=[],
            warnings=[]
        )

    # Ensure required parameters
    if not target_language or not target_region or not tone:
        return render_template(
            'result_visual.html',
            target_language=target_language,
            target_region=target_region,
            tone=tone,
            extracted_text='',
            localized_output='',
            error_message='Missing required parameters: target language, region, or tone',
            filename=getattr(image, 'filename', 'uploaded'),
            image_url=None,
            cultural_notes=[],
            warnings=[]
        )

    try:
        filename = getattr(image, 'filename', 'uploaded')

        # Save uploaded image to static/uploads for preview on results page
        uploads_dir = os.path.join(app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        safe_name = secure_filename(filename)
        unique = f"{int(time.time())}-{uuid.uuid4().hex[:8]}-" + safe_name
        save_path = os.path.join(uploads_dir, unique)

        # Save a copy for preview, then pass the saved path to the service
        image.save(save_path)
        image_url = url_for('static', filename=f'uploads/{unique}')

        svc = get_visual_localization_service()

        result = svc.process_image(
            image_file=save_path,
            target_language=target_language,
            target_region=target_region,
            tone=tone,
            user_caption=caption,
            ocr_language=ocr_language
        )
        
        print("VISUAL RESULT:", result)

        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error during visual processing')
            return render_template(
                'result_visual.html',
                target_language=target_language,
                target_region=target_region,
                tone=tone,
                extracted_text=result.get('ocr_text') or "No text detected",
                localized_output=result.get('localized_caption') or result.get('localized_text', ''),
                error_message=error_msg,
                filename=filename,
                image_url=image_url,
                cultural_notes=result.get('cultural_notes', []),
                warnings=result.get('warnings', [])
            )

        return render_template(
            'result_visual.html',
            target_language=target_language,
            target_region=target_region,
            tone=tone,
            extracted_text=result.get('ocr_text') or "No text detected",
            localized_output=result.get('localized_caption') or result.get('localized_text', ''),
            filename=filename,
            image_url=image_url,
            cultural_notes=result.get('cultural_notes', []),
            warnings=result.get('warnings', [])
        )

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return f"Error processing visual: {str(e)}\n\nTraceback:\n{tb}", 500



if __name__ == "__main__":
    app.run(debug=True)
