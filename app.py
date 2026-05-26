from flask import Flask, request, jsonify, send_from_directory
import os
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Receive text message from Android
@app.route("/send-message", methods=["POST"])
def receive_text_message():
    try:
        message_data = request.get_json()
        print("Received Text Message:", message_data)
        return jsonify({
            "status": "success",
            "message": "Text received"
        }), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"status": "error", "detail": str(e)}), 400

# Receive file / image upload
@app.route("/upload-file", methods=["POST"])
def receive_upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"status": "error", "detail": "No file uploaded"}), 400

        file = request.files["file"]
        timestamp = request.form.get("timestamp", "")
        msg_type = request.form.get("msgType", "")
        username = request.form.get("username", "")
        receivename = request.form.get("receivename", "")

        print("Received File Upload Info")
        print(f"timestamp: {timestamp}")
        print(f"msgType: {msg_type}")
        print(f"username: {username}")
        print(f"receivename: {receivename}")
        print(f"File Name: {file.filename}")

        if file.filename:
            save_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(save_path)
            print(f"File saved to: {save_path}")

        return jsonify({
            "status": "success",
            "message": "File uploaded"
        }), 200
    except Exception as e:
        print("Upload Error:", str(e))
        return jsonify({"status": "error", "detail": str(e)}), 400

# List all uploaded files
@app.route("/list-all-files", methods=["GET"])
def list_all_files():
    try:
        file_list = os.listdir(UPLOAD_FOLDER)
        return jsonify({
            "total_files": len(file_list),
            "files": file_list
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 400

# Access single file
@app.route("/files/<filename>", methods=["GET"])
def view_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Clear all files
@app.route("/clear-all", methods=["GET"])
def clear_all_files():
    try:
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        return "✅ All files cleared successfully!", 200
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
