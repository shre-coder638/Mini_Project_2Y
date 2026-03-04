from flask import Flask, render_template, request, redirect, url_for, session
from services.voice_service import speech_to_text, text_to_speech
from langdetect import detect, LangDetectException
import os
from services.gemini_service import localize_text


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

    filename = image.filename if image else "No image uploaded"

    return f"""
    <h2>Visual Input Received:</h2>
    <p><strong>Image:</strong> {filename}</p>
    <p><strong>Caption:</strong> {caption}</p>
    <p><strong>Language:</strong> {target_language}</p>
    <p><strong>Region:</strong> {target_region}</p>
    <p><strong>Tone:</strong> {tone}</p>
    """


if __name__ == "__main__":
    app.run(debug=True)
