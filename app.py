from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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

    # Temporary dummy output (replace later with Gemini)
    localized_output = f"[Localized {tone} version in {target_language} for {target_region}]"

    return render_template(
        "result_text.html",
        original_text=original_text,
        localized_output=localized_output,
        target_language=target_language,
        target_region=target_region,
        tone=tone
    )


@app.route("/voice")
def voice_localization():
    return render_template("voice.html")


@app.route("/process_voice", methods=["POST"])
def process_voice():
    audio_file = request.files.get("audio_file")
    target_language = request.form.get("target_language")
    target_region = request.form.get("target_region")
    tone = request.form.get("tone")

    if audio_file:
        filename = audio_file.filename
    else:
        filename = "No file uploaded"

    return f"""
    <h2>Voice Input Received:</h2>
    <p><strong>File:</strong> {filename}</p>
    <p><strong>Language:</strong> {target_language}</p>
    <p><strong>Region:</strong> {target_region}</p>
    <p><strong>Tone:</strong> {tone}</p>
    """

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
