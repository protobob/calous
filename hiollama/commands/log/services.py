"""Log management services."""
from typing import NamedTuple


class LogOperationResult(NamedTuple):
    """Result of log operations."""
    success: bool
    message: str = ""
    data: str = ""


class LogService:
    """Service for managing log operations."""
    
    def __init__(self, app):
        self.app = app
    
    def enable_logging(self) -> LogOperationResult:
        """Enable unified logging."""
        from ...unified_logger import unified_logger
        
        if unified_logger.enabled:
            return LogOperationResult(success=False, message="Unified logging is already enabled")
        else:
            unified_logger.toggle_logging()
            return LogOperationResult(success=True, message="Unified logging is now: enabled")
    
    def disable_logging(self) -> LogOperationResult:
        """Disable unified logging."""
        from ...unified_logger import unified_logger
        
        if not unified_logger.enabled:
            return LogOperationResult(success=False, message="Unified logging is already disabled")
        else:
            unified_logger.toggle_logging()
            return LogOperationResult(success=True, message="Unified logging is now: disabled")
    
    def get_today_log(self) -> LogOperationResult:
        """Get today's unified log content."""
        from pathlib import Path
        from datetime import datetime
        from ...constants import LOG_DIR
        
        today_log = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.txt"
        
        if not today_log.exists():
            return LogOperationResult(
                success=False, 
                message=f"No unified log found for today. Log would be created at: {today_log}"
            )
        
        try:
            with open(today_log, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            if not content:
                return LogOperationResult(
                    success=False,
                    message="Unified log exists but is empty."
                )
            
            return LogOperationResult(
                success=True,
                data=content,
                message=f"Unified Log for {datetime.now().strftime('%Y-%m-%d')}"
            )
            
        except Exception as e:
            return LogOperationResult(
                success=False,
                message=f"Error reading unified log: {e}"
            )
