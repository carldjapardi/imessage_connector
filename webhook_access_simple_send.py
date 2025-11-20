import json
import requests
import os
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

load_dotenv()

BLUEBUBBLES_URL = "http://localhost:1234" 
BLUEBUBBLES_PASSWORD = os.getenv('SERVER_PASSWORD')

MY_PORT = 8000 

def send_message(chat_guid, message_text):
    """Sends a message back to BlueBubbles to be delivered via iMessage"""
    url = f"{BLUEBUBBLES_URL}/api/v1/message/text"
    
    payload = {
        "chatGuid": chat_guid,
        "tempGuid": str(uuid.uuid4()),  # Generate a unique GUID for each message
        "message": message_text,
        "method": "apple-script" # Use 'apple-script' if you don't have Private API set up
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

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle incoming data from BlueBubbles"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            
            # Check if this is a new message event
            if data.get('type') == 'new-message':
                message_data = data.get('data', {})
                
                # Avoid replying to yourself!
                if not message_data.get('isFromMe'):
                    text = message_data.get('text')
                    chat_guid = message_data.get('chats', [{}])[0].get('guid')
                    
                    print(f"Received Message: {text}")
                    
                    # --- EXAMPLE LOGIC ---
                    if text and "ping" in text.lower():
                        send_message(chat_guid, "Pong! 🏓")
            
            # Tell BlueBubbles we received it successfully
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            
        except Exception as e:
            print(f"Error handling webhook: {e}")
            self.send_response(500)
            self.end_headers()

if __name__ == "__main__":
    print(f"Starting bot on port {MY_PORT}...")
    server = HTTPServer(('localhost', MY_PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()