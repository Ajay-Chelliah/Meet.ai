from flask import Flask, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment

# import whisper
import os
from main import summarise
from main import extract
from transformers import pipeline
from gmail import service, create_message, send_email

app = Flask(__name__)
CORS(app)

# Directory to save audio files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/process-audio/", methods=["POST"])
def process_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["file"]
    if audio_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(file_path)

    # Convert to WAV and Transcribe
    # Convert MP3 to WAV (16kHz, mono)
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio_path = os.path.join(UPLOAD_FOLDER, "converted_audio.wav")
    audio.save(audio_path, format="wav")


@app.route("/transcribe-audio/", methods=["GET"])
def transcribe_audio():
    # Load the audio file
    audio_file = "uploads/converted_audio.wav"

    # Load Whisper model
    transcriber = pipeline(
        "automatic-speech-recognition", model="openai/whisper-medium"
    )

    # Transcribe recorded audio
    transcription = transcriber(
        audio_file, return_timestamps=True, generate_kwargs={"language": "en"}
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
    summary = summarise(transcription_text)
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
    details = extract(transcription_text)
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
