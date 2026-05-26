import operator
from typing import Annotated, TypedDict


class ProposalState(TypedDict):
    # --- raw job input ---
    job_text: str
    title: str | None
    features: list[str] | None
    skills: list[str] | None
    proposal_questions: list[str] | None

    # --- client context ---
    client_location: str | None
    client_rating: float | None
    client_total_spend: str | None
    client_hires: int | None
    client_competition_level: str | None
    client_previous_jobs_summary: str | None
    client_name: str | None
    client_company: str | None
    client_company_domain: str | None
    client_person_notes: str | None
    client_company_notes: str | None

    # --- developer ---
    developer_id: str
    developer_name: str

    # --- analysis results ---
    analysis: str
    verdict: str               # GO / MAYBE / SKIP
    verdict_reason: str

    # --- rag results ---
    rag_context: str

    # --- proposal ---
    proposal: str
    proposal_feedback: str
    revision_count: int
    versions: Annotated[list[str], operator.add]

    # --- flow control ---
    status: str                # active / skipped / approved