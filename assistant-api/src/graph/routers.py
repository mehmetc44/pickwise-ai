from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.graph import END

from graph.state import AgenticCommerceState


def route_supervisor(state: AgenticCommerceState) -> Literal["search_node", "tool_node", "__end__"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return END

    if any(tc["name"] == "delegate_to_search" for tc in last_message.tool_calls):
        return "search_node"

    return "tool_node"


def route_search(state: AgenticCommerceState) -> Literal["search_tool_node", "supervisor_node"]:
    search_messages = state.get("search_messages") or []
    if search_messages:
        last_search_msg = search_messages[-1]
        if isinstance(last_search_msg, AIMessage) and getattr(last_search_msg, "tool_calls", None):
            return "search_tool_node"
    return "supervisor_node"

