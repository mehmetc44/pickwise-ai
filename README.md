# AgenticCommerce

AgenticCommerce is an AI-powered e-commerce assistant ecosystem built with **LangGraph**, **LangChain**, **FastMCP**, and **pgvector**. Going beyond traditional keyword-based search bars, it provides autonomous reasoning, semantic product discovery, web-assisted compatibility research, product comparison, and customer review summarization — laying the foundation for **visual search**, **outfit & style recommendations**, and **virtual try-on** experiences.

---

## ✨ Key Capabilities

* **Conversational Product Discovery:** Understands complex, natural-language shopping intents and surfaces the most relevant products using semantic vector search.
* **Web-Assisted Compatibility Research:** Researches external technical specifications and compatibility details when catalog titles alone are not enough.
* **Product Comparison & Review Insights:** Compares selected products side-by-side and summarizes customer reviews into clear pros and cons.
* **Interactive Shopping UI:** Allows users to select products directly from the catalog as chat context, trigger quick comparisons/summaries, and view both highlighted picks in the assistant panel and full results on the main grid.

---

## 🏗️ Project Structure

* **`assistant-api` (Port `8000`):** FastAPI service powered by LangGraph and LangChain for multi-turn conversational orchestration and reasoning.
* **`mcp-server`:** Model Context Protocol (`FastMCP`) server exposing catalog, comparison, review, and web search capabilities as standardized tools.
* **`catalog-api` (Port `8001`):** FastAPI backend managing products, categories, reviews, and `pgvector` semantic similarity search using `Trendyol/TY-ecomm-embed-multilingual-base-v1.2.0`.
* **`frontend` (Port `3000`):** Web storefront with semantic search, product detail pages, and an interactive AI assistant panel.

---

## 🛠️ Setup & Running

### Prerequisites
* Python 3.12+
* PostgreSQL with `pgvector` enabled
* `uv` package manager

### Install Dependencies
```bash
uv sync
```

### Start All Services
Starts `catalog-api` (`:8001`), `assistant-api` (`:8000`), `frontend` (`:3000`), and `langgraph-dev` (`:2024`) with a single command:
```bash
uv run python run.py
```

### Tracing & Studio
* **LangGraph Studio:** Available via the Studio URL printed in the terminal when running `run.py`.
* **LangSmith Tracing:** Configured via `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, and `LANGCHAIN_ENDPOINT` inside `assistant-api/.env`.

---

## 🗺️ Roadmap
* **Visual Search:** Find products, color variations, or similar styles directly from user-uploaded images (e.g., *"Find this skirt in blue"*).
* **Outfit & Style Matching:** Suggest complementary pieces based on an uploaded item or style prompt (e.g., *"Find an old-money shirt to match these trousers"*).
* **Virtual Try-On:** Preview selected garments on a user-provided photo.
* **Hybrid Search:** Combine `pgvector` semantic search with `Full-Text / BM25` and `RRF` ranking.
