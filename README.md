# AgenticCommerce

AgenticCommerce, geleneksel arama motorlarının ötesine geçen, **LangGraph** destekli ve **Çoklu Ajan (Multi-Agent)** mimarisiyle çalışan yeni nesil bir yapay zeka e-ticaret ekosistemidir. Kullanıcı niyetini dinamik olarak anlar, yönlendirir ve en karmaşık e-ticaret senaryolarını otonom olarak çözer.

## 🏗️ Sistem Mimarisi

Proje, bağımsız ve özelleşmiş mikro servislerden oluşmaktadır.

### 1. `assistant-api` (LangGraph Multi-Agent Sistemi)
Sistemin beynidir. Doğrusal (linear) bir arama yapmak yerine, **Supervisor (Yönetici) Agent** kullanıcı sorgusunu analiz eder ve görevi en uygun uzman düğüme (node) atar:
- **Search Node (Arama):** Arama işlemi aşamalı bir yapay zeka mimarisi kullanır:
  1. Önce kullanıcı sorgusuyla anlamsal (semantic) olarak en çok eşleşen **ürün kategorileri** vektör benzerliği (vector similarity) ile bulunur.
  2. Bulunan bu kategorilerin altındaki potansiyel ürünler veritabanından çekilir.
  3. Son olarak bu aday ürünler **Bi-Encoder** ve **Cross-Encoder** (Reranker) modelleriyle çift aşamalı olarak puanlanır, sıralanır ve sadece kullanıcının niyetine en uygun ürünler seçilir.
- **Compare Node (Karşılaştırma):** Birden fazla ürünün özelliklerini tablo halinde kıyaslar.
- **Review Node (Yorum Analizi):** Müşteri yorumlarını okuyarak ürünün artılarını, eksilerini ve genel memnuniyeti özetler.
- **Clarification Node (Netleştirme):** Kullanıcı çok muğlak bir soru sorduğunda (örn: "Ayakkabı arıyorum"), bütçe veya renk gibi eksik detayları öğrenmek için sorular sorar.
- **Response Builder Node:** Tüm ajanlardan gelen ham verileri toplayıp, kullanıcıya sunulacak son ve şık cevabı (Markdown/HTML) derler.

**Teknoloji Yığını:** Python, LangGraph, LangChain, DeepSeek API & Ollama.

### 2. `catalog-api` (Katalog ve Ürün Servisi)
E-ticaret ürün kataloğunu, kategorileri ve kullanıcı yorumlarını yöneten güçlü arka uç (backend) servisidir. Assistant API içerisindeki ajanların (agents) doğru kararlar alabilmesi için ihtiyaç duydukları veriyi sağlar.

**Teknoloji Yığını:** Python, FastAPI, PostgreSQL (pgvector).

### 3. `frontend` (Kullanıcı Arayüzü)
Kullanıcıların yapay zeka asistanıyla doğrudan sohbet edebildiği, ürünleri inceleyip ajanların arka planda nasıl karar aldığını (reasoning) görebildiği modern web arayüzü.

### 4. `shared` (AI Modelleri)
Sistem genelinde paylaşılan AI varlıklarını içerir. Ürün ve kategori vektörizasyonu için e-ticarete özel olarak eğitilmiş, yüksek isabetli `Trendyol/TY-ecomm-embed-multilingual-base-v1.2.0` modelini kullanır.

## 🚀 Öne Çıkan Özellikler

- **Agentic İş Akışı:** Sadece bir arama motoru değil; arama, karşılaştırma, yorum analizi yapma veya kullanıcıdan detay isteme kararlarını kendi kendine verebilen düşünen bir sistem.
- **Gelişmiş Semantik Arama ve Sıralama (Reranking):** E-ticaret verilerine özel vektör modelleri (Trendyol Embedding) ile tam isabetli anlamsal eşleşme yapılır. Sadece vektör benzerliği değil; Bi-Encoder ile hızlı kategori/ürün eşleşmesi, ardından Cross-Encoder ile son derece hassas ürün yeniden sıralaması (reranking) gerçekleştirilerek kusursuz sonuçlar elde edilir.
- **Dinamik Yorum Analizi:** AI butonu sayesinde binlerce yorum saniyeler içinde okunarak pro/con (artı/eksi) listesine çevrilir.
- **Gerçek Zamanlı Graph İzleme:** LangSmith ve LangGraph Studio ile %100 uyumlu izlenebilir (traceable) ajan iş akışları.

## 🛠️ Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.10+
- PostgreSQL (ve `pgvector` eklentisi)
- `uv` paket yöneticisi (önerilir)

### Servisleri Başlatma
Sistem ortamları proje kök dizininde yapılandırılmıştır.

Örneğin asistan API'yi çalıştırmak için:
```bash
cd assistant-api
uv run main.py
```

### Ajan Grafiğini Görselleştirme
LangGraph mimarindeki ajanların birbiriyle nasıl konuştuğunu ve yönlendirmeleri görmek için şema oluşturabilirsin:
```bash
cd assistant-api
uv run generate_graph.py
```
Bu komut, aktif iş akışının güncel yapısını `graph_visualization.png` olarak bulunduğun klasöre çıkartacaktır.

---
*Geleceğin diyalog odaklı (conversational) e-ticaret deneyimi için inşa edildi.*
