import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dependency_injector import providers

from agents.containers import ProposalContainer
from agents.graph.workflow import build_graph

logger = logging.getLogger(__name__)


@asynccontextmanager
async def graph_lifespan(container: ProposalContainer) -> AsyncGenerator[None, None]:
    graph = build_graph()
    container.graph.override(providers.Object(graph))
    logger.info("Proposal graph initialized")
    try:
        yield
    finally:
        container.graph.reset_override()
        logger.info("Proposal graph torn down")
