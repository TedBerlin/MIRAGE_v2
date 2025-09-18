"""
Agents module for MIRAGE v2.

This module provides AI agents with optimized prompts for pharmaceutical research.
"""

from .agent_prompts import AgentPrompts
from .agent_manager import AgentManager
from .generator_agent import GeneratorAgent
from .verifier_agent import VerifierAgent
from .reformer_agent import ReformerAgent
from .translator_agent import TranslatorAgent

__all__ = [
    "AgentPrompts",
    "AgentManager",
    "GeneratorAgent",
    "VerifierAgent", 
    "ReformerAgent",
    "TranslatorAgent"
]
