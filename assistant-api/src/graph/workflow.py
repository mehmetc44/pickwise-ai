import asyncio
from pathlib import Path
import sys
from typing import Literal

# LangGraph Studio (langgraph dev) gibi dış giriş noktaları için src/ dizinini sys.path'e ekle
_SRC_DIR = str(Path(__file__).resolve().parents[1])
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agents.search_node import SearchNode
from agents.supervisor import SupervisorAgent
from graph.state import AgenticCommerceState
from tools.handoff_tools import delegate_to_search
from tools.mcp_client import load_mcp_tools


def _route_supervisor(state: AgenticCommerceState) -> Literal["search_node", "tool_node", "__end__"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return END

    if any(tc["name"] == "delegate_to_search" for tc in last_message.tool_calls):
        return "search_node"

    return "tool_node"


class AgenticCommerceWorkflow:
    """
    3 Düğümlü LangGraph İş Akışı:
      - supervisor_node: Ana ReAct Ajanı & Yanıt Üretici
      - tool_node: MCP üzerinden get_product_details, compare_products, get_product_reviews
      - search_node: MCP üzerinden get_closest_products çalıştıran arama düğümü
    """

    def __init__(self):
        self.checkpointer = MemorySaver()
        self.app_graph = None
        self._init_lock = asyncio.Lock()

    async def build_graph(self, use_checkpointer: bool = True):
        mcp_tools = await load_mcp_tools()

        search_tool = mcp_tools.get("get_closest_products")
        if search_tool is None:
            raise RuntimeError("MCP Server'da 'get_closest_products' tool'u bulunamadı.")

        tool_node_tools = [
            tool
            for name, tool in mcp_tools.items()
            if name in {"get_product_details", "compare_products", "get_product_reviews"}
        ]

        supervisor = SupervisorAgent(tools=[delegate_to_search, *tool_node_tools])
        search_node = SearchNode(get_closest_products_tool=search_tool)
        tool_node = ToolNode(tool_node_tools)

        workflow = StateGraph(AgenticCommerceState)

        workflow.add_node("supervisor_node", supervisor.ainvoke)
        workflow.add_node("tool_node", tool_node)
        workflow.add_node("search_node", search_node.ainvoke)

        workflow.add_edge(START, "supervisor_node")
        workflow.add_conditional_edges(
            "supervisor_node",
            _route_supervisor,
            {
                "search_node": "search_node",
                "tool_node": "tool_node",
                END: END,
            },
        )
        workflow.add_edge("tool_node", "supervisor_node")
        workflow.add_edge("search_node", "supervisor_node")

        if use_checkpointer:
            return workflow.compile(checkpointer=self.checkpointer)
        return workflow.compile()

    async def initialize(self):
        if self.app_graph is not None:
            return

        async with self._init_lock:
            if self.app_graph is not None:
                return
            self.app_graph = await self.build_graph(use_checkpointer=True)

    async def aexecute(self, user_query: str, session_id: str = "default") -> dict:
        await self.initialize()
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "found_products": [],
            "response": "",
        }
        config = {"configurable": {"thread_id": session_id}}
        return await self.app_graph.ainvoke(initial_state, config=config)

    def execute(self, user_query: str, session_id: str = "default") -> dict:
        return asyncio.run(self.aexecute(user_query, session_id=session_id))


_STUDIO_GRAPH = None
_STUDIO_LOCK = asyncio.Lock()


async def make_studio_graph():
    """
    LangGraph Studio (langgraph dev) için checkpointer'sız grafik factory fonksiyonu.
    Her /schemas, /graph, /subgraphs isteğinde MCP subprocess'ini yeniden başlatmamak için cache'lenir.
    """
    global _STUDIO_GRAPH
    if _STUDIO_GRAPH is not None:
        return _STUDIO_GRAPH

    async with _STUDIO_LOCK:
        if _STUDIO_GRAPH is not None:
            return _STUDIO_GRAPH
        wf = AgenticCommerceWorkflow()
        _STUDIO_GRAPH = await wf.build_graph(use_checkpointer=False)
        return _STUDIO_GRAPH
