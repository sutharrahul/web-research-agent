# 🔎 Web Search Agent

A terminal-based AI web search agent with intelligent caching using LangGraph, Ollama, DuckDuckGo Search, and Redis. The agent searches the web on your behalf, summarizes results using a local LLM, and caches answers in Redis — so repeated queries are answered instantly without re-fetching.

## Features

- Real-time web search powered by DuckDuckGo (via `ddgs`)
- AI-powered summarization using a local LLM — no API costs
- Redis caching — repeated queries are served instantly (TTL: 5 minutes)
- LangGraph state machine — clean, modular agent pipeline
- Conditional graph edges — skips search if cached result exists

## Tech Stack

| Tool | Purpose |
|---|---|
| LangGraph | Agent state graph + conditional routing |
| Ollama (`gemma3:4b`) | Local LLM inference for summarization |
| DuckDuckGo (`ddgs`) | Web search (top 5 results) |
| Redis | In-memory caching of search summaries |
| `langchain-ollama` | LangChain-compatible Ollama wrapper |

## Project Structure

```
web_search_agent/
├── requirementpackage.txt   # Python dependencies
├── main.py                  # Entry point — agent graph + search loop
└── README.md
```

## Setup

### 1. Clone and create virtual environment

```bash
git clone <your-repo-url>
cd web_search_agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirementpackage.txt
```

### 3. Start Redis

Make sure Redis is running locally on the default port:

```bash
redis-server
```

> Redis is used to cache search summaries for 5 minutes (TTL = 300s). Install Redis via `brew install redis` (macOS) or your system's package manager.

### 4. Pull the Ollama model

```bash
ollama pull gemma3:4b
```

### 5. Run the agent

```bash
python main.py
```

You will be prompted to enter a search query:

```
🔎 Search with Ai > what is quantum computing
```

## How It Works

```
User enters search query
        ↓
Check Redis cache for existing result
        ↓ (cache hit)              ↓ (cache miss)
Return cached summary         Search DuckDuckGo (top 5 results)
                                    ↓
                              Summarize results with local LLM
                                    ↓
                              Save summary to Redis (TTL: 5 min)
                                    ↓
                              Print summary to terminal
```

## Agent Graph (LangGraph)

The agent is built as a `StateGraph` with the following nodes:

| Node | Description |
|---|---|
| `check_cache` | Looks up the query in Redis |
| `search` | Fetches top 5 DuckDuckGo results |
| `summarize` | Sends results to LLM for summarization |
| `save_cache` | Stores the summary in Redis |

Conditional routing after `check_cache`: if a cached result exists, the graph jumps directly to `END`; otherwise it proceeds to `search`.

## Requirements

Key packages used by this project:

```
ddgs
redis
langchain-ollama
langgraph
langchain-core
```

## Notes

- Redis cache TTL is set to **300 seconds (5 minutes)** — adjust `ex=300` in `save_cache` as needed
- The LLM model is `gemma3:4b` — swap it out in the `summarize` node for any other Ollama-supported model
- Search results are limited to **5 items** via `max_results=5` in the `search` node
