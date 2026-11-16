"""
AgenticCommerce — AI Servisi (Port: 8000)

Supervisor ReAct Agent + MCP ToolNode + SearchNode iş akışı.
"""

from contextlib import asynccontextmanager
import os
import sys
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

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


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        final_state = await workflow_engine.aexecute(
            user_query=request.query,
            session_id=request.session_id,
        )

        return {
            "response": final_state.get("response", ""),
            "found_products": final_state.get("found_products", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
