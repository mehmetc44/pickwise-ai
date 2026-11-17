import asyncio

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agents.search_node import SearchNode
from agents.supervisor import SupervisorAgent
from graph.routers import route_search, route_supervisor
from graph.state import AgenticCommerceState
from tools.handoff_tools import delegate_to_search
from tools.mcp_client import load_mcp_tools


class AgenticCommerceWorkflow:
    """
    4 Düğümlü Çift ReAct LangGraph İş Akışı:
      - supervisor_node: Ana ReAct Ajanı & Yanıt Üretici
      - tool_node: Supervisor MCP araçları
      - search_node: Uzman Arama ReAct Ajanı
      - search_tool_node: Search MCP araçları
    """

    def __init__(self):
        self.checkpointer = MemorySaver()
        self.app_graph = None
        self._init_lock = asyncio.Lock()

    async def build_graph(self, use_checkpointer: bool = True):
        mcp_tools = await load_mcp_tools()

        search_tools = [
            tool
            for name, tool in mcp_tools.items()
            if name in {"get_closest_products", "web_search"}
        ]
        if not any(t.name == "get_closest_products" for t in search_tools):
            raise RuntimeError("MCP Server'da 'get_closest_products' tool'u bulunamadı.")

        tool_node_tools = [
            tool
            for name, tool in mcp_tools.items()
            if name in {"get_product_details", "compare_products", "get_product_reviews"}
        ]

        supervisor = SupervisorAgent(tools=[delegate_to_search, *tool_node_tools])
        search_node = SearchNode(tools=search_tools)

        tool_node = ToolNode(tool_node_tools)
        search_tool_node = ToolNode(search_tools, messages_key="search_messages")

        workflow = StateGraph(AgenticCommerceState)

        workflow.add_node("supervisor_node", supervisor.ainvoke)
        workflow.add_node("tool_node", tool_node)
        workflow.add_node("search_node", search_node.ainvoke)
        workflow.add_node("search_tool_node", search_tool_node)

        workflow.add_edge(START, "supervisor_node")
        workflow.add_conditional_edges(
            "supervisor_node",
            route_supervisor,
            {
                "search_node": "search_node",
                "tool_node": "tool_node",
                END: END,
            },
        )
        workflow.add_edge("tool_node", "supervisor_node")

        workflow.add_conditional_edges(
            "search_node",
            route_search,
            {
                "search_tool_node": "search_tool_node",
                "supervisor_node": "supervisor_node",
            },
        )
        workflow.add_edge("search_tool_node", "search_node")

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
            "search_messages": [],
            "search_call_id": "",
            "found_products": [],
            "response": "",
        }
        config = {"configurable": {"thread_id": session_id}}
        return await self.app_graph.ainvoke(initial_state, config=config)

    def execute(self, user_query: str, session_id: str = "default") -> dict:
        return asyncio.run(self.aexecute(user_query, session_id=session_id))
