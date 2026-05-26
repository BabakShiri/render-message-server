import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import shutil
import sys

# Enable full request logging
logging.basicConfig(level=logging.INFO)
werkzeug_log = logging.getLogger('werkzeug')
werkzeug_log.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)
os.environ["PYTHONUNBUFFERED"] = "1"
sys.stdout.reconfigure(line_buffering=True)

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/send-message", methods=["POST"])
def receive_text():
    print("\n===== New POST /send-message =====")
    print("Headers:", dict(request.headers))
    print("Raw JSON:", request.get_json(force=True, silent=True))
    return jsonify({"status": "ok"}), 200

@app.route("/upload-file", methods=["POST"])
def receive_file():
    print("\n===== New POST /upload-file =====")
    print("Form data:", dict(request.form))
    print("File:", request.files.get("file"))
    file = request.files.get("file")
    if file and file.filename:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return jsonify({"status": "ok"}), 200

@app.route("/list-all-files")
def list_all_files():
    return jsonify({
        "total_files": len(os.listdir(UPLOAD_FOLDER)),
        "files": os.listdir(UPLOAD_FOLDER)
    })

@app.route("/files/<filename>")
def view_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/clear-all")
def clear_all():
    for f in os.listdir(UPLOAD_FOLDER):
        os.unlink(os.path.join(UPLOAD_FOLDER, f))
    return "All files cleared"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
