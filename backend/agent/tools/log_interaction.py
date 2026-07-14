"""
Log Interaction Tool — parses a natural-language description of an HCP meeting
and extracts structured fields via the LLM (entity extraction + classification).
"""

import json
from datetime import date
from langchain_core.tools import tool


@tool
def log_interaction(message: str) -> str:
    """Parse a natural-language interaction description and extract structured
    HCP interaction fields. Use this tool when the user describes a new
    interaction/meeting with an HCP for the first time.

    Args:
        message: The user's natural-language description of the interaction.

    Returns:
        JSON string with extracted fields: hcp_name, interaction_type, date,
        time, attendees, topics_discussed, materials_shared,
        samples_distributed, sentiment, outcomes, follow_up_actions.
    """
    # This is a placeholder — the actual LLM call happens in the graph node.
    # The tool definition is used by LangGraph for routing and schema.
    return json.dumps({"status": "tool_called", "message": message})


LOG_INTERACTION_PROMPT = """You are a pharma CRM assistant. Extract structured interaction details from the user's message.

Today's date is {today}.

Extract the following fields from the message. Return ONLY a valid JSON object with these keys:
- hcp_name: The healthcare professional's name (e.g., "Dr. Smith")
- interaction_type: Type of interaction (Meeting, Call, Email, Video Call). Default to "Meeting" if not specified.
- date: Date of interaction in MM/DD/YYYY format. Use today's date if the user says "today" or doesn't specify.
- time: Time of interaction if mentioned, otherwise null.
- attendees: Other attendees mentioned, comma-separated string, or null.
- topics_discussed: Key discussion topics/products discussed.
- materials_shared: Materials shared (brochures, studies, etc.), or null.
- samples_distributed: Drug samples distributed, or null.
- sentiment: Overall HCP sentiment — must be exactly one of: "positive", "neutral", "negative". Infer from context if not explicitly stated.
- outcomes: Key outcomes or agreements, or null.
- follow_up_actions: Any follow-up actions mentioned, or null.

IMPORTANT: Return ONLY the JSON object, no other text. Use null for fields not mentioned.

User message: {message}"""
