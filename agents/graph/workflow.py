from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from agents.graph.state import ProposalState
from agents.graph.subgraphs.proposal import build_proposal_subgraph
from agents.graph.nodes import manager_review, write_proposal
from agents.graph.edges import route_after_generate, route_after_manager_review
from agents.schemas import JobRequest


def create_initial_state(payload: JobRequest) -> dict:
    client_info = payload.client_info
    client_research = payload.client_research

    return {
        # raw job input
        "job_text": payload.job_text,
        "title": payload.title,
        "features": payload.features,
        "skills": payload.skills,
        "proposal_questions": payload.proposal_questions,

        # client context
        "client_location": client_info.location if client_info else None,
        "client_rating": client_info.average_rating if client_info else None,
        "client_total_spend": client_info.total_spend if client_info else None,
        "client_hires": client_info.hires if client_info else None,
        "client_competition_level": client_info.competition_level if client_info else None,
        "client_previous_jobs_summary": client_info.previous_jobs_summary if client_info else None,
        "client_name": client_research.person_name if client_research else None,
        "client_company": client_research.company_name if client_research else None,
        "client_company_domain": client_research.company_domain if client_research else None,
        "client_person_notes": client_research.person_notes if client_research else None,
        "client_company_notes": client_research.company_notes if client_research else None,

        # analysis / rag / proposal (empty at start)
        "analysis": "",
        "verdict": "",
        "verdict_reason": "",
        "rag_context": "",
        "proposal": "",
        "proposal_feedback": "",
        "revision_count": 0,
        "versions": [],
        "status": "active",
    }


def build_graph():
    proposal_subgraph = build_proposal_subgraph().compile()

    builder = StateGraph(ProposalState)

    builder.add_node("generate_proposal", proposal_subgraph)
    builder.add_node("manager_review", manager_review)
    builder.add_node("write_proposal", write_proposal)

    builder.add_edge(START, "generate_proposal")
    builder.add_conditional_edges("generate_proposal", route_after_generate)
    builder.add_conditional_edges("manager_review", route_after_manager_review)
    builder.add_edge("write_proposal", "manager_review")

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)
