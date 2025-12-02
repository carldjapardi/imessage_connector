import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from gpt_response import genereate_response

load_dotenv()

BLUEBUBBLES_URL = "http://localhost:1234"
BLUEBUBBLES_PASSWORD = os.getenv("SERVER_PASSWORD")

MY_PORT = 8000

app = FastAPI()

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
async def webhook():
    try:
        await data = request.get_json()
        if data.get("type") == "new-message":
            message = data.get("data", {})
            if not message.get("isFromMe"):
                text = message.get("text")
                chat_guid = msg.get("chats", [{}])[0].get("guid")
                print(f"Received Message: {text}")

                if text:
                    gpt_response = generate_response(text)
                    send_message(chat_guid, gpt_response)
        return {"status": "ok"} 
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    print(f"Starting FastAPI bot on IPv6 dual-stack port {MY_PORT}...")
    uvicorn.run("webhook_fastapi:app", host="::", port=MY_PORT, reload=True)