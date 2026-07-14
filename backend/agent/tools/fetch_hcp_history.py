import json
from langchain_core.tools import tool
from database import SessionLocal
from models import Interaction

@tool
def fetch_hcp_history(message: str) -> str:
    """Fetch past interactions for a given HCP."""
    db = SessionLocal()
    try:
        records = db.query(Interaction).filter(
            Interaction.hcp_name.ilike(f"%{message}%")
        ).order_by(Interaction.created_at.desc()).limit(3).all()
        
        if not records:
            return json.dumps({
                "status": "tool_called", 
                "message": f"I haven't talked to {message} yet."
            })
            
        history_lines = []
        for r in records:
            date_str = r.date if r.date else r.created_at.strftime("%Y-%m-%d")
            line = f"On {date_str}, you had a {r.interaction_type}."
            if r.topics_discussed:
                line += f" Discussed: {r.topics_discussed}."
            if r.sentiment:
                line += f" Sentiment: {r.sentiment}."
            history_lines.append(line)
            
        return json.dumps({
            "status": "tool_called",
            "message": " ".join(history_lines)
        })
    finally:
        db.close()

FETCH_HCP_HISTORY_PROMPT = """You are an assistant retrieving historical context.
The user wants to know about past interactions with a specific HCP (e.g. "What did we discuss with Dr. Smith last time?" or "What did I discuss with him?").

The current HCP loaded in the form is: "{current_hcp}"

Extract ONLY the name of the HCP from the user's message (e.g., "Dr. Smith").
If the user uses pronouns like "him", "her", "them", or doesn't specify a name, you should output "{current_hcp}" if it's provided.

User message: {message}

Return a valid JSON object with a key "hcp_name" containing the extracted name.

IMPORTANT: Return ONLY the JSON object, no other text.
Example:
{{"hcp_name": "Dr. Smith"}}
"""
