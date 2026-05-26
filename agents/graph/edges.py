from typing import Literal
from langgraph.graph import END
from agents.graph.state import ProposalState


def route_after_qualify(state: ProposalState) -> Literal["search_rag", "reject_job"]:
    """After qualification: proceed or reject."""
    if state["verdict"] == "SKIP":
        return "reject_job"
    return "search_rag"


def route_after_evaluate(state: ProposalState) -> str:
    """After evaluation: revise or finish.
    Max 3 revisions to avoid infinite loop.
    """
    if state["status"] == "approved":
        return END

    if state["revision_count"] >= 3:
        print("   Max revisions reached - accepting as is")
        return END

    return "write_proposal"