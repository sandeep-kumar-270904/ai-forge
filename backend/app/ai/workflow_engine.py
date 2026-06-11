from typing import TypedDict, Any, Dict
from langgraph.graph import StateGraph, START, END
from app.models.workflow import Workflow

# A flexible state that can handle diverse inputs for the visual workflow
class DynamicState(TypedDict):
    input: str
    output: str
    scratchpad: dict

class DynamicWorkflowEngine:
    """
    Takes a database-driven DAG (Workflow, Nodes, Edges) and compiles it into
    an executable LangGraph StateGraph on the fly.
    """
    
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.builder = StateGraph(DynamicState)
        self._compile()

    def _compile(self):
        # ---------------------------------------------------------
        # Node Execution Factories
        # ---------------------------------------------------------
        def create_llm_node(config):
            async def llm_step(state: DynamicState):
                # In production, this would invoke LangChain chat models
                # Here we simulate the dynamic execution using the config
                prompt = config.get("prompt", "Default instruction")
                return {"output": f"LLM executed [{prompt}] against input: {state.get('input')}"}
            return llm_step

        def create_tool_node(config):
            async def tool_step(state: DynamicState):
                tool_name = config.get("tool_name", "unknown_tool")
                return {"scratchpad": {"last_tool": tool_name, "status": "success"}}
            return tool_step

        # 1. Add Nodes to LangGraph
        for node in self.workflow.nodes:
            if node.node_type == "llm":
                self.builder.add_node(node.id, create_llm_node(node.config or {}))
            elif node.node_type == "tool":
                self.builder.add_node(node.id, create_tool_node(node.config or {}))
            # '__start__' and '__end__' are reserved by LangGraph so they aren't added as explicit nodes

        # 2. Add Edges to LangGraph
        for edge in self.workflow.edges:
            source = START if edge.source_node_id == "__start__" else edge.source_node_id
            target = END if edge.target_node_id == "__end__" else edge.target_node_id
            
            if edge.condition_type == "always" or not edge.condition_type:
                self.builder.add_edge(source, target)
            elif edge.condition_type == "conditional":
                # In a real implementation, this router would evaluate a JSONata/JMESPath
                # expression from edge.condition_config against the `state`
                def route_condition(state: DynamicState):
                    return target 
                
                self.builder.add_conditional_edges(
                    source,
                    route_condition,
                    {target: target} # routing map
                )
        
        # 3. Compile the graph
        self.graph = self.builder.compile()

    async def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the compiled graph asynchronously"""
        return await self.graph.ainvoke(state)
