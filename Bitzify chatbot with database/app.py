from flask import Flask, request, jsonify
import os
from utils.file_handler import handle_file_upload
from utils.chatbot import chatbot_reply

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        handle_file_upload(filepath)
        return jsonify({"message": f"{file.filename} uploaded and processed."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_query = data.get("message", "")
    if not user_query:
        return jsonify({"error": "No message provided"}), 400

    reply = chatbot_reply(user_query)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
