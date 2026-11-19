from typing import Annotated, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgenticCommerceState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    search_messages: Annotated[list[BaseMessage], add_messages]
    search_call_id: str
    context_products: list[dict[str, Any]]
    found_products: list[dict[str, Any]]
    response: str
