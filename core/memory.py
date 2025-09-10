"""
Memory management for JarvisX
Supabase integration with local cache fallback
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import hashlib
from supabase import create_client, Client
from .logging_utils import get_logger

logger = get_logger(__name__)

class LocalCache:
    """Local SQLite cache for offline/fallback use"""
    
    def __init__(self, db_path: str = "temp/jarvisx_cache.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    created_at TEXT,
                    data TEXT
                )
            """)
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    started_at TEXT,
                    title TEXT,
                    data TEXT
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    meta TEXT,
                    created_at TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            # Permissions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permissions (
                    id TEXT PRIMARY KEY,
                    capability TEXT,
                    policy TEXT,
                    updated_at TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Local cache database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize local cache: {e}")
    
    def save_profile(self, profile_id: str, data: Dict[str, Any]):
        """Save profile to local cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO profiles (id, created_at, data)
                VALUES (?, ?, ?)
            """, (profile_id, datetime.utcnow().isoformat(), json.dumps(data)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save profile to local cache: {e}")
    
    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get profile from local cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT data FROM profiles WHERE id = ?", (profile_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get profile from local cache: {e}")
            return None
    
    def save_conversation(self, conv_id: str, title: str, data: Dict[str, Any]):
        """Save conversation to local cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO conversations (id, started_at, title, data)
                VALUES (?, ?, ?, ?)
            """, (conv_id, datetime.utcnow().isoformat(), title, json.dumps(data)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save conversation to local cache: {e}")
    
    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation from local cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT data FROM conversations WHERE id = ?", (conv_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get conversation from local cache: {e}")
            return None
    
    def save_message(self, msg_id: str, conv_id: str, role: str, content: str, meta: Dict[str, Any] = None):
        """Save message to local cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO messages (id, conversation_id, role, content, meta, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (msg_id, conv_id, role, content, json.dumps(meta or {}), datetime.utcnow().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save message to local cache: {e}")
    
    def get_messages(self, conv_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages from local cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, role, content, meta, created_at
                FROM messages 
                WHERE conversation_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (conv_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            messages = []
            for row in results:
                messages.append({
                    "id": row[0],
                    "role": row[1],
                    "content": row[2],
                    "meta": json.loads(row[3]) if row[3] else {},
                    "created_at": row[4]
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get messages from local cache: {e}")
            return []
    
    def save_permission(self, perm_id: str, capability: str, policy: str):
        """Save permission to local cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO permissions (id, capability, policy, updated_at)
                VALUES (?, ?, ?, ?)
            """, (perm_id, capability, policy, datetime.utcnow().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save permission to local cache: {e}")
    
    def get_permission(self, capability: str) -> Optional[str]:
        """Get permission policy from local cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT policy FROM permissions WHERE capability = ?", (capability,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return result[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get permission from local cache: {e}")
            return None

