from pydantic import BaseModel


class ClientInfo(BaseModel):
    location: str | None = None
    average_rating: float | None = None
    total_spend: str | None = None
    hires: int | None = None
    company_industry: str | None = None
    company_size: str | None = None
    competition_level: str | None = None       # e.g. "50+" proposals already submitted
    previous_jobs_summary: str | None = None   # e.g. "Mostly Webflow/design at $14-20/hr"


class ClientResearch(BaseModel):
    person_name: str | None = None
    company_name: str | None = None
    company_domain: str | None = None
    person_notes: str | None = None    # what web search found about the person
    company_notes: str | None = None   # what web search found about the company


class JobRequest(BaseModel):
    job_text: str
    title: str | None = None
    features: list[str] | None = None
    skills: list[str] | None = None
    proposal_questions: list[str] | None = None
    client_info: ClientInfo | None = None
    client_research: ClientResearch | None = None
    developer_id: str = "artem_koshevoi"


class RevisionRequest(BaseModel):
    thread_id: str
    feedback: str
    prompt_template: str | None = None


class ProposalResult(BaseModel):
    proposal: str
    developer_id: str
    developer_name: str
    verdict: str
    verdict_reason: str
    revision_count: int
    versions: list[str]
    thread_id: str
