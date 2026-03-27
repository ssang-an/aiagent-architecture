from __future__ import annotations

import re
from itertools import count

from .state import AgentState, PlanAction, TaskItem


def parse_intent_node(state: AgentState) -> AgentState:
    goal = state.get("user_goal", "").strip()
    if not goal:
        goal = "general_assistance"
    return {"user_goal": goal}


def decompose_tasks_node(state: AgentState) -> AgentState:
    goal = state.get("user_goal", "")
    chunks = [part.strip() for part in re.split(r"[\n,;]+", goal) if part.strip()]
    if not chunks:
        chunks = [goal or "handle_user_request"]

    tasks: list[TaskItem] = []
    for idx, chunk in enumerate(chunks, start=1):
        tasks.append(
            {
                "task_id": f"t-{idx}",
                "description": chunk,
                "priority": idx,
            }
        )

    return {"tasks": tasks}


def build_action_plan_node(state: AgentState) -> AgentState:
    action_seq = count(1)
    actions: list[PlanAction] = []

    for task in state.get("tasks", []):
        fetch_id = f"a-{next(action_seq)}"
        analyze_id = f"a-{next(action_seq)}"

        actions.append(
            {
                "action_id": fetch_id,
                "task_id": task["task_id"],
                "tool_name": "knowledge_search",
                "input": {"query": task["description"]},
                "dependencies": [],
                "executable": False,
                "reason": "pending_selector",
            }
        )
        actions.append(
            {
                "action_id": analyze_id,
                "task_id": task["task_id"],
                "tool_name": "summarize_text",
                "input": {"text": task["description"]},
                "dependencies": [fetch_id],
                "executable": False,
                "reason": "pending_selector",
            }
        )

    return {"plan_actions": actions}
