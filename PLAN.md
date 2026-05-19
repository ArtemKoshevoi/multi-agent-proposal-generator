# Upwork Proposal Agent — Build Plan

> **For Claude Code and developers:** Read this entire document before making
> any changes. Follow the architecture and patterns described here. Do not
> deviate without updating this document first.

---

## Goal

Build a multi-agent system that:
1. Receives a parsed Upwork job offer + optional client research data
2. Selects the best matching developer from a pool of ~10
3. Generates a high-quality proposal for the selected developer
4. Supports manager review, revision requests, and additional prompt templates
5. Returns the final approved proposal

Built incrementally — each milestone is independently testable.

---

## Current State

### Completed milestones
- [x] Milestone 1 — RAG + ChromaDB with Artem's profile (single developer)
- [x] Milestone 2 — Linear pipeline (no LangGraph, for learning only)
- [x] Milestone 3 — LangGraph workflow: analyze → qualify → RAG → write → evaluate
- [x] Milestone 4 — Orchestrator-Worker for parallel batch processing

### What exists in codebase
```
agents/
├── __init__.py
├── run.py                    ← CLI: single job entry point
├── orchestrator.py           ← CLI: batch processing entry point
├── graph/
│   ├── __init__.py
│   ├── state.py              ← ProposalState TypedDict
│   ├── nodes.py              ← analyze, qualify, search_rag, write, evaluate, reject
│   ├── edges.py              ← route_after_qualify, route_after_evaluate
│   └── workflow.py           ← build_graph(), create_initial_state()
├── rag/
│   ├── __init__.py
│   ├── setup.py              ← loads developer profile into ChromaDB
│   └── search.py             ← semantic search over profile
└── prompts/
    └── system_prompt_manual.txt  ← proposal writing rules (not yet used in graph)

mock_data/
├── jobs/                     ← 7 test job descriptions (.txt)
└── artem_koshevoi.txt        ← single developer profile (RAG source)
```

### Known issues to fix before or during Milestone 5
- `system_prompt_manual.txt` not yet used — simplified prompt hardcoded in nodes.py
- Single developer only — multi-developer support comes in Milestone 6
- `initial_state` duplicated in run.py and orchestrator.py — use create_initial_state()
- No API layer yet — runs only from CLI

---

## Full System Architecture (target)

```
External tools (built separately, not part of this repo):
  Job Parser        → structured job data from Upwork page
  Client Researcher → client profile, spend history, hire rate
        ↓
INPUT: JobRequest {
  job_text: str,          required
  client_data: dict,      optional — from client researcher
  metadata: dict          optional — pre-parsed budget, skills, duration
}
        ↓
┌─────────────────────────────────────────┐
│  DEVELOPER SELECTOR (Milestone 6)       │
│  - Search all ~10 developer profiles    │
│  - Score each against job requirements  │
│  - Weight: stack match, level, domain   │
│  - Return top 1-3 ranked developers     │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│  PROPOSAL WORKFLOW (Milestone 3, done)  │
│  analyze → qualify → RAG → write → eval │
│  Runs for selected developer            │
└─────────────────────────────────────────┘
        ↓
OUTPUT: ProposalResult {
  proposal: str,
  developer_id: str,
  developer_name: str,
  verdict: str,
  revision_count: int,
  versions: list[str]    ← all previous versions stored
  thread_id: str         ← for resuming revisions
}
        ↓
┌─────────────────────────────────────────┐
│  MANAGER REVIEW (Milestone 7)           │
│  Via API → Slack / Telegram / Discord   │
│  Options:                               │
│  - Approve and send                     │
│  - Request revision with text feedback  │
│  - Apply prompt template:               │
│      client_perspective — rewrite from  │
│        client POV                       │
│      more_technical — add depth         │
│      shorter — compress to 5 sentences  │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│  REVISION LOOP (on manager request)     │
│  - Store current proposal in versions[] │
│  - Apply feedback + optional template   │
│  - Re-run writer + evaluator            │
│  - Return new version                   │
└─────────────────────────────────────────┘
```

---

## Data Schemas

