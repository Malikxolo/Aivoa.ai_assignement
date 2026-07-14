"""
Edit Interaction Tool — parses a correction/update message and modifies ONLY
the specific fields that the user wants changed, leaving everything else intact.
Uses LLM for intent classification + selective field extraction.
"""

import json
from langchain_core.tools import tool


@tool
def edit_interaction(message: str, current_fields: str) -> str:
    """Parse a correction or update message and determine which specific fields
    to change in an already-filled HCP interaction form. Only the fields
    explicitly mentioned for change should be updated.

    Args:
        message: The user's correction/update message.
        current_fields: JSON string of the current form field values.

    Returns:
        JSON string with ONLY the fields that should be updated.
    """
    return json.dumps({"status": "tool_called", "message": message})


EDIT_INTERACTION_PROMPT = """You are a pharma CRM assistant. The user wants to correct or update specific fields in an already-logged HCP interaction.

Current form values:
{current_fields}

The user's correction message:
{message}

Identify ONLY the fields that need to be changed based on the user's message.
Return a JSON object containing ONLY the fields that should be updated, with their new values.
Do NOT include fields that should remain unchanged.

Valid field keys are: hcp_name, interaction_type, date, time, attendees, topics_discussed,
materials_shared, samples_distributed, sentiment, outcomes, follow_up_actions.

IMPORTANT: Return ONLY the JSON object with changed fields, no other text.
If the user says "the name was actually Dr. John", only return {{"hcp_name": "Dr. John"}}.
If the user corrects sentiment to negative, only return {{"sentiment": "negative"}}."""
