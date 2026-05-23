from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

messages = []
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve uploaded audio and files via url
@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    messages.append(data)
    return "", 200

@app.route("/receive", methods=["GET"])
def receive():
    return jsonify(messages)

@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file", 400
    file = request.files["file"]
    if file.filename == "":
        return "No filename", 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    # Generate accessible file link
    base_url = request.host_url
    file_link = f"{base_url}uploads/{file.filename}"
    name_lower = file.filename.lower()

    # Distinguish voice and common file
    if name_lower.endswith((".m4a", ".mp3", ".wav")):
        new_msg = {
            "msgType": "voice",
            "content": file_link,
            "extraInfo": "Voice message"
        }
    else:
        new_msg = {
            "msgType": "file",
            "content": file_link,
            "extraInfo": file.filename
        }
    messages.append(new_msg)
    return "OK", 200

@app.route("/all_files", methods=["GET"])
def all_files():
    return jsonify({"files": os.listdir(UPLOAD_FOLDER)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
