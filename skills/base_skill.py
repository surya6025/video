"""
Base skill class for JarvisX
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from core.permissions import Capability

class BaseSkill(ABC):
    """Abstract base class for all JarvisX skills"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "Base skill description"
        self.capabilities = []
        self.requires_permission = None  # Set to specific capability if needed
        self.version = "1.0.0"
    
    @abstractmethod
    def run(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the skill with the given query and context
        
        Args:
            query: User's query string
            context: Additional context information
            
        Returns:
            Dictionary with result information:
            {
                "type": "text|table|chart|files|action",
                "content": "Main result content",
                "artifacts": ["list", "of", "generated", "files"],
                "metadata": {"additional": "info"}
            }
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this skill"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "version": self.version,
            "requires_permission": self.requires_permission.value if self.requires_permission else None
        }
    
    def validate_input(self, query: str, context: Dict[str, Any]) -> bool:
        """Validate input before execution"""
        return bool(query and query.strip())
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess the query string"""
        return query.strip()
    
    def postprocess_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess the result before returning"""
        # Ensure required fields are present
        if "type" not in result:
            result["type"] = "text"
        
        if "content" not in result:
            result["content"] = "No content generated"
        
        if "artifacts" not in result:
            result["artifacts"] = []
        
        if "metadata" not in result:
            result["metadata"] = {}
        
        return result
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors during skill execution"""
        return {
            "type": "text",
            "content": f"Error executing {self.name}: {str(error)}",
            "artifacts": [],
            "metadata": {
                "error": True,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        }
    
    def get_usage_examples(self) -> List[str]:
        """Get example usage queries for this skill"""
        return []
    
    def get_help_text(self) -> str:
        """Get help text for this skill"""
        return f"""
        **{self.name}**
        
        {self.description}
        
        **Capabilities:**
        {chr(10).join(f"• {cap}" for cap in self.capabilities)}
        
        **Examples:**
        {chr(10).join(f"• {ex}" for ex in self.get_usage_examples())}
        """