from __future__ import annotations

from collections import Counter

from .state import AgentState


def final_response_node(state: AgentState) -> AgentState:
    results = state.get("action_results", [])
    counter = Counter(result["status"] for result in results)

    summary = {
        "total_actions": len(results),
        "success": counter.get("success", 0),
        "failed": counter.get("failed", 0),
        "skipped": counter.get("skipped", 0),
        "deferred": counter.get("deferred", 0),
        "retry_queue": state.get("retry_queue", []),
    }

    final_answer = (
        f"작업 완료: total={summary['total_actions']} "
        f"success={summary['success']} failed={summary['failed']} "
        f"deferred={summary['deferred']}"
    )

    return {
        "summary": summary,
        "final_answer": final_answer,
    }
