from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# Store messages
messages = []

# Upload folder config
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------- Core Routes -------------------
# 1. Serve uploaded files (critical for voice playback)
@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 2. Receive messages (text/voice/file) from Android
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    messages.append(data)
    return "", 200

# 3. Get all messages
@app.route("/receive", methods=["GET"])
def receive():
    return jsonify(messages)

# 4. NEW: Clear all messages from the server
@app.route("/clear_messages", methods=["POST"])
def clear_messages():
    global messages
    messages.clear()  # Empty the list permanently
    return jsonify({"status": "cleared"}), 200

# 5. Upload file (only saves, no duplicate message)
@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file", 400

    file = request.files["file"]
    if file.filename == "":
        return "No filename", 400

    # Save the file
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    # Return only the file URL to Android (no auto-created message)
    base_url = request.host_url
    file_url = f"{base_url}uploads/{file.filename}"
    return file_url, 200

# 6. List all files (for your app's file browser)
@app.route("/all_files", methods=["GET"])
def all_files():
    return jsonify({"files": os.listdir(UPLOAD_FOLDER)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
