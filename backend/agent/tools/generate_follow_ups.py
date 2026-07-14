"""
Generate Follow-ups Tool — analyzes the interaction to suggest next steps.
"""

import json
from langchain_core.tools import tool

@tool
def generate_follow_ups(message: str) -> str:
    """Generate strategic follow-up actions based on the interaction."""
    return json.dumps({"status": "tool_called", "message": message})


GENERATE_FOLLOW_UPS_PROMPT = """You are a strategic pharma CRM assistant. 
Based on the current logged interaction details and the user's request, provide strategic coaching on what the sales rep should do next.

Current Interaction Details:
{current_fields}

User message: {message}

Return a valid JSON object with the key "coaching_message" containing your advice as a string.

IMPORTANT: Return ONLY the JSON object, no other text.
Example:
{{"coaching_message": "Since Dr. Smith had a negative sentiment about efficacy, I suggest sending him the Phase III long-term safety data."}}
"""
