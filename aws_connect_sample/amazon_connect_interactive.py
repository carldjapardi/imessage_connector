"""
Amazon Connect Interactive Messages Module
Provides builders for interactive message templates compatible with Amazon Connect/Lex format
"""
import json
from typing import List, Dict, Optional, Any


class InteractiveMessageBuilder:
    """Builder for Amazon Connect interactive message templates"""
    
    @staticmethod
    def create_list_picker(title: str, items: List[Dict[str, str]], subtitle: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a ListPicker interactive message template.
        
        Args:
            title: The title of the list picker
            items: List of items with 'title' and 'identifier' keys
            subtitle: Optional subtitle text
            
        Returns:
            Dictionary representing the ListPicker template
        """
        return {
            "templateType": "ListPicker",
            "version": "1.0",
            "data": {
                "content": {
                    "title": title,
                    "subtitle": subtitle,
                    "items": items
                }
            }
        }
    
    @staticmethod
    def create_form(title: str, fields: List[Dict[str, Any]], subtitle: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Form interactive message template.
        
        Args:
            title: The title of the form
            fields: List of form fields, each with 'label', 'type', 'required', etc.
            subtitle: Optional subtitle text
            
        Returns:
            Dictionary representing the Form template
        """
        return {
            "templateType": "Form",
            "version": "1.0",
            "data": {
                "content": {
                    "title": title,
                    "subtitle": subtitle,
                    "fields": fields
                }
            }
        }
    
    @staticmethod
    def create_text_field(label: str, field_id: str, required: bool = True, 
                         placeholder: Optional[str] = None, input_type: str = "text") -> Dict[str, Any]:
        """
        Create a text input field for a form.
        
        Args:
            label: Field label
            field_id: Unique identifier for the field
            required: Whether the field is required
            placeholder: Placeholder text
            input_type: Input type (text, email, tel, etc.)
        """
        field = {
            "label": label,
            "identifier": field_id,
            "type": input_type,
            "required": required
        }
        if placeholder:
            field["placeholder"] = placeholder
        return field
    
    @staticmethod
    def create_list_field(label: str, field_id: str, options: List[Dict[str, str]], 
                         required: bool = True) -> Dict[str, Any]:
        """
        Create a list/dropdown field for a form.
        
        Args:
            label: Field label
            field_id: Unique identifier for the field
            options: List of options with 'title' and 'identifier' keys
            required: Whether the field is required
        """
        return {
            "label": label,
            "identifier": field_id,
            "type": "list",
            "required": required,
            "options": options
        }
    
    @staticmethod
    def format_for_imessage(interactive_message: Dict[str, Any]) -> str:
        """
        Convert an interactive message template to a text format suitable for iMessage.
        This is a fallback for when full interactive support isn't available.
        
        Args:
            interactive_message: The interactive message template
            
        Returns:
            Formatted text string for iMessage
        """
        template_type = interactive_message.get("templateType")
        content = interactive_message.get("data", {}).get("content", {})
        
        if template_type == "ListPicker":
            title = content.get("title", "")
            subtitle = content.get("subtitle", "")
            items = content.get("items", [])
            
            text = f"📋 {title}\n"
            if subtitle:
                text += f"{subtitle}\n\n"
            
            for idx, item in enumerate(items, 1):
                text += f"{idx}. {item.get('title', '')}\n"
            
            text += "\nPlease reply with the number of your choice."
            return text
        
        elif template_type == "Form":
            title = content.get("title", "")
            subtitle = content.get("subtitle", "")
            fields = content.get("fields", [])
            
            text = f"📝 {title}\n"
            if subtitle:
                text += f"{subtitle}\n\n"
            
            for field in fields:
                label = field.get("label", "")
                field_type = field.get("type", "text")
                required = field.get("required", False)
                req_marker = " *" if required else ""
                
                if field_type == "list":
                    options = field.get("options", [])
                    text += f"{label}{req_marker}:\n"
                    for idx, option in enumerate(options, 1):
                        text += f"  {idx}. {option.get('title', '')}\n"
                else:
                    placeholder = field.get("placeholder", "")
                    if placeholder:
                        text += f"{label}{req_marker}: {placeholder}\n"
                    else:
                        text += f"{label}{req_marker}: ___\n"
            
            text += "\nPlease provide your information above."
            return text
        
        return json.dumps(interactive_message, indent=2)


class CustomerInfoForm:
    """Pre-built form for collecting customer information"""
    
    @staticmethod
    def create() -> Dict[str, Any]:
        """Create the customer information form with name, company, country, and email fields."""
        countries = [
            {"title": "United States", "identifier": "US"},
            {"title": "Canada", "identifier": "CA"},
            {"title": "United Kingdom", "identifier": "UK"},
            {"title": "Australia", "identifier": "AU"},
            {"title": "Germany", "identifier": "DE"},
            {"title": "France", "identifier": "FR"},
            {"title": "Japan", "identifier": "JP"},
            {"title": "Other", "identifier": "OTHER"}
        ]
        
        fields = [
            InteractiveMessageBuilder.create_text_field(
                label="Name",
                field_id="name",
                required=True,
                placeholder="Enter your full name"
            ),
            InteractiveMessageBuilder.create_text_field(
                label="Company",
                field_id="company",
                required=True,
                placeholder="Enter your company name"
            ),
            InteractiveMessageBuilder.create_list_field(
                label="Choose Country",
                field_id="country",
                options=countries,
                required=True
            ),
            InteractiveMessageBuilder.create_text_field(
                label="Email",
                field_id="email",
                required=True,
                placeholder="your.email@example.com",
                input_type="email"
            )
        ]
        
        return InteractiveMessageBuilder.create_form(
            title="Customer Information Form",
            subtitle="Please provide the following information:",
            fields=fields
        )

