import os
import uuid
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from webhook_fastapi import send_message

load_dotenv()

BLUEBUBBLES_URL = "http://localhost:1234"
BLUEBUBBLES_PASSWORD = os.getenv("SERVER_PASSWORD")

MY_PORT = 8000

app = FastAPI()

@app.post("/")
async def webhook(request: Request):
    try:
        data = await request.json()
        print(data)
        if data.get("type") == "new-message":
            message = data.get("data", {})
            if not message.get("isFromMe"):
                text = message.get("text")
                attachment = message.get("attachments")
                if attachment:
                    att_guid = attachment.get("guid")
                    att_type = attachment.get("mimeType")
                    chat_guid = message.get("chats", [{}])[0].get("guid")
                    print(f"Received Attachment Type: {att_type}")
                elif text:
                    chat_guid = message.get("chats", [{}])[0].get("guid")
                    print(f"Received Message: {text}")
                    send_message(chat_guid, str(data))
        return {"status": "ok"} 
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    print(f"Starting FastAPI bot on IPv6 port {MY_PORT}...")
    uvicorn.run("bb_json_dump:app", host="::", port=MY_PORT, reload=True)