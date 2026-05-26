from dependency_injector.wiring import inject
from fastapi import APIRouter

from agents.containers import ProposalServiceDep
from agents.schemas import JobRequest, ProposalResult, RevisionRequest

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


@router.post("/revise-proposal", response_model=ProposalResult)
@inject
async def revise_proposal(
    payload: RevisionRequest,
    proposal_service: ProposalServiceDep,
) -> ProposalResult:
    return await proposal_service.revise_proposal(payload)
