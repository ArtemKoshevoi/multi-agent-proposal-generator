import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dependency_injector import providers
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from agents.containers import ProposalContainer
from agents.environments import environments
from agents.graph.workflow import build_graph

logger = logging.getLogger(__name__)


@asynccontextmanager
async def graph_lifespan(container: ProposalContainer) -> AsyncGenerator[None, None]:
    async with AsyncSqliteSaver.from_conn_string(environments.DB_PATH) as checkpointer:
        graph = build_graph(checkpointer)
        container.graph.override(providers.Object(graph))
        logger.info("Proposal graph initialized (checkpointer: %s)", environments.DB_PATH)
        try:
            yield
        finally:
            container.graph.reset_override()
            logger.info("Proposal graph torn down")
