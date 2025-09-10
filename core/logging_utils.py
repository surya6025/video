"""
Logging utilities for JarvisX
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger
import sys

class JarvisXLogger:
    """Centralized logging for JarvisX"""
    
    def __init__(self, log_level: str = "INFO", log_file: str = "logs/jarvisx.log"):
        self.log_level = log_level
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging with file and console handlers"""
        # Remove default loguru handler
        logger.remove()
        
        # Add console handler with colors
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=self.log_level,
            colorize=True
        )
        
        # Add file handler
        log_path = Path(self.log_file)
        log_path.parent.mkdir(exist_ok=True)
        
        logger.add(
            self.log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=self.log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )
        
        # Add action logging
        action_log_path = Path("logs/actions.jsonl")
        action_log_path.parent.mkdir(exist_ok=True)
        
        logger.add(
            str(action_log_path),
            format="{message}",
            level="INFO",
            filter=lambda record: record["extra"].get("type") == "action",
            serialize=True
        )
    
    def log_action(self, action: str, user: str, parameters: Dict[str, Any], 
                   result: str, success: bool = True):
        """Log a user action for audit purposes"""
        action_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "user": user,
            "action": action,
            "parameters": parameters,
            "result": result,
            "success": success
        }
        
        logger.bind(type="action").info(json.dumps(action_data))
    
    def log_error(self, error: Exception, context: str = "", user: str = ""):
        """Log an error with context"""
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "user": user
        }
        
        logger.error(f"Error in {context}: {error}")
        
        # Also log to errors file
        error_log_path = Path("logs/errors.log")
        error_log_path.parent.mkdir(exist_ok=True)
        
        with open(error_log_path, "a") as f:
            f.write(f"{json.dumps(error_data)}\n")
    
    def get_logger(self, name: str):
        """Get a logger instance for a specific module"""
        return logger.bind(name=name)

# Global logger instance
jarvisx_logger = JarvisXLogger()
get_logger = jarvisx_logger.get_logger
log_action = jarvisx_logger.log_action
log_error = jarvisx_logger.log_error