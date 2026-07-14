from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    interaction_id: Optional[str] = None


class InteractionFields(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    ai_suggested_follow_ups: Optional[list[str]] = None


class ChatResponse(BaseModel):
    message: str
    tool_used: Optional[str] = None
    fields_updated: Optional[InteractionFields] = None
    interaction_id: Optional[str] = None