### API input
```python
class JobRequest(BaseModel):
    job_text: str                       # raw job description (required)
    client_data: dict | None = None     # from client researcher (optional)
    metadata: dict | None = None        # pre-parsed fields (optional)

class RevisionRequest(BaseModel):
    thread_id: str                      # identifies session to resume
    feedback: str                       # manager revision instructions
    prompt_template: str | None = None  # e.g. "client_perspective"
```

### API output
```python
class ProposalResult(BaseModel):
    proposal: str
    developer_id: str
    developer_name: str
    verdict: str                        # GO / MAYBE / SKIP
    verdict_reason: str
    revision_count: int
    versions: list[str]                 # all versions including current
    thread_id: str                      # for resuming revisions
```

### Developer profile namespace in ChromaDB
```
collection: "developer_profile"
namespace per developer: (developer_id, "profile")
examples: ("artem", "profile"), ("dmytro", "profile")
```

---

## Milestones

### ✅ Milestone 1 — RAG + Knowledge Base
Single developer (Artem) profile loaded into ChromaDB. Semantic search verified.

### ✅ Milestone 2 — Linear Pipeline (learning only)
Sequential Python functions without LangGraph. File agents/pipeline.py deleted.

### ✅ Milestone 3 — LangGraph Workflow
StateGraph: analyze_job → qualify_job → search_rag → write_proposal →
evaluate_proposal. Conditional edges, evaluator-optimizer loop (max 2 revisions),
MemorySaver, thread_id per job.

### ✅ Milestone 4 — Orchestrator-Worker
Parallel batch processing via Send API and Annotated state + operator.add.

---

### Milestone 5 — FastAPI Layer
**Goal:** Expose pipeline as HTTP API with proper initialization and DI.
**Status:** NEXT

**Key patterns (from team lead review):**
- Graph and ChromaDB initialized ONCE at startup via FastAPI lifespan
- Never rebuild graph per request
- Dependency injection via FastAPI Depends
- Each request gets unique thread_id = str(uuid4())
- LangGraph invoke() is sync — wrap in run_in_executor or use ainvoke()

**New files:**
- `agents/main.py` — FastAPI app with lifespan and endpoints
- `agents/schemas.py` — Pydantic request/response models

**Endpoints:**
```
GET  /health           → {"status": "ok"}
POST /process-job      → JobRequest → ProposalResult
POST /process-batch    → list[str] (job texts) → list[ProposalResult]
POST /revise-proposal  → RevisionRequest → ProposalResult
```

**Exit criteria:**
- All endpoints respond correctly via curl and /docs
- Graph initialized once (verify with startup log message)
- Two concurrent requests handled without conflict
- /revise-proposal returns updated proposal with previous version stored

---

### Milestone 6 — Multi-Developer Support
**Goal:** System selects best developer from pool of ~10 for each job.

**Steps:**
1. Add profiles to `mock_data/developers/` (one .txt per developer)
2. Update rag/setup.py to load all profiles with namespace per developer
3. Build `agents/selector/developer_selector.py`:
   - Query ChromaDB for each developer against job
   - Score: stack match 40%, experience level 30%, domain relevance 30%
   - Return top 1-3 ranked with scores
4. Add developer_id and developer_score to ProposalState
5. Update search_rag node to use selected developer namespace
6. Return candidates list in ProposalResult

**Exit criteria:** React/TypeScript job selects React-focused developer
over Python-only developer from the pool.

---

### Milestone 7 — Manager Revision Flow
**Goal:** Manager requests revisions with feedback and optional prompt templates.

**Steps:**
1. Add `versions: list[str]` to ProposalState
2. Implement POST /revise-proposal — resumes via thread_id + Command
3. Add prompt template files to agents/prompts/:
   - client_perspective.txt
   - more_technical.txt
   - shorter.txt
4. Writer node loads template if provided
5. Return new proposal + all previous versions

**LangGraph pattern:** interrupt() + Command(resume=feedback)

**Exit criteria:** Proposal revised 3 times, each version stored and
retrievable via thread_id.

---

### Milestone 8 — Docker (local)
**Goal:** Full system runs in Docker.

**Services:**
- `api` — FastAPI on port 8000
- `chroma` — ChromaDB with persistent volume

**Steps:**
1. agents/Dockerfile
2. docker-compose.yml
3. Init container: load all developer profiles on first start
4. .env for secrets, .env.example for template

