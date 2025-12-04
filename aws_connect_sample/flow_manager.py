from enum import Enum
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


class FlowState(Enum):
    """States a customer can be in during a flow"""
    IDLE = "idle"
    WAITING_FOR_FORM = "waiting_for_form"
    FILLING_FORM = "filling_form"
    FORM_COMPLETE = "form_complete"
    AWAITING_AGENT = "awaiting_agent"
    IN_CONVERSATION = "in_conversation"


@dataclass
class FormData:
    """Stores form field data"""
    name: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([self.name, self.company, self.country, self.email])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "company": self.company,
            "country": self.country,
            "email": self.email
        }


@dataclass
class CustomerFlow:
    """Tracks a customer's flow state"""
    chat_guid: str
    state: FlowState = FlowState.IDLE
    form_data: FormData = field(default_factory=FormData)
    current_field: Optional[str] = None
    field_order: list = field(default_factory=lambda: ["name", "company", "country", "email"])
    field_index: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    conversation_history: list = field(default_factory=list)
    
    def get_next_field(self) -> Optional[str]:
        """Get the next field to collect"""
        if self.field_index < len(self.field_order):
            return self.field_order[self.field_index]
        return None
    
    def set_field_value(self, field_id: str, value: str):
        """Set a field value"""
        if hasattr(self.form_data, field_id):
            setattr(self.form_data, field_id, value)
            self.last_updated = datetime.now()
    
    def advance_to_next_field(self):
        """Move to the next field"""
        if self.field_index < len(self.field_order) - 1:
            self.field_index += 1
            self.current_field = self.get_next_field()
        else:
            self.current_field = None
    
    def reset(self):
        """Reset the flow to initial state"""
        self.state = FlowState.IDLE
        self.form_data = FormData()
        self.field_index = 0
        self.current_field = None
        self.last_updated = datetime.now()


class FlowManager:
    """Manages customer flows across multiple chats"""
    
    def __init__(self):
        self.flows: Dict[str, CustomerFlow] = {}
    
    def get_or_create_flow(self, chat_guid: str) -> CustomerFlow:
        """Get existing flow or create a new one"""
        if chat_guid not in self.flows:
            self.flows[chat_guid] = CustomerFlow(chat_guid=chat_guid)
        return self.flows[chat_guid]
    
    def start_form_flow(self, chat_guid: str):
        """Start a form collection flow"""
        flow = self.get_or_create_flow(chat_guid)
        flow.state = FlowState.FILLING_FORM
        flow.field_index = 0
        flow.current_field = flow.get_next_field()
        flow.last_updated = datetime.now()
        return flow
    
    def process_form_response(self, chat_guid: str, message_text: str):
        """
        Process a customer's response during form filling.
        Returns (flow, is_complete)
        """
        flow = self.get_or_create_flow(chat_guid)
        
        if flow.state != FlowState.FILLING_FORM:
            return flow, False
        
        current_field = flow.current_field
        if not current_field:
            return flow, False
        
        # Set the field value
        flow.set_field_value(current_field, message_text.strip())
        
        # Add to conversation history
        flow.conversation_history.append({
            "type": "customer_input",
            "field": current_field,
            "value": message_text.strip(),
            "timestamp": datetime.now().isoformat()
        })
        
        # Move to next field
        flow.advance_to_next_field()
        
        # Check if form is complete
        if flow.form_data.is_complete():
            flow.state = FlowState.FORM_COMPLETE
            return flow, True
        
        return flow, False
    
    def complete_form_flow(self, chat_guid: str):
        """Mark form flow as complete and ready for agent"""
        flow = self.get_or_create_flow(chat_guid)
        flow.state = FlowState.AWAITING_AGENT
        flow.last_updated = datetime.now()
        return flow
    
    def start_conversation(self, chat_guid: str):
        """Start agent-customer conversation"""
        flow = self.get_or_create_flow(chat_guid)
        flow.state = FlowState.IN_CONVERSATION
        flow.last_updated = datetime.now()
        return flow
    
    def reset_flow(self, chat_guid: str):
        """Reset a flow"""
        if chat_guid in self.flows:
            self.flows[chat_guid].reset()
    
    def get_flow_summary(self, chat_guid: str) -> Dict[str, Any]:
        """Get a summary of the flow for agent review"""
        flow = self.get_or_create_flow(chat_guid)
        return {
            "chat_guid": chat_guid,
            "state": flow.state.value,
            "form_data": flow.form_data.to_dict(),
            "is_form_complete": flow.form_data.is_complete(),
            "conversation_history": flow.conversation_history,
            "last_updated": flow.last_updated.isoformat()
        }

