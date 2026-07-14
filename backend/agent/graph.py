"""
LangGraph Agent — orchestrates the HCP interaction tools.

The agent receives a chat message, uses the LLM to decide which tool to invoke,
executes the tool with LLM-powered extraction/classification, and returns
structured field updates to the frontend.
"""

import json
import re
from datetime import date

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.tools.log_interaction import log_interaction, LOG_INTERACTION_PROMPT
from agent.tools.edit_interaction import edit_interaction, EDIT_INTERACTION_PROMPT
from agent.tools.generate_follow_ups import generate_follow_ups, GENERATE_FOLLOW_UPS_PROMPT
from agent.tools.schedule_follow_up import schedule_follow_up, SCHEDULE_FOLLOW_UP_PROMPT
from agent.tools.fetch_hcp_history import fetch_hcp_history, FETCH_HCP_HISTORY_PROMPT
from config import settings


def _get_llm():
    """Create a Groq LLM instance."""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0.1,
        max_tokens=1000,
    )


def _extract_json(text: str) -> dict:
    """Extract JSON object from LLM response text, handling markdown fences."""
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        return json.loads(fence_match.group(1))

    brace_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if brace_match:
        return json.loads(brace_match.group(0))

    return json.loads(text)


def _clean_fields(fields: dict) -> dict:
    """Remove null/None values from extracted fields."""
    return {k: v for k, v in fields.items() if v is not None and v != "null"}


# ──────────────────── GRAPH NODES ────────────────────


def router_node(state: AgentState) -> AgentState:
    llm = _get_llm()
    last_message = state["messages"][-1].content
    has_interaction = bool(
        state.get("current_interaction")
        and any(v for v in state["current_interaction"].values() if v)
    )

    router_prompt = f"""You are an AI assistant for pharma sales reps managing HCP interactions.

Classify the user's message into exactly one of these tool categories:
- "log_interaction": Describing a NEW interaction/meeting.
- "edit_interaction": CORRECTING or UPDATING an already-logged interaction.
- "generate_follow_ups": Asking for suggestions on what to do next based on the meeting.
- "schedule_follow_up": Asking to schedule a meeting or follow-up task on a specific date.
- "fetch_hcp_history": Asking about past meetings or history with a specific doctor.
- "out_of_scope": Anything else (greetings, general chat, unrelated questions).

Current form state: {"FILLED" if has_interaction else "EMPTY"}
User message: "{last_message}"

Reply with ONLY one of: log_interaction, edit_interaction, generate_follow_ups, schedule_follow_up, fetch_hcp_history, out_of_scope"""

    response = llm.invoke([SystemMessage(content=router_prompt)])
    intent = response.content.strip().lower().replace('"', "").replace("'", "")

    # Normalize to valid tool name
    if "log" in intent:
        tool_name = "log_interaction"
    elif "edit" in intent:
        tool_name = "edit_interaction"
    elif "generate" in intent:
        tool_name = "generate_follow_ups"
    elif "schedule" in intent:
        tool_name = "schedule_follow_up"
    elif "fetch" in intent or "history" in intent:
        tool_name = "fetch_hcp_history"
    else:
        tool_name = "out_of_scope"

    if tool_name == "edit_interaction" and not has_interaction:
        tool_name = "log_interaction"
    if tool_name == "generate_follow_ups" and not has_interaction:
        tool_name = "out_of_scope" # Can't generate followups if no interaction is logged

    return {
        **state,
        "tool_used": tool_name,
    }


