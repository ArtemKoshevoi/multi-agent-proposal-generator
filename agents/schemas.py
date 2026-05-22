from pydantic import BaseModel


class ClientInfo(BaseModel):
    location: str | None = None
    average_rating: float | None = None
    total_spend: str | None = None
    hires: int | None = None
    company_industry: str | None = None
    company_size: str | None = None


class ClientResearch(BaseModel):
    person_name: str | None = None
    company_name: str | None = None
    company_domain: str | None = None
    search_notes: str | None = None


class JobRequest(BaseModel):
    job_text: str
    title: str | None = None
    features: list[str] | None = None
    skills: list[str] | None = None
    proposal_questions: list[str] | None = None
    client_info: ClientInfo | None = None
    client_research: ClientResearch | None = None


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
