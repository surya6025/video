"""
LLM models integration for JarvisX
Supports Ollama (local) and optional cloud LLMs
"""

import os
import json
import requests
from typing import Dict, List, Optional, Generator, Any
from abc import ABC, abstractmethod
import time
from .logging_utils import get_logger

logger = get_logger(__name__)

class BaseLLM(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, context: str = "", **kwargs) -> str:
        """Generate text response"""
        pass
    
    @abstractmethod
    def stream_generate(self, prompt: str, context: str = "", **kwargs) -> Generator[str, None, None]:
        """Stream text response"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available"""
        pass

class OllamaLLM(BaseLLM):
    """Ollama local LLM integration"""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3"):
        self.host = host.rstrip('/')
        self.model = model
        self.api_url = f"{self.host}/api"
        logger.info(f"Initialized Ollama LLM with host: {host}, model: {model}")
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model["name"] == self.model for model in models)
            return False
        except Exception as e:
            logger.warning(f"Ollama availability check failed: {e}")
            return False
    
    def generate(self, prompt: str, context: str = "", **kwargs) -> str:
        """Generate complete response"""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "max_tokens": kwargs.get("max_tokens", 2048)
                }
            }
            
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def stream_generate(self, prompt: str, context: str = "", **kwargs) -> Generator[str, None, None]:
        """Stream response token by token"""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "max_tokens": kwargs.get("max_tokens", 2048)
                }
            }
            
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=60,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'response' in data:
                                yield data['response']
                        except json.JSONDecodeError:
                            continue
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                logger.error(error_msg)
                yield error_msg
                
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            yield f"Error streaming response: {str(e)}"

class OpenAILLM(BaseLLM):
    """OpenAI API integration (optional)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        logger.info("Initialized OpenAI LLM")
    
    def is_available(self) -> bool:
        """Check if OpenAI API key is valid"""
        return bool(self.api_key and self.api_key != "your_openai_api_key")
    
    def generate(self, prompt: str, context: str = "", **kwargs) -> str:
        """Generate complete response using OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": kwargs.get("model", "gpt-3.5-turbo"),
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048)
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def stream_generate(self, prompt: str, context: str = "", **kwargs) -> Generator[str, None, None]:
        """Stream response using OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": kwargs.get("model", "gpt-3.5-turbo"),
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
                "stream": True
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            line = line.decode('utf-8')
                            if line.startswith('data: '):
                                data = line[6:]
                                if data == '[DONE]':
                                    break
                                try:
                                    json_data = json.loads(data)
                                    if 'choices' in json_data and len(json_data['choices']) > 0:
                                        delta = json_data['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            yield delta['content']
                                except json.JSONDecodeError:
                                    continue
                        except Exception as e:
                            logger.warning(f"Error parsing streaming response: {e}")
                            continue
            else:
                error_msg = f"OpenAI API error: {response.status_code}"
                logger.error(error_msg)
                yield error_msg
                
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            yield f"Error streaming response: {str(e)}"

class LLMManager:
    """Manages multiple LLM providers with fallback"""
    
    def __init__(self):
        self.providers: List[BaseLLM] = []
        self.current_provider: Optional[BaseLLM] = None
        self.setup_providers()
    
    def setup_providers(self):
        """Initialize available LLM providers"""
        # Try Ollama first (local)
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        
        ollama = OllamaLLM(ollama_host, ollama_model)
        if ollama.is_available():
            self.providers.append(ollama)
            self.current_provider = ollama
            logger.info("Ollama LLM provider initialized and set as primary")
        
        # Try OpenAI as fallback
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key":
            openai = OpenAILLM(openai_key)
            if openai.is_available():
                self.providers.append(openai)
                if not self.current_provider:
                    self.current_provider = openai
                logger.info("OpenAI LLM provider initialized")
        
        if not self.providers:
            logger.warning("No LLM providers available!")
    
    def get_provider(self) -> Optional[BaseLLM]:
        """Get the current active LLM provider"""
        return self.current_provider
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different LLM provider"""
        for provider in self.providers:
            if provider.__class__.__name__.lower().startswith(provider_name.lower()):
                self.current_provider = provider
                logger.info(f"Switched to {provider.__class__.__name__} provider")
                return True
        return False
    
    def generate(self, prompt: str, context: str = "", **kwargs) -> str:
        """Generate response using current provider"""
        if not self.current_provider:
            return "Error: No LLM provider available"
        
        return self.current_provider.generate(prompt, context, **kwargs)
    
    def stream_generate(self, prompt: str, context: str = "", **kwargs) -> Generator[str, None, None]:
        """Stream response using current provider"""
        if not self.current_provider:
            yield "Error: No LLM provider available"
            return
        
        yield from self.current_provider.stream_generate(prompt, context, **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {
            "current_provider": self.current_provider.__class__.__name__ if self.current_provider else None,
            "available_providers": [],
            "total_providers": len(self.providers)
        }
        
        for provider in self.providers:
            status["available_providers"].append({
                "name": provider.__class__.__name__,
                "available": provider.is_available(),
                "is_current": provider == self.current_provider
            })
        
        return status

# Global LLM manager instance
llm_manager = LLMManager()