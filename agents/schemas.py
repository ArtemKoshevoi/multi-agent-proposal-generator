from pydantic import BaseModel


class JobRequest(BaseModel):
    job_text: str
    client_data: dict | None = None
    metadata: dict | None = None


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
