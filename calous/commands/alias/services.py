"""Service layer for alias management operations."""
from typing import Dict, Optional, Tuple
from ..registry import registry
from ...config import ConfigManager


class AliasResult:
    """Result object for alias operations."""
    
    def __init__(self, success: bool, message: str = "", data: Optional[Dict] = None):
        self.success = success
        self.message = message
        self.data = data or {}


class AliasService:
    """Service class for managing command aliases."""
    
    @staticmethod
    def add_alias(alias: str, command: str) -> AliasResult:
        """Add a new command alias with validation."""
        # Validate that target command exists
        if not registry.get_command(command):
            return AliasResult(
                success=False,
                message=f"Command '{command}' does not exist"
            )
        
        # Prevent aliases that conflict with existing command names
        if registry.get_command(alias) and alias not in registry.user_aliases:
            return AliasResult(
                success=False,
                message=f"'{alias}' is already a command name"
            )
        
        # Check if alias already exists
        existing_command = None
        if alias in registry.user_aliases:
            existing_command = registry.user_aliases[alias]
        
        # Add the alias
        success = registry.add_user_alias(alias, command)
        if success:
            message = f"Alias created: '{alias}' → '{command}'"
            if existing_command:
                message = f"Alias updated: '{alias}' → '{command}' (was pointing to '{existing_command}')"
            return AliasResult(
                success=True,
                message=message,
                data={"alias": alias, "command": command, "was_update": existing_command is not None}
            )
        else:
            return AliasResult(
                success=False,
                message="Failed to create alias"
            )
    
    @staticmethod
    def remove_alias(alias: str) -> AliasResult:
        """Remove a command alias."""
        if alias not in registry.user_aliases:
            return AliasResult(
                success=False,
                message=f"Alias '{alias}' does not exist"
            )
        
        command = registry.user_aliases[alias]
        success = registry.remove_user_alias(alias)
        
        if success:
            return AliasResult(
                success=True,
                message=f"Alias removed: '{alias}' (was pointing to '{command}')",
                data={"alias": alias, "command": command}
            )
        else:
            return AliasResult(
                success=False,
                message="Failed to remove alias"
            )
    
    @staticmethod
    def list_aliases() -> AliasResult:
        """Get all user-defined aliases."""
        aliases = registry.list_user_aliases()
        return AliasResult(
            success=True,
            message=f"Found {len(aliases)} aliases" if aliases else "No aliases defined",
            data={"aliases": aliases}
        )
    
    @staticmethod
    def check_existing_alias(alias: str) -> Tuple[bool, Optional[str]]:
        """Check if alias exists and return the command it points to."""
        if alias in registry.user_aliases:
            return True, registry.user_aliases[alias]
        return False, None
