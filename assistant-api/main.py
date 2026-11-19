"""
AgenticCommerce — AI Servisi (Port: 8000)

Supervisor ReAct Agent + MCP ToolNode + SearchNode iş akışı.
"""

from contextlib import asynccontextmanager
import asyncio
import os
import sys
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel

# Add src directory to Python path and load .env before LangChain/LangGraph imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

import core.config  # noqa: E402, F401
from core.config import settings
from graph.workflow import AgenticCommerceWorkflow

workflow_engine = AgenticCommerceWorkflow()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await workflow_engine.initialize()
    except Exception as exc:
        print(f"⚠️ Başlangıçta MCP/Workflow başlatılamadı (ilk istekte tekrar denenecek): {exc}")
    yield


app = FastAPI(
    title="AgenticCommerce — AI Service",
    description="LangGraph + MCP tabanlı e-ticaret asistan servisi.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"
    context_products: Optional[List[Any]] = None


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-service"}


async def _enrich_found_products(products: list[dict]) -> list[dict]:
    if not products:
        return []

    catalog_url = settings.CATALOG_API_URL.rstrip("/")

    async def _fetch_image(client: httpx.AsyncClient, prod: dict) -> dict:
        if prod.get("images") or prod.get("image_url"):
            return prod
        pid = prod.get("id")
        if not pid:
            return prod
        try:
            resp = await client.get(f"{catalog_url}/api/v1/products/{pid}")
            if resp.status_code == 200:
                full = resp.json()
                return {**prod, "images": full.get("images", [])}
        except Exception:
            pass
        return prod

    async with httpx.AsyncClient(timeout=5.0) as client:
        return await asyncio.gather(*(_fetch_image(client, p) for p in products))


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        final_state = await workflow_engine.aexecute(
            user_query=request.query,
            session_id=request.session_id,
            context_products=request.context_products,
        )

        enriched_products = await _enrich_found_products(final_state.get("found_products", []))

        return {
            "response": final_state.get("response", ""),
            "found_products": enriched_products,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
