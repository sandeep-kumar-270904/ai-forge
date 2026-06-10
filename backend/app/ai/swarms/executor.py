import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from ...crud.crud_swarms import swarm
from .supervisor import SupervisorRouter

logger = logging.getLogger(__name__)

class SwarmExecutor:
    @staticmethod
    async def invoke_swarm(db: AsyncSession, swarm_id: str, input_message: str) -> Dict[str, Any]:
        """
        Orchestrates the LangGraph multi-agent loop for the given swarm.
        """
        target_swarm = await swarm.get_with_agents(db, id=swarm_id)
        if not target_swarm:
            raise HTTPException(status_code=404, detail="Swarm not found")
            
        state = {
            "messages": [{"role": "user", "content": input_message}],
            "loop_count": 0
        }
        
        # Simulated LangGraph Execution Loop
        while state["loop_count"] < target_swarm.max_loops:
            next_agent_id = await SupervisorRouter.decide_next_agent(target_swarm, state)
            
            if next_agent_id == "FINISH":
                break
                
            state["messages"].append({
                "role": "agent", 
                "agent_id": next_agent_id, 
                "content": "Simulated agent output"
            })
            
            state["loop_count"] += 1
            
        if state["loop_count"] >= target_swarm.max_loops:
            logger.warning(f"Swarm {swarm_id} hit max loops ({target_swarm.max_loops}). Terminating.")
            
        return {
            "status": "completed",
            "loops_executed": state["loop_count"],
            "final_state": state
        }
