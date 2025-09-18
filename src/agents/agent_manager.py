"""
Agent Manager for MIRAGE v2.

Manages the lifecycle and coordination of all AI agents.
"""

import structlog
from typing import Dict, Any, Optional
from .agent_prompts import AgentPrompts

logger = structlog.get_logger(__name__)


class AgentManager:
    """Manages all AI agents and their interactions."""
    
    def __init__(self):
        self.prompts = AgentPrompts()
        self.agents = {}
        logger.info("AgentManager initialized")
    
    def get_agent_prompts(self) -> AgentPrompts:
        """Get the agent prompts manager."""
        return self.prompts
    
    def validate_all_agents(self) -> Dict[str, bool]:
        """Validate all agent configurations."""
        return self.prompts.validate_prompts()

