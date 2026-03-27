from __future__ import annotations

from .state import AgentState, PlanAction


def _has_policy_violation(action: PlanAction) -> bool:
    blocked_words = {"drop database", "wire transfer", "delete production"}
    payload = " ".join(str(v).lower() for v in action.get("input", {}).values())
    return any(word in payload for word in blocked_words)


def _has_tool_capability(action: PlanAction, available_tools: set[str]) -> bool:
    return action["tool_name"] in available_tools


def _deps_satisfied(action: PlanAction, executable_map: dict[str, bool]) -> bool:
    for dep in action.get("dependencies", []):
        if not executable_map.get(dep, False):
            return False
    return True


def set_executable_flag_node(state: AgentState) -> AgentState:
    available_tools = {"knowledge_search", "summarize_text", "ticket_create"}
    selected: list[PlanAction] = []
    executable_map: dict[str, bool] = {}
    policy_flags: list[str] = state.get("policy_flags", [])

    for action in state.get("plan_actions", []):
        if _has_policy_violation(action):
            action = {**action, "executable": False, "reason": "blocked_by_policy"}
            policy_flags.append(f"blocked:{action['action_id']}")
        elif not _has_tool_capability(action, available_tools):
            action = {**action, "executable": False, "reason": "tool_unavailable"}
        elif not _deps_satisfied(action, executable_map):
            action = {**action, "executable": False, "reason": "dependency_not_ready"}
        else:
            action = {**action, "executable": True, "reason": "ready"}

        executable_map[action["action_id"]] = action["executable"]
        selected.append(action)

    return {
        "plan_actions": selected,
        "policy_flags": policy_flags,
    }
