from flask import Flask, render_template, request, jsonify
from chatbot import Chatbot
from database import init_db, save_message, get_recent_messages, clear_messages

app = Flask(__name__)
bot = Chatbot()
init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400
    if len(message) > 1000:
        return jsonify({"error": "Message is too long. Keep it under 1000 characters."}), 400

    response = bot.reply(message)
    save_message("user", message)
    save_message("bot", response)

    return jsonify({"response": response})

@app.get("/api/history")
def history():
    return jsonify({"messages": get_recent_messages(50)})

@app.delete("/api/history")
def clear_history():
    clear_messages()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
