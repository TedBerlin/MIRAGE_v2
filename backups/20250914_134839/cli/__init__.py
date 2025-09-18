"""
CLI module for MIRAGE v2.

This module provides command-line interface for pharmaceutical research operations.
"""

from .main import cli
from .commands import query_command, health_command, audit_command, validate_command

__all__ = [
    "cli",
    "query_command",
    "health_command", 
    "audit_command",
    "validate_command"
]
