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
Artem: senior frontend/fullstack — React, Next.js, TypeScript, Node.js, React Native. 7 years experience.

FORMAT:
- If PROPOSAL QUESTIONS are listed: write a short cover letter (3-4 sentences), then answer each question labeled Q1:, Q2:, etc., separated by blank lines.
- If no PROPOSAL QUESTIONS: write a single block proposal (5-8 sentences).
- If the client name is known, open with "Hi [name],"

WRITING RULES:
- Plain text only. No markdown, no bold, no bullet points, no headers.
- Never open with "I am excited", "I have extensive experience", or "I noticed your job posting".
- Open with a specific observation about their problem, stack, or business — not a generic intro about Artem.
- Reference 1-2 real projects with full URLs when relevant. Format: Name (https://url)
- No em-dashes (—). Use colons, commas, or parentheses instead.
- Use contractions naturally. Keep it direct and conversational.
- If Artem is missing something the client explicitly requires, flag it honestly in one sentence. Honesty builds trust.
- If client research notes are provided, weave in one specific detail that shows you understand their business.
- End with a calm next step: suggest a short call or ask one focused question.

End with exactly:
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


def _build_client_context(state: ProposalState) -> str:
    parts = []
    if state.get("client_name"):
        parts.append(f"Client name: {state['client_name']}")
    if state.get("client_company"):
        parts.append(f"Company: {state['client_company']}")
    if state.get("client_company_domain"):
        parts.append(f"Website: {state['client_company_domain']}")
    if state.get("client_location"):
        parts.append(f"Location: {state['client_location']}")
    if state.get("client_rating"):
        parts.append(f"Upwork rating: {state['client_rating']}")
    if state.get("client_total_spend"):
        parts.append(f"Total Upwork spend: {state['client_total_spend']}")
    if state.get("client_competition_level"):
        parts.append(f"Proposals already submitted: {state['client_competition_level']}")
    if state.get("client_previous_jobs_summary"):
        parts.append(f"Past hiring pattern: {state['client_previous_jobs_summary']}")
    if state.get("client_person_notes"):
        parts.append(f"About the person: {state['client_person_notes']}")
    if state.get("client_company_notes"):
        parts.append(f"About the company: {state['client_company_notes']}")
    return "\n".join(parts) if parts else "No client research available."


def _build_questions_section(state: ProposalState) -> str:
    questions = state.get("proposal_questions")
    if not questions:
        return ""
    lines = ["PROPOSAL QUESTIONS (answer each one):"]
    for i, q in enumerate(questions, 1):
        lines.append(f"Q{i}: {q}")
    return "\n".join(lines)


def write_proposal(state: ProposalState) -> dict:
    print(f">> Node: write_proposal (revision #{state['revision_count']})")

    parts = []

    if state.get("title"):
        parts.append(f"JOB TITLE: {state['title']}")

    parts.append(f"JOB DESCRIPTION:\n{state['job_text']}")

    if state.get("features"):
        parts.append("JOB DETAILS (budget, duration, level):\n" + "\n".join(state["features"]))

    if state.get("skills"):
        parts.append(f"REQUIRED SKILLS: {', '.join(state['skills'])}")

    questions_section = _build_questions_section(state)
    if questions_section:
        parts.append(questions_section)

    parts.append(f"CLIENT CONTEXT:\n{_build_client_context(state)}")
    parts.append(f"JOB ANALYSIS:\n{state['analysis']}")
    parts.append(f"FREELANCER PROFILE (relevant sections):\n{state['rag_context']}")

    if state["revision_count"] > 0 and state["proposal_feedback"]:
        parts.append(f"Previous proposal was rejected. Address this feedback:\n{state['proposal_feedback']}")

    user_message = "\n\n".join(parts)

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
