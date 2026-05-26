from typing import Literal
from langgraph.graph import END
from agents.graph.state import ProposalState


def route_after_qualify(state: ProposalState) -> Literal["search_rag", "reject_job"]:
    if state["verdict"] == "SKIP":
        return "reject_job"
    return "search_rag"


def route_after_evaluate(state: ProposalState) -> str:
    if state["status"] == "approved":
        return END
    if state["revision_count"] >= 3:
        print("   Max revisions reached - accepting as is")
        return END
    return "write_proposal"


def route_after_generate(state: ProposalState) -> str:
    """Skip manager review entirely for rejected jobs."""
    if state["verdict"] == "SKIP":
        return END
    return "manager_review"


def route_after_manager_review(state: ProposalState) -> str:
    if state["status"] == "approved":
        return END
    return "write_proposal"