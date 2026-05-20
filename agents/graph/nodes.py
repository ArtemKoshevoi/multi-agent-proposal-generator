from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from agents.environments import environments
from agents.graph.state import ProposalState
from agents.rag.search import search_profile

MODEL_NAME = "claude-haiku-4-5-20251001"

model = ChatAnthropic(
    model=MODEL_NAME,
    temperature=0,
    api_key=environments.ANTHROPIC_API_KEY,
)

PROPOSAL_SYSTEM_PROMPT = """You are an Upwork proposal writer for a senior developer named Artem Koshevoi.

Write a short, credible proposal (5-8 sentences) that:
- Opens with a specific observation about the client's problem or project
- References 1-2 relevant projects from the provided profile sections with URLs
- Explains briefly how Artem would approach this work
- Ends with a calm next step (suggest a call or ask one focused question)

Rules:
- Plain text only, no markdown formatting
- No bold, no bullet points, no headers
- No generic phrases like "I am excited" or "I have extensive experience"
- Use contractions naturally
- Keep it conversational and direct

End with exactly this signature:
Best regards,
Artem Koshevoi"""


def analyze_job(state: ProposalState) -> dict:
    print(">> Node: analyze_job")

    response = model.invoke([
        SystemMessage(content="You are a job analyzer. Extract: tech stack, budget if mentioned, duration, project type, experience level. Be concise and structured."),
        HumanMessage(content=state["job_text"]),
    ])

    return {"analysis": response.content}


def qualify_job(state: ProposalState) -> dict:
    print(">> Node: qualify_job")

    response = model.invoke([
        SystemMessage(content="""You are a job qualifier for an outstaffing company.

Our developer: Artem Koshevoi — senior frontend/fullstack, React, Next.js, TypeScript, Node.js, React Native. 7 years experience.

Verdict rules:
- SKIP: budget below $25/hr, or stack completely outside our expertise
- GO: React/Next.js/TypeScript/Node.js stack, budget $30+/hr
- MAYBE: partial match or budget unclear

Respond with exactly:
VERDICT: GO or MAYBE or SKIP
REASON: one sentence"""),
        HumanMessage(content=state["analysis"]),
    ])

    text = response.content
    verdict = "MAYBE"
    reason = text

    for line in text.split("\n"):
        if line.startswith("VERDICT:"):
            verdict = line.replace("VERDICT:", "").strip()
        if line.startswith("REASON:"):
            reason = line.replace("REASON:", "").strip()

    status = "skipped" if verdict == "SKIP" else "active"

    return {
        "verdict": verdict,
        "verdict_reason": reason,
        "status": status,
    }


def search_rag(state: ProposalState) -> dict:
    print(">> Node: search_rag")

    results = search_profile(state["job_text"], n_results=4)
    context = "\n\n---\n\n".join(results)

    return {"rag_context": context}


def write_proposal(state: ProposalState) -> dict:
    print(f">> Node: write_proposal (revision #{state['revision_count']})")

    extra = ""
    if state["revision_count"] > 0 and state["proposal_feedback"]:
        extra = f"\n\nPrevious proposal was rejected. Address this feedback:\n{state['proposal_feedback']}"

    user_message = f"""JOB POST:
{state['job_text']}

JOB ANALYSIS:
{state['analysis']}

FREELANCER PROFILE (relevant sections):
{state['rag_context']}{extra}"""

    response = model.invoke([
        SystemMessage(content=PROPOSAL_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    return {
        "proposal": response.content,
        "revision_count": state["revision_count"] + 1,
    }


def evaluate_proposal(state: ProposalState) -> dict:
    print(">> Node: evaluate_proposal")

    response = model.invoke([
        SystemMessage(content="""You are a strict Upwork proposal reviewer.

Evaluate the proposal against these criteria:
1. Opens with specific observation about client's problem (not generic intro)
2. References at least one real project or URL
3. Explains concrete approach (not vague promises)
4. Has clear next step or question at the end
5. No markdown, no bullet points, plain text only

Respond with exactly:
GRADE: APPROVED or NEEDS_IMPROVEMENT
FEEDBACK: one or two sentences on what to fix (only if NEEDS_IMPROVEMENT)"""),
        HumanMessage(content=f"Job:\n{state['job_text']}\n\nProposal:\n{state['proposal']}"),
    ])

    text = response.content
    grade = "APPROVED"
    feedback = ""

    for line in text.split("\n"):
        if line.startswith("GRADE:"):
            grade = line.replace("GRADE:", "").strip()
        if line.startswith("FEEDBACK:"):
            feedback = line.replace("FEEDBACK:", "").strip()

    print(f"   Grade: {grade}")
    if feedback:
        print(f"   Feedback: {feedback}")

    status = "approved" if grade == "APPROVED" else "active"

    return {
        "proposal_feedback": feedback,
        "status": status,
    }


def reject_job(state: ProposalState) -> dict:
    print(f">> Node: reject_job — {state['verdict_reason']}")
    return {}
