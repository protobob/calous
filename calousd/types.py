"""Shared types for Hi, Ollama!"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class ActionType(Enum):
    CONTINUE = "continue"
    SWITCH = "switch"
    TWIST = "twist"
    ADDCHAT = "addchat"
    REMOVECHAT = "removechat"
    QUIT = "quit"

@dataclass
class CommandResult:
    action: ActionType
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None