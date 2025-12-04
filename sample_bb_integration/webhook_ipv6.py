import os
import json
import uuid
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

BLUEBUBBLES_URL = "http://localhost:1234"
BLUEBUBBLES_PASSWORD = os.getenv("SERVER_PASSWORD")

MY_PORT = 8000

app = Flask(__name__)

def send_message(chat_guid, message_text):
    """Send message back to BlueBubbles."""
    url = f"{BLUEBUBBLES_URL}/api/v1/message/text"

    payload = {
        "chatGuid": chat_guid,
        "tempGuid": str(uuid.uuid4()),
        "message": message_text,
        "method": "apple-script",
        }

    params = {
        "password": BLUEBUBBLES_PASSWORD
    }

    try:
        response = requests.post(url, json=payload, params=params)
        if response.status_code == 200:
            print(f"Successfully sent: {message_text}")
        else:
            print(f"Failed to send: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")


@app.post("/")
def webhook():
    """Receive webhook POST events from BlueBubbles."""
    try:
        data = request.get_json(force=True)

        if data.get("type") == "new-message":
            msg = data.get("data", {})

            if not msg.get("isFromMe"):
                text = msg.get("text")
                chat_guid = msg.get("chats", [{}])[0].get("guid")
                print(f"Received Message: {text}")
                
                if text and "ping" in text.lower():
                    send_message(chat_guid, "Pong! 🏓")
        return "OK", 200

    except Exception as e:
        print(f"Webhook Error: {e}")
        return "Internal Server Error", 500


if __name__ == "__main__":
    print(f"Starting Flask bot on IPv6 dual-stack port {MY_PORT}...")

    # Bind to IPv6 wildcard "::" → accepts IPv4 + IPv6 both
    app.run(host="::", port=MY_PORT)