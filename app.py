from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import shutil
import sys

app = Flask(__name__)
CORS(app)

# Critical for Render: force logs to print instantly, no buffer
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
os.environ["PYTHONUNBUFFERED"] = "1"

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Receive text message
@app.route("/send-message", methods=["POST"])
def receive_text():
    try:
        raw_data = request.get_json(force=True)
        print("----------------------------------------")
        print("RECEIVED TEXT JSON:")
        print(raw_data)
        print("----------------------------------------")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"ERROR parsing text: {str(e)}")
        return jsonify({"status": "error"}), 400

# Receive file upload
@app.route("/upload-file", methods=["POST"])
def receive_file():
    try:
        file = request.files.get("file")
        form_data = dict(request.form)
        print("----------------------------------------")
        print("RECEIVED FILE UPLOAD")
        print("Form data:", form_data)
        print("File name:", file.filename if file else "No file")
        print("----------------------------------------")

        if file and file.filename:
            save_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(save_path)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"ERROR file upload: {str(e)}")
        return jsonify({"status": "error"}), 400

# List all files
@app.route("/list-all-files")
def list_all_files():
    file_list = os.listdir(UPLOAD_FOLDER)
    return jsonify({
        "total_files": len(file_list),
        "files": file_list
    })

# View single file
@app.route("/files/<filename>")
def view_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Clear all files
@app.route("/clear-all")
def clear_all():
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    return "✅ All files cleared"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
