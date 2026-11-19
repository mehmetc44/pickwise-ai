from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.types import Overwrite

from agents.base_agent import BaseAgent
from graph.state import AgenticCommerceState
from prompts.search_prompt import SEARCH_AGENT_SYSTEM_PROMPT
from utils.mcp_parser import parse_mcp_tool_output


class SearchNode(BaseAgent):
    def __init__(self, tools: list[BaseTool]):
        super().__init__(config_key="search")
        self.llm_with_tools = self.llm.bind_tools(tools)

    def _build_initial_messages(self, state: AgenticCommerceState) -> tuple[str, list[BaseMessage]] | None:
        last_msg = state["messages"][-1]
        if not isinstance(last_msg, AIMessage) or not last_msg.tool_calls:
            return None

        tc = next((c for c in last_msg.tool_calls if c["name"] == "delegate_to_search"), None)
        if tc is None:
            return None

        args = tc.get("args", {})
        query = args.get("query", "")
        limit = int(args.get("limit", 20))

        messages = [
            SystemMessage(content=SEARCH_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=f"Arama Görevi: {query}\nÖnerilen limit: {limit}"),
        ]
        return tc["id"], messages

    def _collect_products(self, history: list[BaseMessage]) -> list[dict[str, Any]]:
        products: list[dict[str, Any]] = []
        seen_ids: set[Any] = set()

        for msg in history:
            if not (isinstance(msg, ToolMessage) and msg.name == "get_closest_products"):
                continue
            for prod in parse_mcp_tool_output(msg.content):
                if "error" in prod:
                    continue
                pid = prod.get("id")
                if pid is not None and pid in seen_ids:
                    continue
                if pid is not None:
                    seen_ids.add(pid)
                products.append(prod)

        products.sort(key=lambda x: x.get("similarity") or 0, reverse=True)
        return products[:20]

    async def ainvoke(self, state: AgenticCommerceState) -> dict:
        search_call_id = state.get("search_call_id", "")
        search_messages = list(state.get("search_messages") or [])

        if not search_call_id:
            task = self._build_initial_messages(state)
            if task is None:
                return {}
            search_call_id, initial_messages = task
            ai_message = await self.llm_with_tools.ainvoke(initial_messages)
            full_history = [*initial_messages, ai_message]
            outbound_search_msgs = Overwrite(full_history)
        else:
            ai_message = await self.llm_with_tools.ainvoke(search_messages)
            full_history = [*search_messages, ai_message]
            outbound_search_msgs = [ai_message]

        if getattr(ai_message, "tool_calls", None):
            return {"search_messages": outbound_search_msgs, "search_call_id": search_call_id}

        report_text = ai_message.content if isinstance(ai_message.content, str) else str(ai_message.content)
        return {
            "messages": [ToolMessage(tool_call_id=search_call_id, name="delegate_to_search", content=report_text)],
            "search_messages": outbound_search_msgs,
            "search_call_id": "",
            "found_products": self._collect_products(full_history),
        }
