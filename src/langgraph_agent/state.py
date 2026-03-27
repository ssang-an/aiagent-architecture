from __future__ import annotations

from typing import Literal, TypedDict


ActionStatus = Literal["pending", "success", "failed", "skipped", "deferred"]


class TaskItem(TypedDict):
    task_id: str
    description: str
    priority: int


class PlanAction(TypedDict):
    action_id: str
    task_id: str
    tool_name: str
    input: dict
    dependencies: list[str]
    executable: bool
    reason: str


class ActionResult(TypedDict):
    action_id: str
    status: ActionStatus
    output: dict
    error: str


class AgentState(TypedDict, total=False):
    request_id: str
    user_id: str
    session_id: str
    user_goal: str

    tasks: list[TaskItem]
    plan_actions: list[PlanAction]
    action_results: list[ActionResult]

    policy_flags: list[str]
    retry_queue: list[str]
    deferred_queue: list[str]

    final_answer: str
    summary: dict
