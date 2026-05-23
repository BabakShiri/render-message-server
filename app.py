from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Store messages
messages = []

# Store uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Receive text/image/video/file
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    messages.append(data)
    return "", 200

# Get all messages
@app.route("/receive", methods=["GET"])
def receive():
    return jsonify(messages)

# Upload voice/file and generate corresponding message
@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file", 400

    file = request.files["file"]
    if file.filename == "":
        return "No filename", 400

    # Save safely
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    # Judge file type and create matched message
    filename = file.filename.lower()
    file_url = f"https://render-message-server.onrender.com/uploads/{file.filename}"

    if filename.endswith((".m4a", ".mp3", ".wav")):
        # Voice file, add voice type message
        voice_msg = {
            "msgType": "voice",
            "content": file_url,
            "extraInfo": "Voice Message"
        }
        messages.append(voice_msg)
    else:
        # Other common files
        file_msg = {
            "msgType": "file",
            "content": file_url,
            "extraInfo": file.filename
        }
        messages.append(file_msg)

    return "OK", 200

# List all files
@app.route("/all_files", methods=["GET"])
def all_files():
    return jsonify({"files": os.listdir(UPLOAD_FOLDER)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
