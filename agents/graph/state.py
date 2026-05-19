from typing import TypedDict, Optional


class ProposalState(TypedDict):
    # input
    job_text: str              # original job description

    # analysis results
    analysis: str              # structured job analysis
    verdict: str               # GO / MAYBE / SKIP
    verdict_reason: str        # one sentence why

    # rag results
    rag_context: str           # relevant profile sections

    # proposal
    proposal: str              # generated proposal text
    proposal_feedback: str     # evaluator feedback if revision needed
    revision_count: int        # how many times proposal was revised

    # flow control
    status: str                # active / skipped / approved