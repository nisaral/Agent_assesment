# Finance Assistant

A scalable finance assistant for portfolio risk analysis, supporting voice/text queries and visualizations

## Architecture

Architecture Diagram-coming soon

- **Agents**: FastAPI microservices (`api_agent`, `scraping_agent`, `retriever_agent`, `analysis_agent`, `language_agent`, `voice_agent`, `orchestrator`).
- **MCP**: `scraping_agent` uses MCP for news scraping (NewsAPI, stdio via `uvx`).
- **Frontend**: HTML/CSS/JS, React-like interaction, WebRTC voice input.
- **Orchestration**: LangGraph workflow, fallback for low-confidence retrieval.
- **Storage**: FAISS for portfolio RAG.

### Framework Comparison
- **FastAPI vs Flask**: FastAPI chosen for async support and scalability.
- **NewsAPI vs Web Scraping**: NewsAPI simpler than custom scraping for news.
- **FAISS vs Pinecone**: FAISS for local/low-cost vector storage.
- **Vercel vs Heroku**: Vercel for frontend, Heroku for backend APIs.

## Setup

1. **Install Prerequisites**:
   ```bash
   python --version  # >=3.10
   node -v  # >=18
   uvx --version
   docker --version