def log_interaction_node(state: AgentState) -> AgentState:
    llm = _get_llm()
    last_message = state["messages"][-1].content
    today = date.today().strftime("%m/%d/%Y")

    prompt = LOG_INTERACTION_PROMPT.format(today=today, message=last_message)
    response = llm.invoke([SystemMessage(content=prompt)])

    try:
        fields = _extract_json(response.content)
        fields = _clean_fields(fields)
    except (json.JSONDecodeError, ValueError):
        err_msg = "I had trouble parsing that interaction. Could you rephrase it?"
        return {
            **state,
            "tool_used": "log_interaction",
            "fields_updated": {},
            "response_message": err_msg,
            "messages": state["messages"] + [AIMessage(content=err_msg)],
        }

    response_msg = (
        "✅ **Interaction logged successfully!** The details have been automatically populated. "
        "Would you like me to suggest a specific follow-up action, such as scheduling a meeting?"
    )

    return {
        **state,
        "tool_used": "log_interaction",
        "fields_updated": fields,
        "current_interaction": fields,
        "response_message": response_msg,
        "messages": state["messages"] + [AIMessage(content=response_msg)],
    }


def edit_interaction_node(state: AgentState) -> AgentState:
    llm = _get_llm()
    last_message = state["messages"][-1].content
    current = state.get("current_interaction", {})

    prompt = EDIT_INTERACTION_PROMPT.format(
        current_fields=json.dumps(current, indent=2), message=last_message
    )
    response = llm.invoke([SystemMessage(content=prompt)])

    try:
        changed_fields = _extract_json(response.content)
        changed_fields = _clean_fields(changed_fields)
    except (json.JSONDecodeError, ValueError):
        err_msg = "I couldn't understand which fields to update. Could you be more specific?"
        return {
            **state,
            "tool_used": "edit_interaction",
            "fields_updated": {},
            "response_message": err_msg,
            "messages": state["messages"] + [AIMessage(content=err_msg)],
        }

    updated_interaction = {**current, **changed_fields}
    change_list = ", ".join(f"**{k.replace('_', ' ').title()}** → {v}" for k, v in changed_fields.items())
    response_msg = f"✏️ **Interaction updated!** Changed: {change_list}. All other fields remain unchanged."

    return {
        **state,
        "tool_used": "edit_interaction",
        "fields_updated": changed_fields,
        "current_interaction": updated_interaction,
        "response_message": response_msg,
        "messages": state["messages"] + [AIMessage(content=response_msg)],
    }


def generate_follow_ups_node(state: AgentState) -> AgentState:
    llm = _get_llm()
    last_message = state["messages"][-1].content
    current = state.get("current_interaction", {})

    prompt = GENERATE_FOLLOW_UPS_PROMPT.format(
        current_fields=json.dumps(current, indent=2), message=last_message
    )
    response = llm.invoke([SystemMessage(content=prompt)])

    try:
        result = _extract_json(response.content)
        coaching_msg = result.get("coaching_message", "I couldn't generate coaching advice.")
    except (json.JSONDecodeError, ValueError):
        coaching_msg = "I couldn't generate coaching advice. Please try again."

    response_msg = f"💡 **Follow-up Suggestion:**\n\n{coaching_msg}"

    return {
        **state,
        "tool_used": "generate_follow_ups",
        "fields_updated": None, # Doesn't update form
        "response_message": response_msg,
        "messages": state["messages"] + [AIMessage(content=response_msg)],
    }


def schedule_follow_up_node(state: AgentState) -> AgentState:
    llm = _get_llm()
    last_message = state["messages"][-1].content
    current = state.get("current_interaction", {})
    today = date.today().strftime("%Y-%m-%d")

    prompt = SCHEDULE_FOLLOW_UP_PROMPT.format(today=today, message=last_message)
    response = llm.invoke([SystemMessage(content=prompt)])

    try:
        changed_fields = _extract_json(response.content)
        changed_fields = _clean_fields(changed_fields)
        task_desc = changed_fields.get("follow_up_actions", "a meeting")
    except (json.JSONDecodeError, ValueError):
        err_msg = "I couldn't figure out the date for that task. Could you be more specific?"
        return {
            **state,
            "tool_used": "schedule_follow_up",
            "fields_updated": None,
            "response_message": err_msg,
            "messages": state["messages"] + [AIMessage(content=err_msg)],
        }

    hcp_name = current.get("hcp_name", "the HCP")
    # This response message will be shown in the chat AND parsed by the frontend for the popup
    response_msg = f"📅 **Task Scheduled:** {task_desc} with {hcp_name}."

    return {
        **state,
        "tool_used": "schedule_follow_up",
        "fields_updated": None, # Do NOT update the form fields
        "response_message": response_msg,
        "messages": state["messages"] + [AIMessage(content=response_msg)],
    }


