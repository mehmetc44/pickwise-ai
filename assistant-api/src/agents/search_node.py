from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.types import Overwrite

from agents.base_agent import BaseAgent
from graph.state import AgenticCommerceState
from prompts.search_prompt import SEARCH_AGENT_SYSTEM_PROMPT
from utils.mcp_parser import parse_mcp_tool_output


class SearchNode(BaseAgent):
    """
    `search_tool_node` ile ReAct döngüsü kuran uzman Arama Ajanı düğümü.
    """

    def __init__(self, tools: list[BaseTool]):
        super().__init__(config_key="search")
        self.llm_with_tools = self.llm.bind_tools(tools)

    async def ainvoke(self, state: AgenticCommerceState) -> dict:
        search_messages = list(state.get("search_messages") or [])
        search_call_id = state.get("search_call_id", "")

        # 1. Supervisor'dan yeni bir delegate_to_search görevi geldiyse iç geçmişi başlat
        if not search_call_id:
            last_main_msg = state["messages"][-1]
            if not isinstance(last_main_msg, AIMessage) or not last_main_msg.tool_calls:
                return {}

            search_tc = next(
                (tc for tc in last_main_msg.tool_calls if tc["name"] == "delegate_to_search"),
                None,
            )
            if search_tc is None:
                return {}

            search_call_id = search_tc["id"]
            args = search_tc.get("args", {})
            query = args.get("query", "")
            limit = int(args.get("limit", 8))

            task_prompt = (
                f"Arama Görevi: {query}\n"
                f"Her arama çağrısında önerilen limit: {limit}"
            )
            initial_messages = [
                SystemMessage(content=SEARCH_AGENT_SYSTEM_PROMPT),
                HumanMessage(content=task_prompt),
            ]
            ai_message = await self.llm_with_tools.ainvoke(initial_messages)
            raw_search_msgs = [*initial_messages, ai_message]
            outbound_search_msgs = Overwrite(raw_search_msgs)
            full_history = raw_search_msgs
        else:
            # 2. search_tool_node dönüşü: mevcut search_messages üzerinden devam et
            ai_message = await self.llm_with_tools.ainvoke(search_messages)
            outbound_search_msgs = [ai_message]
            full_history = [*search_messages, ai_message]

        if getattr(ai_message, "tool_calls", None):
            return {
                "search_messages": outbound_search_msgs,
                "search_call_id": search_call_id,
            }

        collected_products: list[dict[str, Any]] = []
        seen_ids: set[Any] = set()
        for msg in full_history:
            if isinstance(msg, ToolMessage) and msg.name == "get_closest_products":
                for prod in parse_mcp_tool_output(msg.content):
                    if "error" in prod:
                        continue
                    pid = prod.get("id")
                    if pid is not None and pid in seen_ids:
                        continue
                    if pid is not None:
                        seen_ids.add(pid)
                    collected_products.append(prod)

        report_text = (
            ai_message.content
            if isinstance(ai_message.content, str)
            else str(ai_message.content)
        )

        return {
            "messages": [
                ToolMessage(
                    tool_call_id=search_call_id,
                    name="delegate_to_search",
                    content=report_text,
                )
            ],
            "search_messages": outbound_search_msgs,
            "search_call_id": "",
            "found_products": collected_products,
        }
