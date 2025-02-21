from flask import Flask, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment
from moviepy import AudioFileClip
import os
from main import llm_model
from transformers import pipeline
from gmail import service, create_message, send_email
import torch

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

# Directory to save audio files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
model = llm_model()

# Global variable to store the path of the processed audio file
processed_audio_path = None


@app.route("/process-audio/", methods=["POST"])
def process_audio():
    global processed_audio_path

    if "file" not in request.files:
        print("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["file"]
    if audio_file.filename == "":
        print("No file selected")
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(file_path)

    try:
        # Generate a dynamic file name to avoid overwriting
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        wav_file_path = os.path.join(UPLOAD_FOLDER, f"{base_name}.wav")

        # Convert to WAV format using MoviePy
        audio_clip = AudioFileClip(file_path)
        audio_clip.write_audiofile(wav_file_path, codec="pcm_s16le")
        audio_clip.close()

        # Store the path of the processed audio file
        processed_audio_path = wav_file_path

        return jsonify({"wav_file_path": wav_file_path}), 200

    except Exception as e:
        print(f"Failed to convert audio: {str(e)}")
        return jsonify({"error": f"Failed to convert audio: {str(e)}"}), 500


@app.route("/transcribe-audio/", methods=["GET"])
def transcribe_audio():
    global processed_audio_path

    if not processed_audio_path:
        return jsonify({"error": "No processed audio file found"}), 400

    # Load Whisper model
    transcriber = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-medium",
        device=0 if torch.cuda.is_available() else -1,
    )

    # Transcribe recorded audio
    transcription = transcriber(
        processed_audio_path, return_timestamps=True, generate_kwargs={"language": "en"}
    )

    # Print the transcribed text
    print(transcription["text"])

    # Save the text
    with open("transcription.txt", "w") as f:
        f.write(transcription["text"])

    return jsonify({"transcription": transcription["text"]})


@app.route("/summarise-audio/", methods=["GET"])
def summarise_audio():
    with open("transcription.txt", "r") as f:
        transcription_text = f.read()
    summary = model.summarize(transcription_text)
    print(summary)
    # Return the summary
    with open("summary.txt", "w") as f:
        f.write(summary)
    return jsonify({"summary": summary})


@app.route("/extract-details/", methods=["GET"])
def extract_details():
    with open("transcription.txt", "r") as f:
        transcription_text = f.read()
    # Extract details
    details = model.extract(transcription_text)
    # Return the extracted details
    print(details)
    return jsonify(details)


@app.route("/send_mail", methods=["POST"])
def send_mail():
    data = request.get_json()
    sender = data.get("sender")
    to = data.get("to")
    subject = data.get("subject")

    with open("summary.txt", "r") as f:
        message_text = f.read()
    message = create_message(sender, to, subject, message_text)
    send_email(service, "me", message)

    print("Email sent successfully")
    return jsonify({"status": "Email sent successfully"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