**Exit criteria:** docker compose up → curl /process-job → proposal returned.
ChromaDB persists between restarts.

---

### Milestone 9 — Messaging Integration
**Goal:** Manager interacts via Slack / Telegram / Discord.

FastAPI stays as core. Messaging bot is a thin layer:
1. Receives job text from manager
2. Calls POST /process-job
3. Posts proposal back
4. Handles approve / revise via interrupt()

Platform TBD. Telegram simplest for initial testing.
Switch to SqliteSaver for persistence across restarts.

**Exit criteria:** Paste job in chat → proposal → manager requests revision →
revised proposal returned.

---

### Milestone 10 — Production Deployment
**Goal:** System accessible remotely.

1. Hetzner CX22 (~€4/mo, Ubuntu 24.04)
2. GitHub Actions CI/CD
3. Switch to PostgresSaver
4. nginx + SSL (Let's Encrypt)

**Exit criteria:** Messaging bot → remote server → proposal, no local deps.

---

## File Structure (target)

```
upwork-proposal-agent/
├── PLAN.md
├── docker-compose.yml
├── .env
├── .env.example
├── requirements.txt
│
├── mock_data/
│   ├── jobs/                        ← test job descriptions
│   └── developers/                  ← one .txt per developer
│       ├── artem_koshevoi.txt
│       └── ...
│
└── agents/
    ├── __init__.py
    ├── Dockerfile
    ├── main.py                      ← FastAPI app
    ├── schemas.py                   ← Pydantic models
    ├── run.py                       ← CLI single job
    ├── orchestrator.py              ← CLI batch
    │
    ├── graph/
    │   ├── __init__.py
    │   ├── state.py
    │   ├── nodes.py
    │   ├── edges.py
    │   └── workflow.py
    │
    ├── rag/
    │   ├── __init__.py
    │   ├── setup.py
    │   └── search.py
    │
    ├── selector/
    │   ├── __init__.py
    │   └── developer_selector.py   ← Milestone 6
    │
    └── prompts/
        ├── system_prompt_manual.txt
        ├── client_perspective.txt   ← Milestone 7
        ├── more_technical.txt
        └── shorter.txt
```

---

## Tech Stack

| Layer | Tech | Notes |
|-------|------|-------|
| LLM | Claude Haiku `claude-haiku-4-5-20251001` | cheap, fast |
| Orchestration | LangGraph StateGraph | core framework |
| RAG | ChromaDB + all-MiniLM-L6-v2 | local, no external API |
| API | FastAPI + uvicorn | async, /docs auto-generated |
| Validation | Pydantic v2 | request/response schemas |
| Persistence | MemorySaver → SqliteSaver → PostgresSaver | upgrade per milestone |
| Messaging | Slack / Telegram / Discord (TBD) | thin wrapper over API |
| Infra | Docker + docker-compose | local and prod |
| CI/CD | GitHub Actions | SSH deploy |
| Server | Hetzner CX22 ~€4/mo | Ubuntu 24.04 |

---

## Key Technical Decisions

**Graph initialization:** Build once at startup via lifespan. Never per request.
Inject via FastAPI Depends.

**Thread IDs:** Each request gets `str(uuid4())`. Return in response for
revision resumption. Never reuse between unrelated requests.

**Sync vs async:** LangGraph invoke() is sync. In async endpoints use
`run_in_executor` or `graph.ainvoke()`.

**Developer profiles:** One ChromaDB namespace per developer.
New developer = add .txt + run setup script.

**Proposal versions:** Append to `versions: list[str]` before each overwrite.
Never delete previous versions.

**Prompt templates:** Load from agents/prompts/ at startup into dict.
Template name in request → load text. Unknown template → 400 error.

---

## Open Questions

1. Which messaging platform first — Slack, Telegram, or Discord?
2. How many developers in initial pool — start with 3 or all 10?
3. Exact format of client_data from external researcher (define schema first).
4. Batch processing — return all results or only GO/MAYBE ones?
5. Revision history storage — MemorySaver or SqliteSaver from Milestone 7?
6. Developer selector — return 1 or top 3? If 3 — run proposals in parallel?
