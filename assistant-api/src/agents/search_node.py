from graph.state import AgenticCommerceState


class SearchNode:
    """
    Ürün arama düğümü.
    TODO: Search agent burada tanımlanacak.
    """
    def __init__(self):
        pass

    def invoke(self, state: AgenticCommerceState) -> dict:
        """LangGraph node metodu. Şimdilik state'i değiştirmeden geçirir."""
        return {}
