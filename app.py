from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)

messages = []
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allow ALL file types, set reasonable max size (20MB)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

# Text message endpoints
@app.route("/send-message", methods=["POST"])
def receive_message():
    data = request.get_json()
    messages.append(data)
    print(f"Received message #{len(messages)}: {data}")
    return jsonify({"status": "ok", "count": len(messages)}), 200

@app.route("/messages")
def get_messages():
    return jsonify({
        "total_messages": len(messages),
        "messages": messages
    })

@app.route("/messages/view")
def view_messages():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chat Messages</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .msg { border: 1px solid #ccc; padding: 10px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>All Messages ({{ total }})</h1>
        {% for msg in messages %}
        <div class="msg">
            <strong>From:</strong> {{ msg.username }} → {{ msg.receivename }}<br>
            <strong>Time:</strong> {{ msg.timestamp }}<br>
            <strong>Type:</strong> {{ msg.msgType }}<br>
            <strong>Content:</strong> {{ msg.content }}
        </div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, total=len(messages), messages=messages)

@app.route("/messages/clear")
def clear_messages():
    global messages
    messages = []
    return "All messages cleared!"

# File upload endpoint (support image/video/audio/docs/voice)
@app.route("/upload-file", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"status": "error", "message": "No selected file"}), 400

        timestamp = request.form.get("timestamp", str(int(time.time() * 1000)))
        username = request.form.get("username", "AndroidUser")
        receivename = request.form.get("receivename", "ChatReceiver")

        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        file_msg = {
            "timestamp": int(timestamp),
            "content": file.filename,
            "msgType": "file",
            "username": username,
            "receivename": receivename,
            "isSentByMe": True,
            "file_url": f"/files/{filename}"
        }
        messages.append(file_msg)

        print(f"File uploaded successfully: {filename}")
        return jsonify({
            "status": "ok",
            "filename": filename,
            "url": f"/files/{filename}"
        }), 200

    except Exception as e:
        print(f"Upload error: {str(e)}"))
        return jsonify({"status": "error", "message": str(e)}), 500

# Add this new GET route
@app.route("/upload-file", methods=["GET"])
def upload_file_guide():
    return "Use POST method with form-data to upload files."
# File download
@app.route("/files/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/files/list")
def list_files():
    return jsonify({
        "total_files": len(os.listdir(UPLOAD_FOLDER)),
        "files": os.listdir(UPLOAD_FOLDER)
    })

@app.route("/files/clear")
def clear_files():
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    return "All files cleared!"

if __name__ == "__main__":
    os.environ["PYTHONUNBUFFERED"] = "1"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
