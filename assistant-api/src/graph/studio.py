import asyncio
from pathlib import Path
import sys

_SRC_DIR = str(Path(__file__).resolve().parents[1])
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from graph.workflow import AgenticCommerceWorkflow

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

