import os
import json
import uuid
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flow_manager import FlowManager, FlowState
from amazon_connect_interactive import InteractiveMessageBuilder, CustomerInfoForm

load_dotenv()

BLUEBUBBLES_URL = os.getenv("BLUEBUBBLES_URL", "http://localhost:1234")
BLUEBUBBLES_PASSWORD = os.getenv("SERVER_PASSWORD")
MY_PORT = int(os.getenv("PORT", 8000))

app = Flask(__name__)
flow_manager = FlowManager()


def send_message(chat_guid: str, message_text: str):
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
            print(f"Successfully sent: {message_text[:50]}...")
        else:
            print(f"Failed to send: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")


def send_interactive_message(chat_guid: str, interactive_template: dict):
    """Send an interactive message (formatted for iMessage)"""
    formatted_text = InteractiveMessageBuilder.format_for_imessage(interactive_template)
    send_message(chat_guid, formatted_text)


def handle_form_flow(chat_guid: str, message_text: str) -> str:
    """
    Handle form filling flow.
    Returns response message for the customer.
    """
    flow, is_complete = flow_manager.process_form_response(chat_guid, message_text)
    
    if is_complete:
        # Form is complete, prepare summary for agent
        flow_manager.complete_form_flow(chat_guid)
        form_data = flow.form_data
        
        summary = f"""✅ Thank you! I've received your information:

📋 **Customer Information:**
• Name: {form_data.name}
• Company: {form_data.company}
• Country: {form_data.country}
• Email: {form_data.email}

An agent will be with you shortly to assist you further."""
        
        return summary
    
    # Get next field to ask for
    next_field = flow.current_field
    if not next_field:
        return "Thank you for your information!"
    
    # Map field IDs to friendly prompts
    field_prompts = {
        "name": "What is your full name?",
        "company": "What is your company name?",
        "country": "Please choose your country (reply with the number):\n" + get_country_list(),
        "email": "What is your email address?"
    }
    
    prompt = field_prompts.get(next_field, f"Please provide your {next_field}:")
    return prompt


def get_country_list() -> str:
    """Get formatted country list"""
    countries = [
        "1. United States",
        "2. Canada",
        "3. United Kingdom",
        "4. Australia",
        "5. Germany",
        "6. France",
        "7. Japan",
        "8. Other"
    ]
    return "\n".join(countries)


def handle_country_selection(message_text: str) -> Optional[str]:
    """Parse country selection from message"""
    country_map = {
        "1": "United States",
        "2": "Canada",
        "3": "United Kingdom",
        "4": "Australia",
        "5": "Germany",
        "6": "France",
        "7": "Japan",
        "8": "Other"
    }
    
    # Try to match by number
    text_clean = message_text.strip()
    if text_clean in country_map:
        return country_map[text_clean]
    
    # Try to match by name
    for code, name in country_map.items():
        if name.lower() in text_clean.lower():
            return name
    
    return None


def process_country_field(chat_guid: str, message_text: str) -> str:
    """Process country field selection"""
    country = handle_country_selection(message_text)
    if country:
        flow, is_complete = flow_manager.process_form_response(chat_guid, country)
        if is_complete:
            flow_manager.complete_form_flow(chat_guid)
            form_data = flow.form_data
            return f"""✅ Thank you! I've received your information:

📋 **Customer Information:**
• Name: {form_data.name}
• Company: {form_data.company}
• Country: {form_data.country}
• Email: {form_data.email}

An agent will be with you shortly to assist you further."""
        else:
            next_field = flow.current_field
            if next_field == "email":
                return "What is your email address?"
    else:
        return "Please select a valid country option (1-8) or type the country name."


@app.post("/")
def webhook():
    """Receive webhook POST events from BlueBubbles."""
    try:
        data = request.get_json(force=True)
        
        if data.get("type") == "new-message":
            msg = data.get("data", {})
            
            if not msg.get("isFromMe"):
                text = msg.get("text", "")
                chat_guid = msg.get("chats", [{}])[0].get("guid")
                
                print(f"Received Message from {chat_guid}: {text}")
                
                flow = flow_manager.get_or_create_flow(chat_guid)
                
                # Handle different flow states
                if flow.state == FlowState.IDLE:
                    # Check for form initiation keywords
                    if any(keyword in text.lower() for keyword in ["form", "register", "sign up", "info", "information"]):
                        # Start form flow
                        flow_manager.start_form_flow(chat_guid)
                        form_template = CustomerInfoForm.create()
                        send_interactive_message(chat_guid, form_template)
                        
                        # Send first field prompt
                        send_message(chat_guid, "What is your full name?")
                    else:
                        # Default greeting
                        send_message(chat_guid, "Hello! 👋\n\nI can help you with:\n• Fill out a form (type 'form')\n• Get assistance\n\nHow can I help you today?")
                
                elif flow.state == FlowState.FILLING_FORM:
                    # Check if we're on the country field
                    if flow.current_field == "country":
                        response = process_country_field(chat_guid, text)
                        send_message(chat_guid, response)
                    else:
                        # Process regular form field
                        response = handle_form_flow(chat_guid, text)
                        send_message(chat_guid, response)
                
                elif flow.state == FlowState.FORM_COMPLETE or flow.state == FlowState.AWAITING_AGENT:
                    # Form is complete, agent can respond
                    send_message(chat_guid, "Thank you for your patience. An agent will respond shortly.")
                
                elif flow.state == FlowState.IN_CONVERSATION:
                    # In conversation with agent - could integrate with Amazon Connect here
                    # For now, just acknowledge
                    pass
        
        return "OK", 200
    
    except Exception as e:
        print(f"Webhook Error: {e}")
        import traceback
        traceback.print_exc()
        return "Internal Server Error", 500


@app.get("/flow/<chat_guid>")
def get_flow_status(chat_guid: str):
    """Get flow status for a chat (useful for debugging)"""
    summary = flow_manager.get_flow_summary(chat_guid)
    return jsonify(summary), 200


@app.post("/flow/<chat_guid>/start-form")
def start_form(chat_guid: str):
    """Manually start a form flow"""
    flow_manager.start_form_flow(chat_guid)
    form_template = CustomerInfoForm.create()
    send_interactive_message(chat_guid, form_template)
    send_message(chat_guid, "What is your full name?")
    return jsonify({"status": "form_started"}), 200


@app.post("/flow/<chat_guid>/reset")
def reset_flow(chat_guid: str):
    """Reset a flow"""
    flow_manager.reset_flow(chat_guid)
    return jsonify({"status": "flow_reset"}), 200


if __name__ == "__main__":
    print(f"Starting Amazon Connect Flow webhook server on port {MY_PORT}...")
    app.run(host="::", port=MY_PORT, debug=True)

