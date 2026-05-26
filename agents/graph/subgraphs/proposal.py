from langgraph.graph import StateGraph, START, END

from agents.graph.state import ProposalState
from agents.graph.nodes import (
    analyze_job,
    qualify_job,
    search_rag,
    write_proposal,
    evaluate_proposal,
    reject_job,
)
from agents.graph.edges import route_after_qualify, route_after_evaluate


def build_proposal_subgraph() -> StateGraph:
    builder = StateGraph[ProposalState, None, ProposalState, ProposalState](ProposalState)

    builder.add_node("analyze_job", analyze_job)
    builder.add_node("qualify_job", qualify_job)
    builder.add_node("search_rag", search_rag)
    builder.add_node("write_proposal", write_proposal)
    builder.add_node("evaluate_proposal", evaluate_proposal)
    builder.add_node("reject_job", reject_job)

    builder.add_edge(START, "analyze_job")
    builder.add_edge("analyze_job", "qualify_job")
    builder.add_conditional_edges("qualify_job", route_after_qualify)
    builder.add_edge("search_rag", "write_proposal")
    builder.add_edge("write_proposal", "evaluate_proposal")
    builder.add_conditional_edges("evaluate_proposal", route_after_evaluate)
    builder.add_edge("reject_job", END)

    return builder
