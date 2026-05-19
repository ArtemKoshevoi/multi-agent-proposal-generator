from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from agents.graph.state import ProposalState
from agents.graph.nodes import (
    analyze_job,
    qualify_job,
    search_rag,
    write_proposal,
    evaluate_proposal,
    reject_job
)
from agents.graph.edges import route_after_qualify, route_after_evaluate

def create_initial_state(job_text: str) -> dict:
    return {
        "job_text": job_text,
        "analysis": "",
        "verdict": "",
        "verdict_reason": "",
        "rag_context": "",
        "proposal": "",
        "proposal_feedback": "",
        "revision_count": 0,
        "status": "active"
    }


def build_graph():
    """Builds and compiles the proposal generation graph."""

    builder = StateGraph(ProposalState)

    # register all nodes
    builder.add_node("analyze_job", analyze_job)
    builder.add_node("qualify_job", qualify_job)
    builder.add_node("search_rag", search_rag)
    builder.add_node("write_proposal", write_proposal)
    builder.add_node("evaluate_proposal", evaluate_proposal)
    builder.add_node("reject_job", reject_job)

    # define flow
    builder.add_edge(START, "analyze_job")
    builder.add_edge("analyze_job", "qualify_job")

    # after qualify: GO/MAYBE → search_rag, SKIP → reject_job
    builder.add_conditional_edges("qualify_job", route_after_qualify)

    builder.add_edge("search_rag", "write_proposal")
    builder.add_edge("write_proposal", "evaluate_proposal")

    # after evaluate: APPROVED → END, NEEDS_IMPROVEMENT → write_proposal
    builder.add_conditional_edges("evaluate_proposal", route_after_evaluate)

    builder.add_edge("reject_job", END)

    # compile with memory checkpointer
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    return graph