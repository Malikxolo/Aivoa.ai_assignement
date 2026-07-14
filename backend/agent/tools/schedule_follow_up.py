"""
Schedule Follow-up Tool — parses temporal dates and appends a formatted task to follow_up_actions.
"""

import json
from langchain_core.tools import tool

@tool
def schedule_follow_up(message: str) -> str:
    """Schedule a follow-up action based on the user's request."""
    return json.dumps({"status": "tool_called", "message": message})


SCHEDULE_FOLLOW_UP_PROMPT = """You are a smart temporal scheduling assistant for a pharma CRM.
The user wants to schedule a follow-up task. You need to extract the date they mentioned and the actual task, then return a cleanly formatted string.

Today's date is: {today}

User message: {message}

Figure out the exact date they mean (e.g., "next Tuesday", "in 2 weeks", "tomorrow") and convert it to YYYY-MM-DD.
Then format the task like this exactly:
"[YYYY-MM-DD] Scheduled: <Task Description>"

Return ONLY a valid JSON object with the key "follow_up_actions" containing the newly scheduled task string.

IMPORTANT: Return ONLY the JSON object, no other text.
Example:
{{"follow_up_actions": "[2026-07-21] Scheduled: Meeting to check on samples"}}
"""
