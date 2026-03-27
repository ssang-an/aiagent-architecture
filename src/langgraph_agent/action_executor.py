from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from .state import ActionResult, AgentState, PlanAction
from .tools.registry import TOOL_REGISTRY


def _dependencies_done(action: PlanAction, done: set[str]) -> bool:
    return all(dep in done for dep in action.get("dependencies", []))


def _run_action(action: PlanAction) -> ActionResult:
    tool = TOOL_REGISTRY.get(action["tool_name"])
    if tool is None:
        return {
            "action_id": action["action_id"],
            "status": "failed",
            "output": {},
            "error": "tool_not_found",
        }

    try:
        output = tool.run(action.get("input", {}))
        return {
            "action_id": action["action_id"],
            "status": "success",
            "output": output,
            "error": "",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "action_id": action["action_id"],
            "status": "failed",
            "output": {},
            "error": str(exc),
        }


def parallel_action_node(state: AgentState) -> AgentState:
    actions = state.get("plan_actions", [])
    results: list[ActionResult] = []
    retry_queue: list[str] = []
    deferred_queue: list[str] = state.get("deferred_queue", [])

    done_actions = {
        res["action_id"]
        for res in state.get("action_results", [])
        if res["status"] in {"success", "skipped", "deferred"}
    }

    ready: list[PlanAction] = []
    for action in actions:
        if not action.get("executable", False):
            results.append(
                {
                    "action_id": action["action_id"],
                    "status": "deferred",
                    "output": {},
                    "error": action.get("reason", "not_executable"),
                }
            )
            deferred_queue.append(action["action_id"])
            done_actions.add(action["action_id"])
            continue

        if _dependencies_done(action, done_actions):
            ready.append(action)
        else:
            results.append(
                {
                    "action_id": action["action_id"],
                    "status": "skipped",
                    "output": {},
                    "error": "dependencies_not_satisfied",
                }
            )

    with ThreadPoolExecutor(max_workers=max(1, min(8, len(ready) or 1))) as executor:
        future_map = {executor.submit(_run_action, action): action for action in ready}
        for future in as_completed(future_map):
            result = future.result()
            results.append(result)
            if result["status"] == "failed":
                retry_queue.append(result["action_id"])

    return {
        "action_results": state.get("action_results", []) + results,
        "retry_queue": retry_queue,
        "deferred_queue": deferred_queue,
    }
