from typing import TypedDict, Any, Dict
from langgraph.graph import StateGraph, END

class WorkflowState(TypedDict):
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    current_node: str

async def execute_llm_node(state: WorkflowState):
    prompt = state["inputs"].get("prompt", "Hello")
    state["outputs"]["llm_response"] = f"Processed via LLM Node: {prompt}"
    return state

async def execute_api_node(state: WorkflowState):
    url = state["inputs"].get("url", "https://api.example.com")
    state["outputs"]["api_response"] = f"Fetched data from {url}"
    return state

def route_next(state: WorkflowState):
    if state["current_node"] == "llm":
        return "api"
    return "end"

workflow = StateGraph(WorkflowState)
workflow.add_node("llm", execute_llm_node)
workflow.add_node("api", execute_api_node)

workflow.set_entry_point("llm")
workflow.add_conditional_edges("llm", route_next, {"api": "api", "end": END})
workflow.add_edge("api", END)

workflow_app = workflow.compile()
