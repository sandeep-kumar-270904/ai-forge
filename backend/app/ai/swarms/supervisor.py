import logging
from typing import Dict, Any, List
from ...models.swarms import Swarm, SwarmAgentPersona

logger = logging.getLogger(__name__)

class SupervisorRouter:
    @staticmethod
    async def decide_next_agent(
        swarm: Swarm, 
        current_state: Dict[str, Any],
        model_gateway=None
    ) -> str:
        """
        Analyzes the `current_state` (e.g. list of messages) and decides which
        agent in the swarm should act next, or if the swarm has finished.
        Returns the ID of the agent, or 'FINISH'.
        """
        agents: List[SwarmAgentPersona] = swarm.agents
        if not agents:
            logger.warning(f"Swarm {swarm.id} has no agents.")
            return "FINISH"
            
        agent_names = [a.name for a in agents]
        
        if not model_gateway:
            messages = current_state.get("messages", [])
            if not messages or len(messages) == 1:
                return agents[0].id
            return "FINISH"
            
        prompt = f"""
        You are the Supervisor of a Multi-Agent Swarm.
        Your job is to route the next action to the correct worker agent based on the conversation history.
        
        WORKERS AVAILABLE:
        {', '.join(agent_names)}
        
        CONVERSATION HISTORY:
        {current_state.get('messages', [])}
        
        If the objective is complete, route to 'FINISH'.
        Otherwise, route to the name of the worker agent.
        Return ONLY the name of the worker or FINISH.
        """
        
        return "FINISH"
