from dependency_injector.wiring import inject
from fastapi import APIRouter

from agents.containers import ProposalServiceDep
from agents.schemas import JobRequest, ProposalResult

router = APIRouter(tags=["proposals"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/process-job", response_model=ProposalResult)
@inject
async def process_job(
    payload: JobRequest,
    proposal_service: ProposalServiceDep,
) -> ProposalResult:
    return await proposal_service.process_job(payload)
