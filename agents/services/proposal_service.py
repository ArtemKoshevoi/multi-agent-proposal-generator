import logging
from uuid import uuid4

from langgraph.types import Command

from agents.graph.workflow import create_initial_state
from agents.schemas import JobRequest, ProposalResult, RevisionRequest


class ProposalService:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def process_job(self, payload: JobRequest) -> ProposalResult:
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = create_initial_state(payload)

        self.logger.info("Processing job thread_id=%s", thread_id)
        result = await self.graph.ainvoke(initial_state, config=config)

        return ProposalResult(
            proposal=result.get("proposal", ""),
            developer_id=result.get("developer_id", ""),
            developer_name=result.get("developer_name", ""),
            verdict=result.get("verdict", ""),
            verdict_reason=result.get("verdict_reason", ""),
            revision_count=result.get("revision_count", 0),
            versions=result.get("versions", []),
            thread_id=thread_id,
        )

    async def revise_proposal(self, request: RevisionRequest) -> ProposalResult:
        config = {"configurable": {"thread_id": request.thread_id}}

        self.logger.info("Resuming thread_id=%s feedback=%r", request.thread_id, request.feedback)
        result = await self.graph.ainvoke(Command(resume=request.feedback), config=config)

        return ProposalResult(
            proposal=result.get("proposal", ""),
            developer_id=result.get("developer_id", ""),
            developer_name=result.get("developer_name", ""),
            verdict=result.get("verdict", ""),
            verdict_reason=result.get("verdict_reason", ""),
            revision_count=result.get("revision_count", 0),
            versions=result.get("versions", []),
            thread_id=request.thread_id,
        )
