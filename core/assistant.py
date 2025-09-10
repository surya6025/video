"""
Main assistant orchestrator for JarvisX
Manages conversations, skill execution, and user interactions
"""

import importlib
import traceback
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime
from .models import llm_manager
from .memory import memory
from .router import skill_router
from .permissions import permission_manager, Capability
from .logging_utils import get_logger, log_action
from .io import FileManager

logger = get_logger(__name__)

class JarvisXAssistant:
    """Main assistant orchestrator"""
    
    def __init__(self):
        self.current_profile_id = None
        self.current_conversation_id = None
        self.file_manager = FileManager()
        self.skills_cache = {}
        self.conversation_context = {}
        
        # Initialize default profile and conversation
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize user session with default profile and conversation"""
        try:
            # Create or get default profile
            profile_data = {
                "name": "Default User",
                "preferences": {
                    "theme": "light",
                    "language": "en",
                    "notifications": True
                }
            }
            
            self.current_profile_id = memory.create_profile(profile_data)
            
            # Create initial conversation
            self.current_conversation_id = memory.create_conversation(
                "Welcome to JarvisX", 
                self.current_profile_id
            )
            
            # Add welcome message
            welcome_msg = (
                "Hello! I'm JarvisX, your advanced AI assistant. "
                "I can help you with:\n\n"
                "• **NLP**: Text processing, summarization, project planning\n"
                "• **ML**: Model training, evaluation, predictions\n"
                "• **Data Science**: EDA, visualization, insights\n"
                "• **Data Engineering**: ETL pipelines, data processing\n"
                "• **Analytics**: SQL queries, dashboards, reports\n"
                "• **Automation**: Workflows, batch operations\n"
                "• **Cybersecurity**: Security scanning, analysis\n"
                "• **System Control**: App launching, file operations\n"
                "• **Web Search**: Information retrieval, scraping\n"
                "• **UI/UX**: Interface design, usability review\n\n"
                "What would you like to work on today?"
            )
            
            memory.add_message(
                self.current_conversation_id,
                "assistant",
                welcome_msg,
                {"type": "welcome", "timestamp": datetime.utcnow().isoformat()}
            )
            
            logger.info(f"Initialized session with profile {self.current_profile_id} and conversation {self.current_conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            # Create minimal session
            self.current_profile_id = "default_profile"
            self.current_conversation_id = "default_conversation"
    
    def process_user_message(self, message: str, context: Dict[str, Any] = None) -> Generator[Dict[str, Any], None, None]:
        """Process a user message and generate response"""
        try:
            # Add user message to memory
            user_msg_id = memory.add_message(
                self.current_conversation_id,
                "user",
                message,
                context or {}
            )
            
            # Update conversation context
            self.conversation_context.update(context or {})
            self.conversation_context["current_message"] = message
            self.conversation_context["user_message_id"] = user_msg_id
            
            # Route to appropriate skill
            skill_name, confidence, method, skill_class_path = skill_router.route_query(
                message, 
                self.conversation_context
            )
            
            # Check if we need to ask for clarification
            if confidence < 0.5:
                clarification_response = self._ask_clarification(message, skill_name, confidence)
                yield {
                    "type": "clarification",
                    "content": clarification_response,
                    "skill": skill_name,
                    "confidence": confidence,
                    "method": method
                }
                return
            
            # Execute skill
            skill_result = self._execute_skill(skill_name, message, self.conversation_context)
            
            if skill_result:
                # Add assistant response to memory
                assistant_msg_id = memory.add_message(
                    self.current_conversation_id,
                    "assistant",
                    skill_result.get("content", "Task completed"),
                    {
                        "skill": skill_name,
                        "result_type": skill_result.get("type", "text"),
                        "artifacts": skill_result.get("artifacts", []),
                        "confidence": confidence,
                        "method": method
                    }
                )
                
                # Log the action
                log_action(
                    action=f"skill_execution_{skill_name}",
                    user=self.current_profile_id,
                    parameters={
                        "message": message,
                        "skill": skill_name,
                        "confidence": confidence,
                        "method": method
                    },
                    result=f"Generated {skill_result.get('type', 'text')} response",
                    success=True
                )
                
                # Yield the result
                yield {
                    "type": "skill_result",
                    "skill": skill_name,
                    "confidence": confidence,
                    "method": method,
                    "result": skill_result,
                    "message_id": assistant_msg_id
                }
            else:
                # Fallback to general conversation
                fallback_response = self._generate_fallback_response(message)
                
                assistant_msg_id = memory.add_message(
                    self.current_conversation_id,
                    "assistant",
                    fallback_response,
                    {"type": "fallback", "skill": "general"}
                )
                
                yield {
                    "type": "fallback",
                    "content": fallback_response,
                    "message_id": assistant_msg_id
                }
                
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            error_response = f"I encountered an error while processing your request: {str(e)}"
            
            # Log the error
            log_action(
                action="error_processing_message",
                user=self.current_profile_id,
                parameters={"message": message, "error": str(e)},
                result=error_response,
                success=False
            )
            
            yield {
                "type": "error",
                "content": error_response,
                "error": str(e)
            }
    
    def _execute_skill(self, skill_name: str, message: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a specific skill"""
        try:
            # Get skill instance
            skill_instance = self._get_skill_instance(skill_name)
            if not skill_instance:
                logger.error(f"Could not instantiate skill: {skill_name}")
                return None
            
            # Check permissions if needed
            if hasattr(skill_instance, 'requires_permission'):
                capability = skill_instance.requires_permission
                is_permitted, reason = permission_manager.check_permission(capability, context)
                
                if not is_permitted:
                    logger.warning(f"Permission denied for {skill_name}: {reason}")
                    return {
                        "type": "permission_denied",
                        "content": f"Permission denied: {reason}",
                        "capability": capability.value,
                        "requires_approval": True
                    }
            
            # Execute the skill
            logger.info(f"Executing skill: {skill_name}")
            result = skill_instance.run(message, context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing skill {skill_name}: {e}")
            logger.error(traceback.format_exc())
            return {
                "type": "error",
                "content": f"Error executing {skill_name}: {str(e)}",
                "error": str(e)
            }
    
    def _get_skill_instance(self, skill_name: str):
        """Get or create skill instance"""
        if skill_name in self.skills_cache:
            return self.skills_cache[skill_name]
        
        try:
            # Import skill module
            skill_class_path = skill_router.skill_mappings.get(skill_name)
            if not skill_class_path:
                logger.error(f"No skill mapping found for: {skill_name}")
                return None
            
            module_path, class_name = skill_class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            skill_class = getattr(module, class_name)
            
            # Create instance
            skill_instance = skill_class()
            self.skills_cache[skill_name] = skill_instance
            
            logger.info(f"Created skill instance for: {skill_name}")
            return skill_instance
            
        except Exception as e:
            logger.error(f"Failed to create skill instance for {skill_name}: {e}")
            return None
    
    def _ask_clarification(self, message: str, skill_name: str, confidence: float) -> str:
        """Ask user for clarification when intent is unclear"""
        skill_info = skill_router.get_skill_info(skill_name)
        
        clarification = (
            f"I think you want to use the **{skill_info['name']}** skill "
            f"(confidence: {confidence:.1%}), but I'm not entirely sure.\n\n"
            f"Could you please clarify what you'd like me to do?\n\n"
            f"**{skill_info['name']}** can help with:\n"
        )
        
        for capability in skill_info['capabilities'][:3]:  # Show first 3 capabilities
            clarification += f"• {capability}\n"
        
        clarification += f"\nOr if you meant something else, please rephrase your request."
        
        return clarification
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate a fallback response when no skill matches"""
        try:
            # Use LLM to generate a helpful response
            prompt = f"""
            The user said: "{message}"
            
            I couldn't determine which specific skill to use for this request. 
            Please provide a helpful response that:
            1. Acknowledges their request
            2. Suggests how they might rephrase it
            3. Lists some examples of what I can help with
            
            Keep the response friendly and helpful.
            """
            
            response = llm_manager.generate(prompt, context="You are JarvisX, a helpful AI assistant.")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate fallback response: {e}")
            return (
                f"I'm not sure how to help with that specific request. "
                f"Could you try rephrasing it? For example:\n\n"
                f"• \"Create a project plan for a web app\"\n"
                f"• \"Train a model on my data\"\n"
                f"• \"Analyze this CSV file\"\n"
                f"• \"Open Chrome browser\"\n\n"
                f"What would you like to work on?"
            )
    
    def get_conversation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history"""
        if self.current_conversation_id:
            return memory.get_messages(self.current_conversation_id, limit)
        return []
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get current conversation context"""
        return self.conversation_context.copy()
    
    def update_conversation_context(self, updates: Dict[str, Any]):
        """Update conversation context"""
        self.conversation_context.update(updates)
    
    def get_available_skills(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available skills"""
        return skill_router.get_all_skills_info()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information"""
        return {
            "llm_status": llm_manager.get_status(),
            "memory_status": memory.get_status(),
            "permissions_status": permission_manager.get_security_report(),
            "current_profile": self.current_profile_id,
            "current_conversation": self.current_conversation_id,
            "skills_available": len(skill_router.get_available_skills()),
            "skills_cache_size": len(self.skills_cache)
        }
    
    def reset_conversation(self):
        """Start a new conversation"""
        try:
            # Create new conversation
            self.current_conversation_id = memory.create_conversation(
                "New Conversation", 
                self.current_profile_id
            )
            
            # Clear context
            self.conversation_context = {}
            
            # Add welcome message
            welcome_msg = "Started a new conversation. How can I help you?"
            memory.add_message(
                self.current_conversation_id,
                "assistant",
                welcome_msg,
                {"type": "new_conversation", "timestamp": datetime.utcnow().isoformat()}
            )
            
            logger.info(f"Started new conversation: {self.current_conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to reset conversation: {e}")
    
    def load_conversation(self, conversation_id: str):
        """Load a specific conversation"""
        try:
            conversation = memory.get_conversation(conversation_id)
            if conversation:
                self.current_conversation_id = conversation_id
                # Load messages to rebuild context
                messages = memory.get_messages(conversation_id, limit=10)
                self.conversation_context = {
                    "conversation_id": conversation_id,
                    "conversation_title": conversation.get("title", "Unknown"),
                    "recent_messages": messages
                }
                logger.info(f"Loaded conversation: {conversation_id}")
            else:
                logger.warning(f"Conversation not found: {conversation_id}")
                
        except Exception as e:
            logger.error(f"Failed to load conversation {conversation_id}: {e}")

# Global assistant instance
assistant = JarvisXAssistant()