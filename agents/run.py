import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.graph.workflow import build_graph, create_initial_state
from dotenv import load_dotenv


load_dotenv()


def run(job_file: str):
    """Runs the proposal graph for a single job file."""

    with open(job_file, "r", encoding="utf-8") as f:
        job_text = f.read()

    graph = build_graph()

    # thread_id identifies this job processing session
    config = {"configurable": {"thread_id": f"job-{job_file}"}}

    initial_state = create_initial_state(job_text)

    result = graph.invoke(initial_state, config=config)

    print("\n" + "="*60)
    if result["status"] == "skipped":
        print("JOB SKIPPED")
        print(f"Reason: {result['verdict_reason']}")
    else:
        print("FINAL PROPOSAL:")
        print("="*60)
        print(result["proposal"])


if __name__ == "__main__":
    run("mock_data/jobs/job-02.txt")