class SupabaseMemory:
    """Supabase-powered persistent memory with local cache fallback"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.local_cache = LocalCache()
        self.offline_mode = False
        self.setup_supabase()
    
    def setup_supabase(self):
        """Initialize Supabase client"""
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            
            if supabase_url and supabase_key and supabase_url != "your_supabase_project_url":
                self.supabase = create_client(supabase_url, supabase_key)
                logger.info("Supabase client initialized")
                
                # Test connection
                self.test_connection()
            else:
                logger.warning("Supabase credentials not configured, using offline mode")
                self.offline_mode = True
                
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            self.offline_mode = True
    
    def test_connection(self):
        """Test Supabase connection"""
        try:
            if self.supabase:
                # Try to fetch a simple query
                result = self.supabase.table("profiles").select("id").limit(1).execute()
                logger.info("Supabase connection test successful")
                self.offline_mode = False
        except Exception as e:
            logger.warning(f"Supabase connection test failed: {e}")
            self.offline_mode = True
    
    def create_profile(self, profile_data: Dict[str, Any]) -> str:
        """Create a new user profile"""
        profile_id = hashlib.md5(f"{datetime.utcnow().isoformat()}".encode()).hexdigest()
        
        profile = {
            "id": profile_id,
            "created_at": datetime.utcnow().isoformat(),
            **profile_data
        }
        
        # Save to local cache
        self.local_cache.save_profile(profile_id, profile)
        
        # Try to save to Supabase
        if not self.offline_mode and self.supabase:
            try:
                self.supabase.table("profiles").insert(profile).execute()
                logger.info(f"Profile {profile_id} saved to Supabase")
            except Exception as e:
                logger.warning(f"Failed to save profile to Supabase: {e}")
                self.offline_mode = True
        
        return profile_id
    
    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        # Try Supabase first
        if not self.offline_mode and self.supabase:
            try:
                result = self.supabase.table("profiles").select("*").eq("id", profile_id).execute()
                if result.data:
                    profile = result.data[0]
                    # Update local cache
                    self.local_cache.save_profile(profile_id, profile)
                    return profile
            except Exception as e:
                logger.warning(f"Failed to get profile from Supabase: {e}")
                self.offline_mode = True
        
        # Fallback to local cache
        return self.local_cache.get_profile(profile_id)
    
    def create_conversation(self, title: str, profile_id: str) -> str:
        """Create a new conversation"""
        conv_id = hashlib.md5(f"{datetime.utcnow().isoformat()}{title}".encode()).hexdigest()
        
        conversation = {
            "id": conv_id,
            "started_at": datetime.utcnow().isoformat(),
            "title": title,
            "profile_id": profile_id
        }
        
        # Save to local cache
        self.local_cache.save_conversation(conv_id, title, conversation)
        
        # Try to save to Supabase
        if not self.offline_mode and self.supabase:
            try:
                self.supabase.table("conversations").insert(conversation).execute()
                logger.info(f"Conversation {conv_id} saved to Supabase")
            except Exception as e:
                logger.warning(f"Failed to save conversation to Supabase: {e}")
                self.offline_mode = True
        
        return conv_id
    
    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation"""
        # Try Supabase first
        if not self.offline_mode and self.supabase:
            try:
                result = self.supabase.table("conversations").select("*").eq("id", conv_id).execute()
                if result.data:
                    conversation = result.data[0]
                    # Update local cache
                    self.local_cache.save_conversation(conv_id, conversation["title"], conversation)
                    return conversation
            except Exception as e:
                logger.warning(f"Failed to get conversation from Supabase: {e}")
                self.offline_mode = True
        
        # Fallback to local cache
        return self.local_cache.get_conversation(conv_id)
    
    def add_message(self, conv_id: str, role: str, content: str, meta: Dict[str, Any] = None) -> str:
        """Add a message to a conversation"""
        msg_id = hashlib.md5(f"{datetime.utcnow().isoformat()}{content[:50]}".encode()).hexdigest()
        
        message = {
            "id": msg_id,
            "conversation_id": conv_id,
            "role": role,
            "content": content,
            "meta": meta or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to local cache
        self.local_cache.save_message(msg_id, conv_id, role, content, meta)
        
        # Try to save to Supabase
        if not self.offline_mode and self.supabase:
            try:
                self.supabase.table("messages").insert(message).execute()
                logger.info(f"Message {msg_id} saved to Supabase")
            except Exception as e:
                logger.warning(f"Failed to save message to Supabase: {e}")
                self.offline_mode = True
        
        return msg_id
    
    def get_messages(self, conv_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages from a conversation"""
        # Try Supabase first
        if not self.offline_mode and self.supabase:
            try:
                result = self.supabase.table("messages").select("*").eq("conversation_id", conv_id).order("created_at", desc=False).limit(limit).execute()
                if result.data:
                    messages = result.data
                    # Update local cache
                    for msg in messages:
                        self.local_cache.save_message(
                            msg["id"], conv_id, msg["role"], 
                            msg["content"], msg.get("meta", {})
                        )
                    return messages
            except Exception as e:
                logger.warning(f"Failed to get messages from Supabase: {e}")
                self.offline_mode = True
        
        # Fallback to local cache
        return self.local_cache.get_messages(conv_id, limit)
    
    def get_conversation_history(self, profile_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations for a profile"""
        if not self.offline_mode and self.supabase:
            try:
                result = self.supabase.table("conversations").select("*").eq("profile_id", profile_id).order("started_at", desc=True).limit(limit).execute()
                if result.data:
                    return result.data
            except Exception as e:
                logger.warning(f"Failed to get conversation history from Supabase: {e}")
                self.offline_mode = True
        
        # Fallback: return empty list for now
        return []
    
    def save_permission(self, capability: str, policy: str):
        """Save permission policy"""
        perm_id = hashlib.md5(f"{capability}".encode()).hexdigest()
        
        # Save to local cache
        self.local_cache.save_permission(perm_id, capability, policy)
        
        # Try to save to Supabase
        if not self.offline_mode and self.supabase:
            try:
                permission = {
                    "id": perm_id,
                    "capability": capability,
                    "policy": policy,
                    "updated_at": datetime.utcnow().isoformat()
                }
                self.supabase.table("permissions").upsert(permission).execute()
                logger.info(f"Permission {capability} saved to Supabase")
            except Exception as e:
                logger.warning(f"Failed to save permission to Supabase: {e}")
                self.offline_mode = True
    
    def get_permission(self, capability: str) -> str:
        """Get permission policy for a capability"""
        # Try Supabase first
        if not self.offline_mode and self.supabase:
            try:
                result = self.supabase.table("permissions").select("policy").eq("capability", capability).execute()
                if result.data:
                    policy = result.data[0]["policy"]
                    # Update local cache
                    self.local_cache.save_permission(capability, policy)
                    return policy
            except Exception as e:
                logger.warning(f"Failed to get permission from Supabase: {e}")
                self.offline_mode = True
        
        # Fallback to local cache
        policy = self.local_cache.get_permission(capability)
        if policy is None:
            # Default policy
            policy = "ask-every-time"
            self.save_permission(capability, policy)
        
        return policy
    
    def get_status(self) -> Dict[str, Any]:
        """Get memory system status"""
        return {
            "offline_mode": self.offline_mode,
            "supabase_configured": self.supabase is not None,
            "local_cache_available": True,
            "last_sync": datetime.utcnow().isoformat() if not self.offline_mode else None
        }

# Global memory instance
memory = SupabaseMemory()