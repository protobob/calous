"""Command system types and categories."""
import argparse
from typing import Dict, Callable, Any, Optional, List
from dataclasses import dataclass


@dataclass
class CommandDefinition:
    """Definition of a command including its metadata and handler."""
    name: str
    handler: Callable
    description: str
    parser: argparse.ArgumentParser
    aliases: List[str] = None
    category: str = "General"


class CommandCategory:
    """Categories for organizing commands in help output."""
    GENERAL = "General Commands"
    NAVIGATION = "Chat Navigation" 
    MODEL = "Model Management"
    PROMPT = "Prompt Management"
    PERSONA = "Persona Management"
    HISTORY = "Chat History"
    LOGGING = "Logging Operations"
    FILE = "File Operations"
    ALIAS = "Alias Management"
    PLUGIN = "Plugin Management"
    CONTEXT = "Context Management"