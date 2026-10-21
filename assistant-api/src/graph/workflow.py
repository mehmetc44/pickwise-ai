from langgraph.graph import StateGraph, START, END
from graph.state import AgenticCommerceState
from agents.supervisor import SupervisorAgent
from agents.search_node import SearchNode
from agents.response_builder import ResponseBuilderNode


class AgenticCommerceWorkflow:
    """
    Sistemin ana iş akışını (LangGraph) yöneten sınıf.

    Akış:
        START -> supervisor_node -> search_node -> response_builder_node -> END
    """
    def __init__(self):
        # 1. Bağımlılıkları başlat
        self.supervisor = SupervisorAgent()
        self.search = SearchNode()
        self.response_builder = ResponseBuilderNode()

        # 2. Graph'ı inşa et
        self.app_graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgenticCommerceState)

        # Node'ları ekle
        workflow.add_node("supervisor_node", self.supervisor.invoke)
        workflow.add_node("search_node", self.search.invoke)
        workflow.add_node("response_builder_node", self.response_builder.invoke)

        # Lineer akış
        workflow.add_edge(START, "supervisor_node")
        workflow.add_edge("supervisor_node", "search_node")
        workflow.add_edge("search_node", "response_builder_node")
        workflow.add_edge("response_builder_node", END)

        return workflow.compile()

    def execute(self, user_query: str) -> dict:
        """
        Sistemi dışarıdan tetiklemek için kullanılacak yardımcı metot.
        State'i hazırlar ve graph'ı çalıştırıp sonucu döner.
        """
        initial_state: AgenticCommerceState = {
            "user_query": user_query,
            "intent": "",
            "response": "",
        }

        # Graph'ı senkron olarak çalıştır
        return self.app_graph.invoke(initial_state)
