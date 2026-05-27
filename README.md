# Multi-Agent Proposal Generator

An AI system that reads Upwork job postings and autonomously writes, evaluates, and refines freelance proposals — with human-in-the-loop review via a Telegram bot.

---

## What It Does

1. Receives a parsed job posting (description, skills, budget, client data)
2. Qualifies the job — GO / MAYBE / SKIP based on stack and budget fit
3. Selects a developer from the team by ID and retrieves their relevant profile sections
4. Writes a personalized proposal grounded in that developer's real projects
5. Self-evaluates and rewrites until the proposal meets the quality bar
6. Pauses for manager review via Telegram — revise with feedback or approve to finish

---

## Architecture

```
POST /process-job
        ↓
┌─────────────────────────────┐
│  generate_proposal subgraph │
│  analyze → qualify → RAG    │
│  → write → evaluate (loop)  │
└─────────────────────────────┘
        ↓
  manager_review  ← interrupt() — pauses here, returns proposal + thread_id
        ↓
POST /revise-proposal  { thread_id, feedback }
        ↓
  write_proposal → manager_review  ← loops until "approve"
        ↓
       END
```

**Subgraph pattern** — the full proposal pipeline is a compiled `StateGraph` used as a single node in the parent graph. Reusable and independently testable.

**Human-in-the-loop** — `interrupt()` pauses the graph after generation. The HTTP request returns immediately with the proposal and a `thread_id`. A second request with `Command(resume=feedback)` resumes from exactly where it stopped.

**Multi-developer RAG** — 10 developer profiles loaded into ChromaDB, each chunk tagged with `developer_id` metadata. Each request targets one developer's namespace. Same job, different developer → different proposal voice, projects, and honest gap flags.

**Two type systems** — Pydantic models at API boundaries (runtime validation, serialization), TypedDict internally for graph state (static hints, zero overhead).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph (StateGraph, subgraphs, interrupt/resume) |
| LLM — analysis / evaluation | Claude Haiku |
| LLM — proposal writing | Claude Sonnet |
| Vector store / RAG | ChromaDB + sentence-transformers |
| API | FastAPI + dependency injection |
| Type validation | Pydantic v2 (API) / TypedDict (graph state) |
| Persistence | SQLite via AsyncSqliteSaver (thread checkpoints survive restarts) |
| Messaging | Telegram Bot (polling, human-in-the-loop interface) |
| Language | Python 3.11+ |
| Containerization | Docker + Docker Compose |

---

## Key Patterns

- **Subgraph** — nested `StateGraph` compiled and used as a node in a parent graph
- **interrupt / Command(resume)** — stateful pause across HTTP requests, manager reviews proposals in Telegram
- **RAG with metadata filtering** — per-developer namespaces in a single ChromaDB collection
- **Reducer state** (`Annotated[list[str], operator.add]`) — proposal versions accumulate across the revision loop
- **Self-reflection loop** — evaluator rejects and re-prompts the writer up to N times before surfacing to the manager
- **Conditional routing** — graph branches on LLM output (qualify verdict, evaluation grade, manager decision)
- **Dependency injection** — graph built once at startup via FastAPI lifespan, injected per request

---

## API

```
GET  /health
POST /process-job      — JobRequest → ProposalResult (pauses at manager review)
POST /revise-proposal  — RevisionRequest → ProposalResult (resumes from thread_id)
```

Swagger UI available at `http://localhost:8000/docs`.

---

## Running Locally

```bash
make install   # create venv and install dependencies
make setup     # load developer profiles into ChromaDB
make dev       # start FastAPI server
make bot       # start Telegram bot (requires TELEGRAM_TOKEN in .env)
make test      # send a test job (JOB=1|2, DEVELOPER=artem_koshevoi|dmytro_mamaiev|...)
```

Copy `.env.example` to `.env` and fill in `ANTHROPIC_API_KEY` and `TELEGRAM_TOKEN`.

---

## Running with Docker

```bash
make install   # one-time: create venv
make setup     # one-time: load developer profiles into ChromaDB (writes ./chroma_db)
make docker-build  # build the image
make docker-up     # start in background
make docker-logs   # tail logs
make docker-down   # stop
```

The `chroma_db/` directory (created by `make setup`) is mounted read-only into the container. The SQLite checkpoint database is stored in `data/checkpoints.db` (mounted as a volume, persists across restarts).

`make bot` still runs locally — the Telegram bot talks to the API over `localhost:8000`.
