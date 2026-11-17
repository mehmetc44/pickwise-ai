from langchain_core.tools import tool


@tool
def delegate_to_search(query: str, limit: int = 8) -> str:
    """
    Katalogda ürün aramak veya teknik uyumluluk araştırmak gerektiğinde
    işi uzman Search Agent'a devreder.
    query: Kullanıcının ürün/hediye/uyumluluk isteğini özetleyen net Türkçe metin.
    limit: Arama başına getirilecek maksimum aday ürün sayısı (varsayılan 8).
    """
    return f"Search Agent'a yönlendirildi: {query}"
