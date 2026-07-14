"""
Chat API route — receives user messages, invokes the LangGraph agent,
and returns structured field updates + AI response message.
"""

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage

from schemas import ChatRequest, ChatResponse, InteractionFields
from agent.graph import agent_graph
from database import get_db
from models import Interaction
from fastapi import Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["chat"])

# In-memory interaction state (per-session; for a production app this would
# be session-based or DB-backed).
_current_interaction: dict = {}


@router.post("/chat", response_model=ChatResponse, response_model_exclude_none=True)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Process a chat message through the LangGraph agent.

    The agent classifies intent, invokes the appropriate tool with LLM-powered
    extraction, and returns:
    - message: AI response text
    - tool_used: which tool was invoked
    - fields_updated: structured field changes to apply to Redux state
    """
    global _current_interaction

    try:
        # Build initial agent state
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "current_interaction": _current_interaction,
            "tool_used": None,
            "fields_updated": None,
            "response_message": None,
        }

        # Invoke the LangGraph agent
        result = agent_graph.invoke(initial_state)

        # Update server-side interaction state
        interaction_id = request.interaction_id
        if result.get("fields_updated"):
            updates = result["fields_updated"]
            if result.get("tool_used") == "log_interaction":
                _current_interaction = updates
                # Save to DB
                new_interaction = Interaction(**{k: v for k, v in updates.items() if hasattr(Interaction, k)})
                db.add(new_interaction)
                db.commit()
                db.refresh(new_interaction)
                interaction_id = str(new_interaction.id)
            elif result.get("tool_used") == "edit_interaction":
                _current_interaction.update(updates)
                # Update in DB if we have an ID
                if interaction_id:
                    db_interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
                    if db_interaction:
                        for k, v in updates.items():
                            if hasattr(db_interaction, k):
                                setattr(db_interaction, k, v)
                        db.commit()
                        db.refresh(db_interaction)

        # Build response
        fields = None
        if result.get("fields_updated"):
            fields = InteractionFields(**result["fields_updated"])

        return ChatResponse(
            message=result.get("response_message", "I'm not sure how to help with that."),
            tool_used=result.get("tool_used"),
            fields_updated=fields,
            interaction_id=interaction_id,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/reset")
async def reset_interaction():
    """Reset the current interaction state."""
    global _current_interaction
    _current_interaction = {}
    return {"status": "ok", "message": "Interaction state reset."}
