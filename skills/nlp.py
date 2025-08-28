"""
NLP Skill for JarvisX
Text processing, summarization, and project planning
"""

import re
from typing import Dict, Any, List, Optional
from skills.base_skill import BaseSkill
from core.models import llm_manager
from core.io import file_manager

class NLPSkill(BaseSkill):
    """Natural Language Processing skill"""
    
    def __init__(self):
        super().__init__()
        self.name = "NLP"
        self.description = "Text summarization, rewriting, project planning, and requirement extraction"
        self.capabilities = [
            "Text Summarization",
            "Content Rewriting", 
            "Project Planning",
            "Requirement Extraction",
            "Translation Assistance",
            "Text Analysis"
        ]
        self.requires_permission = None  # No special permissions needed
    
    def run(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute NLP operations"""
        try:
            # Validate input
            if not self.validate_input(query, context):
                return self.handle_error(ValueError("Invalid input"), context)
            
            # Preprocess query
            processed_query = self.preprocess_query(query)
            
            # Determine operation type
            if self._is_summarization_request(processed_query):
                return self._summarize_text(processed_query, context)
            elif self._is_rewriting_request(processed_query):
                return self._rewrite_text(processed_query, context)
            elif self._is_project_planning_request(processed_query):
                return self._create_project_plan(processed_query, context)
            elif self._is_requirement_extraction_request(processed_query):
                return self._extract_requirements(processed_query, context)
            elif self._is_translation_request(processed_query):
                return self._translate_text(processed_query, context)
            else:
                return self._general_text_analysis(processed_query, context)
                
        except Exception as e:
            return self.handle_error(e, context)
    
    def _is_summarization_request(self, query: str) -> bool:
        """Check if this is a summarization request"""
        keywords = ["summarize", "summary", "summarize", "brief", "overview", "tl;dr"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_rewriting_request(self, query: str) -> bool:
        """Check if this is a rewriting request"""
        keywords = ["rewrite", "rephrase", "paraphrase", "restate", "reword"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_project_planning_request(self, query: str) -> bool:
        """Check if this is a project planning request"""
        keywords = ["project plan", "plan", "roadmap", "timeline", "milestones", "deliverables"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_requirement_extraction_request(self, query: str) -> bool:
        """Check if this is a requirement extraction request"""
        keywords = ["requirements", "specifications", "features", "user stories", "acceptance criteria"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_translation_request(self, query: str) -> bool:
        """Check if this is a translation request"""
        keywords = ["translate", "translation", "language", "spanish", "french", "german"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _summarize_text(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize text content"""
        try:
            # Extract text to summarize from context or query
            text_to_summarize = self._extract_text_from_context(context, query)
            
            if not text_to_summarize:
                return {
                    "type": "text",
                    "content": "Please provide text to summarize or upload a file.",
                    "artifacts": [],
                    "metadata": {"operation": "summarization"}
                }
            
            # Generate summary using LLM
            prompt = f"""
            Please provide a concise summary of the following text. 
            Focus on the key points and main ideas.
            
            Text to summarize:
            {text_to_summarize}
            
            Summary:
            """
            
            summary = llm_manager.generate(prompt, context="You are a helpful text summarization assistant.")
            
            return {
                "type": "text",
                "content": f"**Summary**\n\n{summary}",
                "artifacts": [],
                "metadata": {
                    "operation": "summarization",
                    "original_length": len(text_to_summarize),
                    "summary_length": len(summary)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _rewrite_text(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rewrite text content"""
        try:
            # Extract text to rewrite from context or query
            text_to_rewrite = self._extract_text_from_context(context, query)
            
            if not text_to_rewrite:
                return {
                    "type": "text",
                    "content": "Please provide text to rewrite or upload a file.",
                    "artifacts": [],
                    "metadata": {"operation": "rewriting"}
                }
            
            # Determine rewrite style from query
            style = "professional"
            if "casual" in query.lower():
                style = "casual"
            elif "formal" in query.lower():
                style = "formal"
            elif "simple" in query.lower():
                style = "simple"
            
            # Generate rewritten text using LLM
            prompt = f"""
            Please rewrite the following text in a {style} style while maintaining the same meaning:
            
            Original text:
            {text_to_rewrite}
            
            Rewritten text ({style} style):
            """
            
            rewritten_text = llm_manager.generate(prompt, context="You are a helpful text rewriting assistant.")
            
            return {
                "type": "text",
                "content": f"**Rewritten Text ({style.title()} style)**\n\n{rewritten_text}",
                "artifacts": [],
                "metadata": {
                    "operation": "rewriting",
                    "style": style,
                    "original_length": len(text_to_rewrite),
                    "rewritten_length": len(rewritten_text)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _create_project_plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a project plan"""
        try:
            # Extract project details from query
            project_type = self._extract_project_type(query)
            
            # Generate project plan using LLM
            prompt = f"""
            Create a comprehensive project plan for: {query}
            
            Please include:
            1. Project Overview
            2. Objectives and Goals
            3. Key Deliverables
            4. Timeline and Milestones
            5. Required Resources
            6. Risk Assessment
            7. Success Criteria
            
            Format the response in a clear, structured manner.
            """
            
            project_plan = llm_manager.generate(prompt, context="You are an expert project manager and planner.")
            
            # Save project plan to file
            plan_filename = f"project_plan_{project_type.lower().replace(' ', '_')}.md"
            plan_path = file_manager.create_temp_file(extension=".md", prefix="project_plan_")
            file_manager.save_file(project_plan, str(plan_path))
            
            return {
                "type": "text",
                "content": f"**Project Plan Generated**\n\n{project_plan}",
                "artifacts": [str(plan_path)],
                "metadata": {
                    "operation": "project_planning",
                    "project_type": project_type,
                    "plan_file": str(plan_path)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _extract_requirements(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract requirements from text"""
        try:
            # Extract text to analyze from context or query
            text_to_analyze = self._extract_text_from_context(context, query)
            
            if not text_to_analyze:
                return {
                    "type": "text",
                    "content": "Please provide text to analyze for requirements or upload a file.",
                    "artifacts": [],
                    "metadata": {"operation": "requirement_extraction"}
                }
            
            # Generate requirements using LLM
            prompt = f"""
            Analyze the following text and extract requirements, features, and specifications:
            
            Text to analyze:
            {text_to_analyze}
            
            Please organize the requirements into:
            1. Functional Requirements
            2. Non-Functional Requirements
            3. User Stories
            4. Acceptance Criteria
            
            Format the response clearly and structure it well.
            """
            
            requirements = llm_manager.generate(prompt, context="You are an expert requirements analyst.")
            
            # Save requirements to file
            req_filename = f"requirements_analysis.md"
            req_path = file_manager.create_temp_file(extension=".md", prefix="requirements_")
            file_manager.save_file(requirements, str(req_path))
            
            return {
                "type": "text",
                "content": f"**Requirements Analysis**\n\n{requirements}",
                "artifacts": [str(req_path)],
                "metadata": {
                    "operation": "requirement_extraction",
                    "requirements_file": str(req_path)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _translate_text(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Translate text to another language"""
        try:
            # Extract text to translate from context or query
            text_to_translate = self._extract_text_from_context(context, query)
            
            if not text_to_translate:
                return {
                    "type": "text",
                    "content": "Please provide text to translate or upload a file.",
                    "artifacts": [],
                    "metadata": {"operation": "translation"}
                }
            
            # Determine target language from query
            target_language = self._extract_target_language(query)
            
            # Generate translation using LLM
            prompt = f"""
            Translate the following text to {target_language}:
            
            Original text:
            {text_to_translate}
            
            Translation to {target_language}:
            """
            
            translation = llm_manager.generate(prompt, context=f"You are a professional translator to {target_language}.")
            
            return {
                "type": "text",
                "content": f"**Translation to {target_language}**\n\n{translation}",
                "artifacts": [],
                "metadata": {
                    "operation": "translation",
                    "target_language": target_language,
                    "original_length": len(text_to_translate),
                    "translation_length": len(translation)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _general_text_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform general text analysis"""
        try:
            # Extract text to analyze from context or query
            text_to_analyze = self._extract_text_from_context(context, query)
            
            if not text_to_analyze:
                return {
                    "type": "text",
                    "content": "Please provide text to analyze or upload a file.",
                    "artifacts": [],
                    "metadata": {"operation": "text_analysis"}
                }
            
            # Generate analysis using LLM
            prompt = f"""
            Analyze the following text and provide insights:
            
            Text to analyze:
            {text_to_analyze}
            
            Please provide:
            1. Key themes and topics
            2. Sentiment analysis
            3. Writing style assessment
            4. Suggestions for improvement
            5. Summary of main points
            """
            
            analysis = llm_manager.generate(prompt, context="You are an expert text analyst and writing consultant.")
            
            return {
                "type": "text",
                "content": f"**Text Analysis**\n\n{analysis}",
                "artifacts": [],
                "metadata": {
                    "operation": "text_analysis",
                    "text_length": len(text_to_analyze)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _extract_text_from_context(self, context: Dict[str, Any], query: str) -> Optional[str]:
        """Extract text content from context or query"""
        # Check if there's uploaded file content
        if "uploaded_files" in context:
            for file_info in context["uploaded_files"]:
                if file_info.get("content"):
                    return file_info["content"]
        
        # Check if there's recent message content
        if "recent_messages" in context:
            for msg in context["recent_messages"]:
                if msg.get("role") == "user" and msg.get("content"):
                    return msg["content"]
        
        # Check if query contains text to process
        if len(query) > 50:  # Assume long queries contain text to process
            return query
        
        return None
    
    def _extract_project_type(self, query: str) -> str:
        """Extract project type from query"""
        # Simple keyword extraction
        if "web" in query.lower() or "website" in query.lower():
            return "Web Application"
        elif "mobile" in query.lower() or "app" in query.lower():
            return "Mobile Application"
        elif "api" in query.lower() or "backend" in query.lower():
            return "API/Backend Service"
        elif "data" in query.lower() or "analytics" in query.lower():
            return "Data Analytics Project"
        else:
            return "General Project"
    
    def _extract_target_language(self, query: str) -> str:
        """Extract target language from query"""
        # Simple language detection
        if "spanish" in query.lower():
            return "Spanish"
        elif "french" in query.lower():
            return "French"
        elif "german" in query.lower():
            return "German"
        elif "chinese" in query.lower():
            return "Chinese"
        elif "japanese" in query.lower():
            return "Japanese"
        else:
            return "Spanish"  # Default
    
    def get_usage_examples(self) -> List[str]:
        """Get example usage queries for this skill"""
        return [
            "Summarize this document for me",
            "Rewrite this text in a more professional tone",
            "Create a project plan for a Flask web application",
            "Extract requirements from this user story",
            "Translate this text to Spanish",
            "Analyze the writing style of this content"
        ]