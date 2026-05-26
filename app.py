from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# --------------------------
# Store all messages in memory
# --------------------------
messages = []

# --------------------------
# Receive message from Android
# --------------------------
@app.route("/send-message", methods=["POST"])
def receive_message():
    data = request.get_json()
    messages.append(data)  # Add new message to the list
    print(f"Received message #{len(messages)}: {data}")
    return jsonify({"status": "ok", "count": len(messages)}), 200

# --------------------------
# View list of messages as JSON
# --------------------------
@app.route("/messages")
def get_messages():
    return jsonify({
        "total_messages": len(messages),
        "messages": messages
    })

# --------------------------
# View messages in a simple HTML page
# --------------------------
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

# --------------------------
# Clear all messages
# --------------------------
@app.route("/messages/clear")
def clear_messages():
    global messages
    messages = []
    return "All messages cleared!"

if __name__ == "__main__":
    os.environ["PYTHONUNBUFFERED"] = "1"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
