# Multi-Agent Proposal Generator

An AI system that reads job postings and autonomously writes, evaluates, and refines freelance proposals — built on a multi-agent pipeline with self-reflection and parallel processing.

---

## What It Does

Given a job posting, the system runs a chain of specialized agents that work in sequence:

1. **Analyzer** — extracts tech stack, budget, project type, and timeline from the raw job text
2. **Qualifier** — decides whether to pursue the job (GO / MAYBE / SKIP) based on fit criteria
3. **RAG Search** — retrieves the most relevant sections of the freelancer's profile using vector similarity
4. **Writer** — drafts a personalized proposal grounded in retrieved profile context
5. **Evaluator** — scores the draft against quality criteria and sends it back for revision if needed
6. **Orchestrator** — runs all of the above in parallel across multiple jobs simultaneously

The writer–evaluator loop is a self-reflection pattern: the system critiques its own output and rewrites until the proposal meets the bar or hits the revision limit.

---

## Architecture Highlights

- **Multi-agent graph** — each agent is a discrete node with a single responsibility; the graph routes between them based on runtime decisions (LangGraph)
- **Self-reflection loop** — the evaluator agent can reject and re-prompt the writer, producing iterative improvements without human input
- **RAG (Retrieval-Augmented Generation)** — freelancer profile is chunked and embedded; relevant experience is pulled per job rather than stuffed into every prompt (ChromaDB)
- **Parallel orchestration** — a top-level orchestrator spawns one worker per job and fans out processing using LangGraph's Send API
- **Persistent conversation memory** — thread-based checkpointing allows human-in-the-loop revisions via API after initial generation
- **REST API** — full FastAPI layer for generating proposals, submitting feedback, and retrieving results

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph |
| LLM | Claude (Anthropic) via LangChain |
| Vector store / RAG | ChromaDB |
| API | FastAPI |
| Data validation | Pydantic |
| Language | Python 3.11+ |

---

## Key Patterns Demonstrated

- Supervisor / worker orchestration with dynamic fan-out
- Conditional graph routing based on LLM output
- Self-critique and iterative refinement loops
- RAG pipeline with semantic chunking and retrieval
- Stateful multi-turn agents with memory checkpointing
- Dependency injection for service composition
