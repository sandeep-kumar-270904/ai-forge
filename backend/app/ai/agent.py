import json
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from .rag import search_knowledge_base

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    workspace_id: str

async def knowledge_base_tool(query: str, workspace_id: str) -> str:
    """Search the workspace knowledge base for relevant information."""
    results = await search_knowledge_base(query, f"workspace_{workspace_id}", k=3)
    if not results:
        return "No relevant information found in the knowledge base."
    return "\n\n".join([doc.page_content for doc in results])

tools = [
    {
        "type": "function",
        "function": {
            "name": "knowledge_base_search",
            "description": "Search the workspace knowledge base for relevant information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up in the knowledge base."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

model = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

async def call_model(state: AgentState):
    messages = state["messages"]
    response = await model.ainvoke(messages)
    return {"messages": [response]}

async def execute_tools(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    tool_calls = last_message.tool_calls
    tool_responses = []
    
    for tool_call in tool_calls:
        if tool_call["name"] == "knowledge_base_search":
            query = tool_call["args"]["query"]
            result = await knowledge_base_tool(query, state["workspace_id"])
            tool_responses.append(
                ToolMessage(content=result, name=tool_call["name"], tool_call_id=tool_call["id"])
            )
            
    return {"messages": tool_responses}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    return "continue"

workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("action", execute_tools)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END
    }
)
workflow.add_edge("action", "agent")

app = workflow.compile()
