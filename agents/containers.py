from typing import Annotated

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide
from fastapi import Depends

from agents.services.proposal_service import ProposalService


class ProposalContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["agents.router"])

    # Starts as None — overridden in lifespan once the graph is compiled
    graph: providers.Provider = providers.Object(None)

    proposal_service = providers.Factory(
        ProposalService,
        graph=graph,
    )


ProposalServiceDep = Annotated[
    ProposalService,
    Depends(Provide[ProposalContainer.proposal_service]),
]
