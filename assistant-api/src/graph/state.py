from typing_extensions import TypedDict


class AgenticCommerceState(TypedDict):
    """
    LangGraph için minimal durum (state) yapısı.
    """
    user_query: str   # Kullanıcının mesajı
    intent: str       # Supervisor'ın belirlediği niyet
    response: str     # Node'ların ürettiği (ve en son response builder'ın formatladığı) cevap