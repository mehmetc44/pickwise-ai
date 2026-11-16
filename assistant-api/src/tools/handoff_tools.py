from langchain_core.tools import tool


@tool
def delegate_to_search(query: str, limit: int = 8) -> str:
    """
    Katalogda ürün aramak gerektiğinde işi uzman Search Node'a devreder.
    query: Aranacak ürün veya kullanıcı ihtiyacını özetleyen temiz Türkçe arama metni.
    limit: Getirilecek maksimum ürün sayısı (varsayılan 8).
    """
    # Bu aracın gövdesi doğrudan çalışmaz; LangGraph conditional edge ile
    # çağrıyı search_node'a yönlendirmek için handoff şeması olarak kullanılır.
    return f"Search Node'a yönlendirildi: {query}"