def fetch_hcp_history_node(state: AgentState) -> AgentState:
    llm = _get_llm()
    last_message = state["messages"][-1].content
    current = state.get("current_interaction", {})
    current_hcp = current.get("hcp_name", "")

    # 1. Ask LLM to extract HCP name
    prompt = FETCH_HCP_HISTORY_PROMPT.format(message=last_message, current_hcp=current_hcp)
    response = llm.invoke([SystemMessage(content=prompt)])

    try:
        result = _extract_json(response.content)
        hcp_name = result.get("hcp_name")
        
        # Fallback to current_hcp if LLM extracted nothing but we have one in context
        if not hcp_name or hcp_name.lower() in ["him", "her", "them"]:
            hcp_name = current_hcp

        if not hcp_name:
            history_msg = "Please fill the HCP Name in the form first, or specify the doctor's name in your message."
        else:
            # 2. Actually run the tool!
            tool_response_str = fetch_hcp_history.invoke(hcp_name)
            tool_response = json.loads(tool_response_str)
            history_msg = tool_response.get("message", f"I haven't talked to {hcp_name} yet.")
    except (json.JSONDecodeError, ValueError):
        history_msg = "I couldn't fetch the history for that HCP right now."

    response_msg = f"🔍 **Previous conversation:**\n\n{history_msg}"

    return {
        **state,
        "tool_used": "fetch_hcp_history",
        "fields_updated": None, # Doesn't update form
        "response_message": response_msg,
        "messages": state["messages"] + [AIMessage(content=response_msg)],
    }


def out_of_scope_node(state: AgentState) -> AgentState:
    """Handle out of scope requests with a strict hardcoded message."""
    err_msg = "Sorry, this platform is specifically for logging HCP interactions, scheduling follow-ups, and fetching history. I cannot assist with general inquiries or out-of-scope requests."
    return {
        **state,
        "tool_used": "out_of_scope",
        "fields_updated": None,
        "response_message": err_msg,
        "messages": state["messages"] + [AIMessage(content=err_msg)],
    }


# ──────────────────── ROUTING ────────────────────


def route_after_classification(state: AgentState) -> str:
    return state.get("tool_used", "out_of_scope")


# ──────────────────── BUILD GRAPH ────────────────────


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("log_interaction", log_interaction_node)
    graph.add_node("edit_interaction", edit_interaction_node)
    graph.add_node("generate_follow_ups", generate_follow_ups_node)
    graph.add_node("schedule_follow_up", schedule_follow_up_node)
    graph.add_node("fetch_hcp_history", fetch_hcp_history_node)
    graph.add_node("out_of_scope", out_of_scope_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_after_classification,
        {
            "log_interaction": "log_interaction",
            "edit_interaction": "edit_interaction",
            "generate_follow_ups": "generate_follow_ups",
            "schedule_follow_up": "schedule_follow_up",
            "fetch_hcp_history": "fetch_hcp_history",
            "out_of_scope": "out_of_scope",
        },
    )

    graph.add_edge("log_interaction", END)
    graph.add_edge("edit_interaction", END)
    graph.add_edge("generate_follow_ups", END)
    graph.add_edge("schedule_follow_up", END)
    graph.add_edge("fetch_hcp_history", END)
    graph.add_edge("out_of_scope", END)

    return graph.compile()


agent_graph = build_graph()
