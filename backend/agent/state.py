from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State schema for the LangGraph HCP interaction agent."""

    # Chat message history
    messages: Annotated[list[BaseMessage], add_messages]

    # Current interaction form state (what's displayed on the left panel)
    current_interaction: Optional[dict]

    # The tool that was invoked and its result
    tool_used: Optional[str]
    fields_updated: Optional[dict]
    response_message: Optional[str]
