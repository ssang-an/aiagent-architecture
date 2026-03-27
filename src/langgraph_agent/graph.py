from __future__ import annotations

from .action_executor import parallel_action_node
from .planner import build_action_plan_node, decompose_tasks_node, parse_intent_node
from .state import AgentState
from .synthesis import final_response_node
from .tool_selector import set_executable_flag_node


def build_graph():
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(AgentState)

    graph.add_node("parse_intent", parse_intent_node)
    graph.add_node("decompose_tasks", decompose_tasks_node)
    graph.add_node("build_action_plan", build_action_plan_node)
    graph.add_node("tool_selector", set_executable_flag_node)
    graph.add_node("parallel_action", parallel_action_node)
    graph.add_node("final_response", final_response_node)

    graph.add_edge(START, "parse_intent")
    graph.add_edge("parse_intent", "decompose_tasks")
    graph.add_edge("decompose_tasks", "build_action_plan")
    graph.add_edge("build_action_plan", "tool_selector")
    graph.add_edge("tool_selector", "parallel_action")
    graph.add_edge("parallel_action", "final_response")
    graph.add_edge("final_response", END)

    return graph.compile()
