from typing import Annotated, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgenticCommerceState(TypedDict):
    """
    LangGraph ortak durum (state) yapısı.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    found_products: list[dict[str, Any]]
    response: str
