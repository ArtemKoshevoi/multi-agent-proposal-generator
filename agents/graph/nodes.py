from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import interrupt

from agents.environments import environments
from agents.graph.state import ProposalState
from agents.rag.search import search_profile

model = ChatAnthropic(
    model="claude-haiku-4-5-20251001",  # type: ignore[call-arg]
    temperature=0,
    api_key=environments.ANTHROPIC_API_KEY,
)

writer_model = ChatAnthropic(
    model="claude-sonnet-4-6",  # type: ignore[call-arg]
    temperature=0.3,
    api_key=environments.ANTHROPIC_API_KEY,
)

def _build_proposal_system_prompt(developer_name: str) -> str:
    return f"""You are an Upwork proposal writer for a senior developer named {developer_name}.
The developer's skills, experience, and past projects are in FREELANCER PROFILE below — use them.

FORMAT:
- If PROPOSAL QUESTIONS are listed: write a short cover letter (3-4 sentences), then answer each question labeled Q1:, Q2:, etc., separated by blank lines.
- If no PROPOSAL QUESTIONS: write a single block proposal (5-8 sentences).
- If the client name is known, open with "Hi [name],"

WRITING RULES:
- Plain text only. No markdown, no bold, no bullet points, no headers.
- Never open with "I am excited", "I have extensive experience", or "I noticed your job posting".
- Open with a specific observation about their problem, stack, or business — not a generic intro about the developer.
- Reference 1-2 real projects with full URLs when relevant. Format: Name (https://url)
- No em-dashes (—). Use colons, commas, or parentheses instead.
- Use contractions naturally. Keep it direct and conversational.
- If the developer is missing something the client explicitly requires, flag it honestly in one sentence. Honesty builds trust.
- If client research notes are provided, weave in one specific detail that shows you understand their business.
- End with a calm next step: suggest a short call or ask one focused question.

End with exactly:
Best regards,
{developer_name}"""


def analyze_job(state: ProposalState) -> dict:
    print(">> Node: analyze_job")

    parts = []
    if state.get("title"):
        parts.append(f"Title: {state['title']}")
    features = state.get("features")
    if features:
        parts.append("Details: " + " | ".join(features))
    skills = state.get("skills")
    if skills:
        parts.append("Required skills: " + ", ".join(skills))
    parts.append(f"Description:\n{state['job_text']}")
    analyze_input = "\n".join(parts)

    response = model.invoke([
        SystemMessage(content="You are a job analyzer. Extract: tech stack, budget (use the Details line if present), duration, project type, experience level. Be concise and structured."),
        HumanMessage(content=analyze_input),
    ])

    return {"analysis": response.content}


def qualify_job(state: ProposalState) -> dict:
    print(">> Node: qualify_job")

    features = state.get("features")
    skills = state.get("skills")
    features_text = "\n".join(features) if features else "Not specified"
    skills_text = ", ".join(skills) if skills else "Not specified"

    qualify_input = f"""JOB ANALYSIS:
{state['analysis']}

STRUCTURED JOB DETAILS (budget, duration, level):
{features_text}

REQUIRED SKILLS:
{skills_text}

COMPETITION: {state.get('client_competition_level') or 'Unknown'} proposals already submitted"""

    response = model.invoke([
        SystemMessage(content="""You are a job qualifier for an outstaffing company.

Our team covers: React, Next.js, TypeScript, Node.js, React Native, Angular, Python, AI/LLM integrations. Senior level, 5-10 years experience per developer.

Verdict rules:
- SKIP: budget confirmed below $25/hr, or required stack completely outside our expertise (e.g. pure PHP, .NET, iOS native, embedded C)
- GO: strong stack match, budget $30+/hr confirmed
- MAYBE: partial stack match, budget unclear, or budget in range but unconfirmed

Respond with exactly:
VERDICT: GO or MAYBE or SKIP
REASON: one sentence"""),
        HumanMessage(content=qualify_input),
    ])

    text = str(response.content)
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

    query_parts = []
    title = state.get("title")
    if title:
        query_parts.append(title)
    skills = state.get("skills")
    if skills:
        query_parts.append(", ".join(skills))
    query_parts.append(state["job_text"][:600])
    query = " ".join(query_parts)

    results = search_profile(query, developer_id=state["developer_id"], n_results=5)
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

    features = state.get("features")
    if features:
        parts.append("JOB DETAILS (budget, duration, level):\n" + "\n".join(features))

    skills = state.get("skills")
    if skills:
        parts.append(f"REQUIRED SKILLS: {', '.join(skills)}")

    questions_section = _build_questions_section(state)
    if questions_section:
        parts.append(questions_section)

    parts.append(f"CLIENT CONTEXT:\n{_build_client_context(state)}")
    parts.append(f"JOB ANALYSIS:\n{state['analysis']}")
    parts.append(f"FREELANCER PROFILE (relevant sections):\n{state['rag_context']}")

    if state["revision_count"] > 0 and state["proposal_feedback"]:
        parts.append(f"Previous proposal was rejected. Address this feedback:\n{state['proposal_feedback']}")

    user_message = "\n\n".join(parts)

    response = writer_model.invoke([
        SystemMessage(content=_build_proposal_system_prompt(state["developer_name"])),
        HumanMessage(content=user_message),
    ])

    return {
        "proposal": response.content,
        "revision_count": state["revision_count"] + 1,
    }


def evaluate_proposal(state: ProposalState) -> dict:
    print(">> Node: evaluate_proposal")

    questions = state.get("proposal_questions") or []
    questions_note = ""
    if questions:
        labeled = "\n".join(f"Q{i}: {q}" for i, q in enumerate(questions, 1))
        questions_note = f"\n\nPROPOSAL QUESTIONS that must be answered:\n{labeled}"

    eval_input = f"Job:\n{state['job_text']}{questions_note}\n\nProposal:\n{state['proposal']}"

    response = model.invoke([
        SystemMessage(content="""You are a strict Upwork proposal reviewer.

Evaluate against these criteria:
1. Does NOT open with a generic phrase like "I am excited", "I have extensive experience", or "I noticed your job posting"
2. Opens with a specific observation about the client's problem, stack, or business
3. References at least one real project with a full URL in the format: Name (https://url)
4. If PROPOSAL QUESTIONS were listed: each question has a clearly labeled answer (Q1:, Q2:, etc.)
5. No em-dashes (—) anywhere in the text
6. Plain text only — no markdown, no bold, no bullet points, no headers
7. Ends with a concrete next step or one focused question

Respond with exactly:
GRADE: APPROVED or NEEDS_IMPROVEMENT
FEEDBACK: one or two sentences on the most important thing to fix (only if NEEDS_IMPROVEMENT)"""),
        HumanMessage(content=eval_input),
    ])

    text = str(response.content)
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


def manager_review(state: ProposalState) -> dict:
    print(">> Node: manager_review — waiting for human feedback")
    feedback = str(interrupt(state["proposal"]))
    approved = feedback.lower().strip() == "approve"
    print(f"   Manager: {'APPROVED' if approved else repr(feedback)}")
    return {
        "versions": [state["proposal"]],
        "proposal_feedback": feedback,
        "status": "approved" if approved else "active",
    }
