from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from agents.base_agent import BaseAgent
from graph.state import AgenticCommerceState
from prompts.supervisor_prompt import SUPERVISOR_SYSTEM_PROMPT


class delegate_to_search(BaseModel):
    """Katalogda ürün aramak veya teknik uyumluluk araştırmak gerektiğinde işi uzman Search Agent'a devreder."""

    query: str = Field(description="Kullanıcının ürün/hediye/uyumluluk isteğini özetleyen net Türkçe metin.")
    limit: int = Field(default=20, description="Arama başına getirilecek maksimum aday ürün sayısı.")


class SupervisorAgent(BaseAgent):
    def __init__(self, tools: list[BaseTool]):
        super().__init__(config_key="supervisor")
        self.llm_with_tools = self.llm.bind_tools([delegate_to_search, *tools])

    async def ainvoke(self, state: AgenticCommerceState) -> dict:
        system_prompt = SUPERVISOR_SYSTEM_PROMPT
        context_products = state.get("context_products") or []
        if context_products:
            lines = ["\nKULLANICININ ARAYÜZDEN SEÇTİĞİ ÜRÜNLER (Aktif Bağlam):"]
            for p in context_products:
                lines.append(f"- [ID: {p.get('id')}] {p.get('name')} | Fiyat: {p.get('price')}")
            lines.append("Kullanıcı 'bunları karşılaştır', 'bunun yorumları nasıl' veya 'detayını ver' dediğinde yukarıdaki ID'leri doğrudan kullan.")
            system_prompt = f"{system_prompt}\n" + "\n".join(lines)

        messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
        ai_message = await self.llm_with_tools.ainvoke(messages)

        update: dict = {"messages": [ai_message]}
        if not getattr(ai_message, "tool_calls", None):
            update["response"] = (
                ai_message.content if isinstance(ai_message.content, str) else str(ai_message.content)
            )

        return update
