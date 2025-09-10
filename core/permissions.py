"""
Permission management for JarvisX
Strict security controls for dangerous actions
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from .memory import memory
from .logging_utils import get_logger, log_action

logger = get_logger(__name__)

class PermissionLevel(Enum):
    """Permission levels for capabilities"""
    ASK_EVERY_TIME = "ask-every-time"
    TRUSTED_ONCE = "trusted-once"
    ALWAYS_DENY = "always-deny"
    ALWAYS_ALLOW = "always-allow"

class Capability(Enum):
    """System capabilities that require permissions"""
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    PROCESS_EXECUTION = "process_execution"
    NETWORK_ACCESS = "network_access"
    SYSTEM_CONTROL = "system_control"
    CYBERSECURITY_SCAN = "cybersecurity_scan"
    AUTOMATION_RUN = "automation_run"
    MODEL_TRAINING = "model_training"
    DATABASE_ACCESS = "database_access"
    WEB_SCRAPING = "web_scraping"

class PermissionManager:
    """Manages permissions and security policies"""
    
    def __init__(self):
        self.dangerous_actions = {
            Capability.FILE_WRITE: {
                "description": "Write files to disk",
                "risk_level": "medium",
                "examples": ["CSV export", "model saving", "log writing"]
            },
            Capability.FILE_DELETE: {
                "description": "Delete files from disk",
                "risk_level": "high",
                "examples": ["Cleanup operations", "cache clearing"]
            },
            Capability.PROCESS_EXECUTION: {
                "description": "Execute system commands",
                "risk_level": "high",
                "examples": ["Shell commands", "batch scripts", "PowerShell"]
            },
            Capability.NETWORK_ACCESS: {
                "description": "Access external networks",
                "risk_level": "medium",
                "examples": ["API calls", "web scraping", "downloads"]
            },
            Capability.SYSTEM_CONTROL: {
                "description": "Control system operations",
                "risk_level": "high",
                "examples": ["App launching", "file opening", "system monitoring"]
            },
            Capability.CYBERSECURITY_SCAN: {
                "description": "Perform security scans",
                "risk_level": "low",
                "examples": ["Password checks", "hash verification", "log analysis"]
            },
            Capability.AUTOMATION_RUN: {
                "description": "Run automation workflows",
                "risk_level": "medium",
                "examples": ["Batch operations", "scheduled tasks", "ETL pipelines"]
            },
            Capability.MODEL_TRAINING: {
                "description": "Train machine learning models",
                "risk_level": "low",
                "examples": ["ML model training", "data processing", "model saving"]
            },
            Capability.DATABASE_ACCESS: {
                "description": "Access databases",
                "risk_level": "medium",
                "examples": ["SQLite operations", "data queries", "schema changes"]
            },
            Capability.WEB_SCRAPING: {
                "description": "Scrape web content",
                "risk_level": "low",
                "examples": ["Content extraction", "link gathering", "data collection"]
            }
        }
        
        self.default_policies = {
            Capability.FILE_WRITE: PermissionLevel.ASK_EVERY_TIME,
            Capability.FILE_DELETE: PermissionLevel.ASK_EVERY_TIME,
            Capability.PROCESS_EXECUTION: PermissionLevel.ASK_EVERY_TIME,
            Capability.NETWORK_ACCESS: PermissionLevel.ASK_EVERY_TIME,
            Capability.SYSTEM_CONTROL: PermissionLevel.ASK_EVERY_TIME,
            Capability.CYBERSECURITY_SCAN: PermissionLevel.ALWAYS_ALLOW,
            Capability.AUTOMATION_RUN: PermissionLevel.ASK_EVERY_TIME,
            Capability.MODEL_TRAINING: PermissionLevel.ALWAYS_ALLOW,
            Capability.DATABASE_ACCESS: PermissionLevel.ALWAYS_ALLOW,
            Capability.WEB_SCRAPING: PermissionLevel.ALWAYS_ALLOW
        }
        
        self.initialize_policies()
    
    def initialize_policies(self):
        """Initialize default policies in memory"""
        for capability in Capability:
            current_policy = memory.get_permission(capability.value)
            if not current_policy:
                memory.save_permission(capability.value, self.default_policies[capability].value)
                logger.info(f"Initialized {capability.value} with policy: {self.default_policies[capability].value}")
    
    def get_policy(self, capability: Capability) -> PermissionLevel:
        """Get current policy for a capability"""
        policy_str = memory.get_permission(capability.value)
        try:
            return PermissionLevel(policy_str)
        except ValueError:
            # Fallback to default
            default_policy = self.default_policies[capability]
            memory.save_permission(capability.value, default_policy.value)
            return default_policy
    
    def set_policy(self, capability: Capability, policy: PermissionLevel):
        """Set policy for a capability"""
        memory.save_permission(capability.value, policy.value)
        logger.info(f"Updated {capability.value} policy to: {policy.value}")
    
    def check_permission(self, capability: Capability, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Check if an action is permitted"""
        policy = self.get_policy(capability)
        context = context or {}
        
        if policy == PermissionLevel.ALWAYS_DENY:
            return False, f"Action {capability.value} is permanently denied"
        
        if policy == PermissionLevel.ALWAYS_ALLOW:
            return True, f"Action {capability.value} is always allowed"
        
        if policy == PermissionLevel.TRUSTED_ONCE:
            # Check if this specific action was previously approved
            action_hash = self._get_action_hash(capability, context)
            if self._was_action_approved(action_hash):
                return True, f"Action {capability.value} was previously approved"
            else:
                return False, f"Action {capability.value} requires approval"
        
        # Default: ASK_EVERY_TIME
        return False, f"Action {capability.value} requires approval"
    
    def _get_action_hash(self, capability: Capability, context: Dict[str, Any]) -> str:
        """Generate a hash for the specific action context"""
        import hashlib
        context_str = f"{capability.value}:{str(sorted(context.items()))}"
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def _was_action_approved(self, action_hash: str) -> bool:
        """Check if an action was previously approved (simplified implementation)"""
        # In a real implementation, this would check a database of approved actions
        # For now, return False to always ask for approval
        return False
    
    def get_dangerous_action_info(self, capability: Capability) -> Dict[str, Any]:
        """Get information about a dangerous action"""
        if capability in self.dangerous_actions:
            return self.dangerous_actions[capability]
        return {
            "description": "Unknown capability",
            "risk_level": "unknown",
            "examples": []
        }
    
    def get_all_policies(self) -> Dict[str, str]:
        """Get all current policies"""
        policies = {}
        for capability in Capability:
            policies[capability.value] = memory.get_permission(capability.value)
        return policies
    
    def reset_to_defaults(self):
        """Reset all policies to default values"""
        for capability in Capability:
            default_policy = self.default_policies[capability]
            memory.save_permission(capability.value, default_policy.value)
        logger.info("Reset all policies to default values")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate a security report"""
        policies = self.get_all_policies()
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        
        for capability, policy in policies.items():
            if policy == PermissionLevel.ALWAYS_ALLOW:
                risk_level = self.dangerous_actions.get(Capability(capability), {}).get("risk_level", "unknown")
                if risk_level == "high":
                    high_risk_count += 1
                elif risk_level == "medium":
                    medium_risk_count += 1
                elif risk_level == "low":
                    low_risk_count += 1
        
        return {
            "total_capabilities": len(Capability),
            "high_risk_always_allowed": high_risk_count,
            "medium_risk_always_allowed": medium_risk_count,
            "low_risk_always_allowed": low_risk_count,
            "policies": policies,
            "recommendations": self._generate_recommendations(policies)
        }
    
    def _generate_recommendations(self, policies: Dict[str, str]) -> List[str]:
        """Generate security recommendations based on current policies"""
        recommendations = []
        
        for capability, policy in policies.items():
            if policy == PermissionLevel.ALWAYS_ALLOW:
                risk_info = self.dangerous_actions.get(Capability(capability), {})
                risk_level = risk_info.get("risk_level", "unknown")
                
                if risk_level in ["high", "medium"]:
                    recommendations.append(
                        f"Consider restricting {capability} from 'always-allow' to 'ask-every-time' "
                        f"due to {risk_level} risk level"
                    )
        
        if not recommendations:
            recommendations.append("Current security policies are well-configured")
        
        return recommendations

class PermissionRequest:
    """Represents a permission request for a dangerous action"""
    
    def __init__(self, capability: Capability, context: Dict[str, Any], user: str = "default"):
        self.capability = capability
        self.context = context
        self.user = user
        self.timestamp = None
        self.approved = False
        self.reason = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "capability": self.capability.value,
            "context": self.context,
            "user": self.user,
            "timestamp": self.timestamp,
            "approved": self.approved,
            "reason": self.reason
        }

# Global permission manager instance
permission_manager = PermissionManager()