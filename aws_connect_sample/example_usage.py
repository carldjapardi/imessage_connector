"""
Example usage of Amazon Connect interactive flows
This demonstrates how to programmatically create and use interactive messages
"""
from amazon_connect_interactive import InteractiveMessageBuilder, CustomerInfoForm
from flow_manager import FlowManager, FlowState

# Example 1: Create a list picker
list_picker = InteractiveMessageBuilder.create_list_picker(
    title="Choose your country",
    subtitle="Please select from the options below",
    items=[
        {"title": "United States", "identifier": "US"},
        {"title": "Canada", "identifier": "CA"},
        {"title": "United Kingdom", "identifier": "UK"},
    ]
)

print("List Picker Template:")
print(InteractiveMessageBuilder.format_for_imessage(list_picker))
print("\n" + "="*50 + "\n")

# Example 2: Create a custom form
custom_form = InteractiveMessageBuilder.create_form(
    title="Contact Form",
    subtitle="We'd love to hear from you!",
    fields=[
        InteractiveMessageBuilder.create_text_field(
            label="Your Name",
            field_id="name",
            required=True,
            placeholder="John Doe"
        ),
        InteractiveMessageBuilder.create_text_field(
            label="Email Address",
            field_id="email",
            required=True,
            placeholder="john@example.com",
            input_type="email"
        ),
        InteractiveMessageBuilder.create_list_field(
            label="How did you hear about us?",
            field_id="source",
            options=[
                {"title": "Social Media", "identifier": "social"},
                {"title": "Friend/Colleague", "identifier": "friend"},
                {"title": "Search Engine", "identifier": "search"},
                {"title": "Other", "identifier": "other"}
            ],
            required=True
        )
    ]
)

print("Custom Form Template:")
print(InteractiveMessageBuilder.format_for_imessage(custom_form))
print("\n" + "="*50 + "\n")

# Example 3: Use the pre-built customer info form
customer_form = CustomerInfoForm.create()
print("Customer Info Form Template:")
print(InteractiveMessageBuilder.format_for_imessage(customer_form))
print("\n" + "="*50 + "\n")

# Example 4: Flow management
flow_manager = FlowManager()

# Simulate a customer flow
chat_guid = "example-chat-123"
flow_manager.start_form_flow(chat_guid)

print("Flow started. Current state:", flow_manager.get_or_create_flow(chat_guid).state.value)
print("Current field:", flow_manager.get_or_create_flow(chat_guid).current_field)

# Simulate customer responses
responses = ["John Doe", "Acme Corp", "1", "john@example.com"]

for response in responses:
    flow, is_complete = flow_manager.process_form_response(chat_guid, response)
    print(f"\nResponse: {response}")
    print(f"Current field: {flow.current_field}")
    print(f"Form complete: {is_complete}")
    
    if is_complete:
        print("\nForm Data:")
        print(flow.form_data.to_dict())
        break

# Get flow summary
summary = flow_manager.get_flow_summary(chat_guid)
print("\n" + "="*50)
print("Flow Summary:")
print(summary)

