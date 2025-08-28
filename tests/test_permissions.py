"""
Tests for the permissions system
"""

import pytest
from unittest.mock import Mock, patch
from core.permissions import PermissionManager, PermissionLevel, Capability

class TestPermissionLevel:
    """Test PermissionLevel enum"""
    
    def test_permission_levels(self):
        """Test all permission levels exist"""
        assert PermissionLevel.ASK_EVERY_TIME == "ask-every-time"
        assert PermissionLevel.TRUSTED_ONCE == "trusted-once"
        assert PermissionLevel.ALWAYS_DENY == "always-deny"
        assert PermissionLevel.ALWAYS_ALLOW == "always-allow"

class TestCapability:
    """Test Capability enum"""
    
    def test_capabilities(self):
        """Test all capabilities exist"""
        assert Capability.FILE_READ == "FILE_READ"
        assert Capability.FILE_WRITE == "FILE_WRITE"
        assert Capability.PROCESS_EXECUTION == "PROCESS_EXECUTION"
        assert Capability.NETWORK_ACCESS == "NETWORK_ACCESS"
        assert Capability.MODEL_TRAINING == "MODEL_TRAINING"
        assert Capability.SYSTEM_CONTROL == "SYSTEM_CONTROL"

class TestPermissionManager:
    """Test the PermissionManager class"""
    
    def test_init(self):
        """Test manager initialization"""
        manager = PermissionManager()
        assert manager is not None
        assert hasattr(manager, 'policies')
    
    def test_set_policy(self):
        """Test setting permission policies"""
        manager = PermissionManager()
        
        # Set policy for user
        manager.set_policy("user123", Capability.FILE_WRITE, PermissionLevel.ASK_EVERY_TIME)
        
        # Verify policy was set
        policy = manager.get_policy("user123", Capability.FILE_WRITE)
        assert policy == PermissionLevel.ASK_EVERY_TIME
    
    def test_get_policy_default(self):
        """Test getting default policy when none set"""
        manager = PermissionManager()
        
        # Get policy for user with no policy set
        policy = manager.get_policy("user123", Capability.FILE_WRITE)
        assert policy == PermissionLevel.ASK_EVERY_TIME  # Default
    
    def test_check_permission_always_allow(self):
        """Test permission check with always-allow policy"""
        manager = PermissionManager()
        
        # Set always-allow policy
        manager.set_policy("user123", Capability.FILE_READ, PermissionLevel.ALWAYS_ALLOW)
        
        # Check permission
        result = manager.check_permission("user123", Capability.FILE_READ)
        assert result is True
    
    def test_check_permission_always_deny(self):
        """Test permission check with always-deny policy"""
        manager = PermissionManager()
        
        # Set always-deny policy
        manager.set_policy("user123", Capability.SYSTEM_CONTROL, PermissionLevel.ALWAYS_DENY)
        
        # Check permission
        result = manager.check_permission("user123", Capability.SYSTEM_CONTROL)
        assert result is False
    
    def test_check_permission_ask_every_time(self):
        """Test permission check with ask-every-time policy"""
        manager = PermissionManager()
        
        # Set ask-every-time policy
        manager.set_policy("user123", Capability.FILE_WRITE, PermissionLevel.ASK_EVERY_TIME)
        
        # Check permission - should return None to indicate user decision needed
        result = manager.check_permission("user123", Capability.FILE_WRITE)
        assert result is None
    
    def test_check_permission_trusted_once(self):
        """Test permission check with trusted-once policy"""
        manager = PermissionManager()
        
        # Set trusted-once policy
        manager.set_policy("user123", Capability.MODEL_TRAINING, PermissionLevel.TRUSTED_ONCE)
        
        # Check permission - should return True for trusted operations
        result = manager.check_permission("user123", Capability.MODEL_TRAINING)
        assert result is True
    
    def test_update_policy(self):
        """Test updating existing policies"""
        manager = PermissionManager()
        
        # Set initial policy
        manager.set_policy("user123", Capability.FILE_WRITE, PermissionLevel.ASK_EVERY_TIME)
        
        # Update policy
        manager.update_policy("user123", Capability.FILE_WRITE, PermissionLevel.ALWAYS_ALLOW)
        
        # Verify update
        policy = manager.get_policy("user123", Capability.FILE_WRITE)
        assert policy == PermissionLevel.ALWAYS_ALLOW
    
    def test_remove_policy(self):
        """Test removing policies"""
        manager = PermissionManager()
        
        # Set policy
        manager.set_policy("user123", Capability.FILE_WRITE, PermissionLevel.ALWAYS_ALLOW)
        
        # Remove policy
        manager.remove_policy("user123", Capability.FILE_WRITE)
        
        # Verify removal - should return default
        policy = manager.get_policy("user123", Capability.FILE_WRITE)
        assert policy == PermissionLevel.ASK_EVERY_TIME
    
    def test_get_user_policies(self):
        """Test getting all policies for a user"""
        manager = PermissionManager()
        
        # Set multiple policies
        manager.set_policy("user123", Capability.FILE_READ, PermissionLevel.ALWAYS_ALLOW)
        manager.set_policy("user123", Capability.FILE_WRITE, PermissionLevel.ASK_EVERY_TIME)
        manager.set_policy("user123", Capability.MODEL_TRAINING, PermissionLevel.TRUSTED_ONCE)
        
        # Get all policies
        policies = manager.get_user_policies("user123")
        
        assert len(policies) == 3
        assert policies[Capability.FILE_READ] == PermissionLevel.ALWAYS_ALLOW
        assert policies[Capability.FILE_WRITE] == PermissionLevel.ASK_EVERY_TIME
        assert policies[Capability.MODEL_TRAINING] == PermissionLevel.TRUSTED_ONCE
    
    def test_get_capability_policies(self):
        """Test getting all policies for a capability"""
        manager = PermissionManager()
        
        # Set policies for multiple users
        manager.set_policy("user123", Capability.FILE_WRITE, PermissionLevel.ALWAYS_ALLOW)
        manager.set_policy("user456", Capability.FILE_WRITE, PermissionLevel.ASK_EVERY_TIME)
        manager.set_policy("user789", Capability.FILE_WRITE, PermissionLevel.ALWAYS_DENY)
        
        # Get all policies for capability
        policies = manager.get_capability_policies(Capability.FILE_WRITE)
        
        assert len(policies) == 3
        assert policies["user123"] == PermissionLevel.ALWAYS_ALLOW
        assert policies["user456"] == PermissionLevel.ASK_EVERY_TIME
        assert policies["user789"] == PermissionLevel.ALWAYS_DENY
    
    def test_generate_security_report(self):
        """Test security report generation"""
        manager = PermissionManager()
        
        # Set some policies
        manager.set_policy("user123", Capability.FILE_WRITE, PermissionLevel.ALWAYS_ALLOW)
        manager.set_policy("user456", Capability.SYSTEM_CONTROL, PermissionLevel.ALWAYS_DENY)
        
        # Generate report
        report = manager.generate_security_report()
        
        assert "user123" in report
        assert "user456" in report
        assert "FILE_WRITE" in report
        assert "SYSTEM_CONTROL" in report
    
    def test_bulk_policy_operations(self):
        """Test bulk policy operations"""
        manager = PermissionManager()
        
        # Set multiple policies at once
        policies = {
            Capability.FILE_READ: PermissionLevel.ALWAYS_ALLOW,
            Capability.FILE_WRITE: PermissionLevel.ASK_EVERY_TIME,
            Capability.MODEL_TRAINING: PermissionLevel.TRUSTED_ONCE
        }
        
        manager.set_bulk_policies("user123", policies)
        
        # Verify all policies were set
        for capability, level in policies.items():
            assert manager.get_policy("user123", capability) == level
    
    def test_policy_validation(self):
        """Test policy validation"""
        manager = PermissionManager()
        
        # Test invalid permission level
        with pytest.raises(ValueError):
            manager.set_policy("user123", Capability.FILE_READ, "invalid-level")
        
        # Test invalid capability
        with pytest.raises(ValueError):
            manager.set_policy("user123", "INVALID_CAPABILITY", PermissionLevel.ALWAYS_ALLOW)