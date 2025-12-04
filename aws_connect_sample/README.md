# iMessage Business Messages with Amazon Connect Flows

This project integrates Amazon Connect-style interactive flows with iMessage Business Messages via BlueBubbles. It provides support for interactive elements like forms, list pickers, and templates.

## Features

- **Interactive Forms**: Collect customer information with structured forms
- **List Pickers**: Present options for customers to choose from
- **Flow Management**: Track customer state through multi-step interactions
- **Amazon Connect Compatible**: Uses Amazon Connect/Lex interactive message format
- **Agent Integration**: Ready for agent handoff after form completion

## Example Flow

The system supports a customer information form flow:

1. **Customer initiates**: Types "form" or "register"
2. **Agent sends form**: System presents a formatted form with fields:
   - Name
   - Company
   - Country (list picker)
   - Email
3. **Customer fills form**: System guides customer through each field
4. **Form completion**: System confirms and prepares for agent response

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
SERVER_PASSWORD=your_bluebubbles_password
BLUEBUBBLES_URL=http://localhost:1234
PORT=8000
```

3. Configure BlueBubbles webhook to point to this server (port 8000)

## Usage

### Start the webhook server:
```bash
python webhook_connect_flows.py
```

### Test the form flow:
1. Send a message to your iMessage number with "form" or "register"
2. The system will present the customer information form
3. Follow the prompts to fill out each field
4. After completion, the form data is ready for agent review

### API Endpoints

- `POST /` - Main webhook endpoint (receives BlueBubbles events)
- `GET /flow/<chat_guid>` - Get flow status for a chat
- `POST /flow/<chat_guid>/start-form` - Manually start a form flow
- `POST /flow/<chat_guid>/reset` - Reset a flow

## Architecture

### `amazon_connect_interactive.py`
- Interactive message builders (forms, list pickers)
- Amazon Connect-compatible JSON templates
- iMessage text formatting fallback

### `flow_manager.py`
- Flow state management
- Customer data tracking
- Form completion logic

### `webhook_connect_flows.py`
- Main webhook handler
- Flow orchestration
- BlueBubbles integration

## Extending the System

### Adding New Form Fields

Edit `CustomerInfoForm.create()` in `amazon_connect_interactive.py`:

```python
fields.append(
    InteractiveMessageBuilder.create_text_field(
        label="Phone Number",
        field_id="phone",
        required=True,
        placeholder="+1 (555) 123-4567",
        input_type="tel"
    )
)
```

### Adding New Flow Types

1. Add new state to `FlowState` enum in `flow_manager.py`
2. Add handling logic in `webhook_connect_flows.py`
3. Create corresponding interactive message templates

### Integrating with Amazon Connect

The interactive message templates are already in Amazon Connect format. To integrate:

1. Set up Amazon Connect instance
2. Configure Amazon Lex bot
3. Use the interactive message builders to send responses via Connect API
4. Replace BlueBubbles message sending with Connect API calls

## Example Interactive Message Format

```json
{
  "templateType": "Form",
  "version": "1.0",
  "data": {
    "content": {
      "title": "Customer Information Form",
      "subtitle": "Please provide the following information:",
      "fields": [
        {
          "label": "Name",
          "identifier": "name",
          "type": "text",
          "required": true
        }
      ]
    }
  }
}
```

## Notes

- Currently uses text-based formatting for iMessage (full interactive support requires Amazon Connect integration)
- Flow state is stored in memory (consider adding persistence for production)
- Country selection supports both numeric and text input

