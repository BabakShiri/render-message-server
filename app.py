from flask import Flask, request, jsonify

app = Flask(__name__)
message_box = []

@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    message_box.append(data)
    return jsonify({"status": "success", "message": "received"})

@app.route('/receive', methods=['GET'])
def receive_messages():
    return jsonify(message_box)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
