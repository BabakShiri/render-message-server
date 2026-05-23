from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# Save text messages
message_list = []

# All files save here
FILE_FOLDER = "all_files"
if not os.path.exists(FILE_FOLDER):
    os.mkdir(FILE_FOLDER)

# Root test endpoint
@app.route("/")
def home():
    return "Render message server is running! 🚀"

# 1. Send text message
@app.route("/send", methods=["POST"])
def send_msg():
    data = request.json
    message_list.append(data)
    return jsonify({"status":"success"})

# 2. Get all text messages
@app.route("/receive", methods=["GET"])
def get_msg():
    return jsonify(message_list)

# 3. Upload any file (photo, video, voice, app apk, all files)
@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"status":"error","msg":"No file selected"})
    file = request.files["file"]
    sender = request.form.get("sender","user")
    filename = file.filename
    file.save(os.path.join(FILE_FOLDER, filename))
    
    # Add a file message to the list so it appears in chat
    message_list.append({
        "sender": sender,
        "type": "file",
        "filename": filename,
        "status": "success"
    })
    
    return jsonify({
        "status":"success",
        "sender":sender,
        "filename":filename
    })

# 4. Download file by name
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(FILE_FOLDER, filename, as_attachment=True)

# 5. View all uploaded file names
@app.route("/all_files", methods=["GET"])
def show_all_files():
    files = os.listdir(FILE_FOLDER)
    return jsonify({"files":files})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
