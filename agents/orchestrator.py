from typing import Annotated
import operator
import os
import glob
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from agents.graph.workflow import build_graph, create_initial_state
from dotenv import load_dotenv


load_dotenv()


# ── Orchestrator State ───────────────────────────────────
class OrchestratorState(dict):
    job_files: list[str]                              # input: list of job file paths
    results: Annotated[list, operator.add]            # workers write here in parallel


# ── Worker State ─────────────────────────────────────────
class WorkerState(dict):
    job_file: str                                     # single job file path
    results: Annotated[list, operator.add]            # shared output key


# ── Nodes ────────────────────────────────────────────────
def orchestrator_node(state: OrchestratorState) -> dict:
    """Receives list of job files. Passes to assign_workers."""
    print(f">> Orchestrator: received {len(state['job_files'])} jobs")
    return {}


def process_job_worker(state: WorkerState) -> dict:
    """Worker: runs full proposal graph for a single job file."""
    job_file = state["job_file"]
    print(f"\n>> Worker: processing {job_file}")

    with open(job_file, "r", encoding="utf-8") as f:
        job_text = f.read()

    # run the full proposal graph
    graph = build_graph()
    config = {"configurable": {"thread_id": f"job-{job_file}"}}

    initial_state = create_initial_state(job_text)

    result = graph.invoke(initial_state, config=config)

    return {
        "results": [{
            "file": job_file,
            "status": result["status"],
            "verdict": result["verdict"],
            "verdict_reason": result["verdict_reason"],
            "proposal": result.get("proposal", "")
        }]
    }


def synthesizer_node(state: OrchestratorState) -> dict:
    """Collects all worker results and prints summary."""
    print("\n" + "="*60)
    print("BATCH RESULTS SUMMARY")
    print("="*60)

    approved = [r for r in state["results"] if r["status"] == "approved"]
    skipped = [r for r in state["results"] if r["status"] == "skipped"]

    print(f"\nTotal: {len(state['results'])} jobs")
    print(f"Approved: {len(approved)}")
    print(f"Skipped: {len(skipped)}")

    if approved:
        print("\n--- APPROVED PROPOSALS ---")
        for r in approved:
            print(f"\nFile: {r['file']}")
            print(f"Verdict: {r['verdict']} — {r['verdict_reason']}")
            print(f"\n{r['proposal']}")
            print("-"*40)

    if skipped:
        print("\n--- SKIPPED JOBS ---")
        for r in skipped:
            print(f"File: {r['file']}")
            print(f"Reason: {r['verdict_reason']}")

    return {}


# ── Send API: dynamic worker creation ────────────────────
def assign_workers(state: OrchestratorState):
    """Creates one worker per job file."""
    print(f">> Assigning {len(state['job_files'])} workers")
    return [Send("process_job", {"job_file": f}) for f in state["job_files"]]


# ── Build orchestrator graph ─────────────────────────────
def build_orchestrator():
    builder = StateGraph(OrchestratorState)

    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("process_job", process_job_worker)
    builder.add_node("synthesizer", synthesizer_node)

    builder.add_edge(START, "orchestrator")
    builder.add_conditional_edges(
        "orchestrator",
        assign_workers,
        ["process_job"]
    )
    builder.add_edge("process_job", "synthesizer")
    builder.add_edge("synthesizer", END)

    return builder.compile()


# ── Run ──────────────────────────────────────────────────
if __name__ == "__main__":
    # find all job files
    job_files = sorted(glob.glob("mock_data/jobs/*.txt"))
    print(f"Found {len(job_files)} job files: {job_files}")

    orchestrator = build_orchestrator()
    orchestrator.invoke({
        "job_files": job_files,
        "results": []
    })