from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'm4a', 'mp3', 'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# In-memory storage (replace with a database in production)
messages = []

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/send', methods=['POST'])
def send_message():
    """Receive and store messages from clients"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    messages.append(data)
    return jsonify({"status": "success"}), 200

@app.route('/receive', methods=['GET'])
def receive_messages():
    """Send stored messages to clients (polling endpoint)"""
    return jsonify(messages), 200

@app.route('/upload_file', methods=['POST'])
def upload_file():
    """Handle file uploads from clients"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    sender = request.form.get('sender', 'unknown')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid conflicts
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Return ONLY the filename (not full URL) to the client
        # This is critical for your Android app to download it later
        return jsonify({
            "filename": unique_filename,
            "sender": sender
        }), 200
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    """Serve uploaded files to clients (matches your Android Retrofit endpoint)"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=False  # False for inline viewing, True for download
    )

@app.route('/all_files', methods=['GET'])
def list_files():
    """List all uploaded files (for debugging)"""
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify({"files": files}), 200

@app.route('/clear_messages', methods=['POST'])
def clear_messages():
    """Clear all stored messages (called when user clears chat)"""
    global messages
    messages = []
    return jsonify({"status": "cleared"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
