# AgenticCommerce

AgenticCommerce, **LangGraph**, **FastMCP** ve **pgvector** tabanlı; ürün keşfi, teknik detay inceleme, ürün karşılaştırma ve müşteri yorumu analizi yapabilen çoklu-ajan (Multi-Agent) e-ticaret asistanı platformudur.

---

## 🏗️ Sistem Mimarisi

Proje birbirinden bağımsız 4 ana bileşenden oluşur:

### 1. `assistant-api` (LangGraph İş Akışı — Port: `8000`)
Kullanıcıyla sohbet eden, araçları yöneten ve çok turlu oturum hafızasını (`MemorySaver`) tutan orkestrasyon katmanıdır.

```text
[START] ──► supervisor_node (ReAct Ajanı & Yanıt Üretici)
                ├── delegate_to_search ──► search_node (MCP: get_closest_products) ──► supervisor_node
                ├── detay/kıyas/yorum  ──► tool_node   (MCP: details, compare, reviews) ──► supervisor_node
                └── doğrudan yanıt     ──► [END]
```

* **`supervisor_node` (`SupervisorAgent`):** Kullanıcının niyetini anlar, gereksiz soru sormadan arama yaptırır veya sohbet eder; araçlardan dönen sonuçları kullanıcıya Markdown formatında sunar.
* **`search_node` (`SearchNode`):** `delegate_to_search` çağrısını yakalar, `mcp-server` üzerinden katalog araması yapar ve `found_products` state'ini günceller.
* **`tool_node` (`ToolNode`):** MCP üzerinden ürün detayı, karşılaştırma ve yorum araçlarını çalıştırır.

**Teknoloji Yığını:** Python, FastAPI, LangGraph, LangChain, DeepSeek / OpenAI / Ollama.

---

### 2. `mcp-server` (Tekil MCP Tool Sunucusu)
Ajanların `catalog-api` ile iletişim kurduğu standart **Model Context Protocol (FastMCP)** katmanıdır (`stdio` / `streamable_http`):
* `get_closest_products`: Vektör benzerliği ile katalogdan ürün arama
* `get_product_details`: Tekil ürünün teknik özelliklerini ve fiyatını getirme
* `compare_products`: Birden fazla ürünü kıyaslama için toplu detay çekme
* `get_product_reviews`: Ürün müşteri yorumlarını getirme

---

### 3. `catalog-api` (Katalog ve Vektör Servisi — Port: `8001`)
Ürün, kategori ve yorum verilerini PostgreSQL + `pgvector` üzerinden sunan N-Tier FastAPI servisidir.
* **Embedding Modeli:** `Trendyol/TY-ecomm-embed-multilingual-base-v1.2.0` (`shared/ai-models/embeddings`)
* **Veritabanı:** PostgreSQL + `pgvector`

---

### 4. `frontend` (Web Arayüzü — Port: `3000`)
Ürün listeleme, vektör tabanlı arama çubuğu, ürün detay sayfası ve AI asistan sohbet panelini içeren web arayüzü.

---

## 🛠️ Kurulum ve Çalıştırma

### Gereksinimler
* Python 3.12+
* PostgreSQL (`pgvector` eklentisi aktif)
* `uv` paket yöneticisi

### Bağımlılıkları Yükleme
```bash
uv sync
```

### Tüm Servisleri Başlatma
`catalog-api` (`:8001`), `assistant-api` (`:8000`) ve `frontend` (`:3000`) servislerini tek komutla ayağa kaldırır:
```bash
uv run python run.py
```

### LangGraph Studio ile Görsel Test & Debug
`catalog-api` çalışırken ajan akışını, düğüm geçişlerini ve state değişimlerini canlı izlemek için:
```bash
uv run langgraph dev --no-reload
```
*(İzleme/Tracing için `assistant-api/.env` içindeki `LANGCHAIN_TRACING_V2` ve `LANGCHAIN_API_KEY` değişkenleri kullanılır.)*

---

## 🗺️ Planlanan Geliştirmeler (Yol Haritası)
* `SearchNode` içerisine LLM tabanlı sorgu ayrıştırma ve **Tavily** (`web_search`) ile teknik uyumluluk araştırması eklenmesi
* `catalog-api` üzerinde **Hibrit Arama (`pgvector + Full-Text/BM25 RRF + Cross-Encoder`)** motoruna geçiş
* Görsel arama (**Vision Search**) ve sanal kıyafet deneme (**Virtual Try-On**) entegrasyonu
