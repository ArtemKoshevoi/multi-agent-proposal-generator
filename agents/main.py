from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from agents.environments import environments
from agents.containers import ProposalContainer
from agents.lifespans import graph_lifespan
from agents.router import router

container = ProposalContainer()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with graph_lifespan(container):
        yield


app = FastAPI(
    title="Upwork Proposal Agent",
    version="0.1.0",
    debug=environments.DEBUG,
    lifespan=lifespan,
)

app.state.container = container
app.include_router(router)
