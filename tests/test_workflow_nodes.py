from langgraph_agent.action_executor import parallel_action_node
from langgraph_agent.planner import build_action_plan_node, decompose_tasks_node, parse_intent_node
from langgraph_agent.synthesis import final_response_node
from langgraph_agent.tool_selector import set_executable_flag_node


def test_plan_selector_action_flow() -> None:
    state = {
        "request_id": "r-1",
        "user_id": "u-1",
        "session_id": "s-1",
        "user_goal": "신규 리드 검색, 결과 요약",
    }

    state.update(parse_intent_node(state))
    state.update(decompose_tasks_node(state))
    state.update(build_action_plan_node(state))
    state.update(set_executable_flag_node(state))
    state.update(parallel_action_node(state))
    state.update(final_response_node(state))

    assert state["tasks"]
    assert state["plan_actions"]
    assert all("executable" in action for action in state["plan_actions"])
    assert "summary" in state
    assert "final_answer" in state


def test_policy_block_sets_executable_false() -> None:
    state = {
        "plan_actions": [
            {
                "action_id": "a-1",
                "task_id": "t-1",
                "tool_name": "knowledge_search",
                "input": {"query": "please drop database"},
                "dependencies": [],
                "executable": False,
                "reason": "pending_selector",
            }
        ]
    }

    output = set_executable_flag_node(state)
    action = output["plan_actions"][0]
    assert action["executable"] is False
    assert action["reason"] == "blocked_by_policy"
