import json
from typing import Any
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import BaseTool

from graph.state import AgenticCommerceState


def _parse_tool_output(raw: Any) -> list[dict[str, Any]]:
    """
    MCP (langchain-mcp-adapters) çıktısını normalize eder.
    MCP araçları veriyi `[{'type': 'text', 'text': '...'}]` blokları halinde döner;
    bu fonksiyon blokların içindeki JSON'u çözer ve düz `list[dict]` üretir.
    """
    items: list[dict[str, Any]] = []

    def _collect(obj: Any):
        if isinstance(obj, dict):
            if obj.get("type") == "text" and isinstance(obj.get("text"), str):
                try:
                    _collect(json.loads(obj["text"]))
                except json.JSONDecodeError:
                    pass
            else:
                items.append(obj)
        elif isinstance(obj, list):
            for el in obj:
                _collect(el)
        elif isinstance(obj, str):
            try:
                _collect(json.loads(obj))
            except json.JSONDecodeError:
                pass

    _collect(raw)
    return items


class SearchNode:
    """
    Şimdilik MCP üzerindeki `get_closest_products` aracını çalıştırarak
    ürünleri listeleyen ve Supervisor'a başarılı durum raporu dönen arama düğümü.
    """

    def __init__(self, get_closest_products_tool: BaseTool):
        self.get_closest_products_tool = get_closest_products_tool

    async def ainvoke(self, state: AgenticCommerceState) -> dict:
        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            return {}

        tool_messages: list[ToolMessage] = []
        collected_products: list[dict[str, Any]] = []

        for tool_call in last_message.tool_calls:
            if tool_call["name"] != "delegate_to_search":
                continue

            args = tool_call.get("args", {})
            query = args.get("query", "")
            limit = int(args.get("limit", 8))

            raw_result = await self.get_closest_products_tool.ainvoke(
                {"query": query, "limit": limit}
            )
            products = _parse_tool_output(raw_result)

            if products and "error" in products[0]:
                content = f"Arama sırasında hata oluştu: {products[0]['error']}"
            elif not products:
                content = f"Arama tamamlandı ancak '{query}' için katalogda ürün bulunamadı."
            else:
                collected_products.extend(products)
                lines = [
                    f"Arama başarılı! '{query}' sorgusu için {len(products)} ürün bulundu:"
                ]
                for p in products:
                    lines.append(
                        f"- [ID: {p.get('id')}] {p.get('name')} | Marka: {p.get('brand') or '-'} | "
                        f"Fiyat: {p.get('price')} {p.get('currency') or 'TRY'} | "
                        f"Puan: {p.get('rating') or '-'} ({p.get('review_count') or 0} yorum) | "
                        f"Kategori: {p.get('full_path') or '-'}"
                    )
                content = "\n".join(lines)

            tool_messages.append(
                ToolMessage(
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"],
                    content=content,
                )
            )

        return {
            "messages": tool_messages,
            "found_products": collected_products,
        }
