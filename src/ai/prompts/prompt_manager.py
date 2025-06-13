"""
Prompt manager implementation for Geometra AI.
Handles prompt templates and context management.
"""

from typing import Dict, Optional
import os
import yaml
from jinja2 import Environment, FileSystemLoader

class PromptManager:
    """Prompt manager for Geometra AI."""
    
    def __init__(self, config_path: str = "src/ai/config.yaml"):
        """Initialize prompt manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.env = Environment(
            loader=FileSystemLoader("src/ai/prompts/templates")
        )
        self.config = self._load_config(config_path)
        self.templates = self._load_templates()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    def _load_templates(self) -> Dict:
        """Load prompt templates.
        
        Returns:
            Dictionary of templates
        """
        return {
            "system": self.env.get_template("system.txt"),
            "user": self.env.get_template("user.txt"),
            "assistant": self.env.get_template("assistant.txt")
        }
    
    def get_prompt(
        self,
        template_name: str,
        context: Optional[Dict] = None
    ) -> str:
        """Get rendered prompt from template.
        
        Args:
            template_name: Name of template to use
            context: Optional context dictionary
            
        Returns:
            Rendered prompt string
        """
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        return template.render(**(context or {}))
    
    def get_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Get system prompt.
        
        Args:
            context: Optional context dictionary
            
        Returns:
            System prompt string
        """
        return self.get_prompt("system", context)
    
    def get_user_prompt(
        self,
        message: str,
        context: Optional[Dict] = None
    ) -> str:
        """Get user prompt.
        
        Args:
            message: User message
            context: Optional context dictionary
            
        Returns:
            User prompt string
        """
        context = context or {}
        context["message"] = message
        return self.get_prompt("user", context)
    
    def get_assistant_prompt(
        self,
        response: str,
        context: Optional[Dict] = None
    ) -> str:
        """Get assistant prompt.
        
        Args:
            response: Assistant response
            context: Optional context dictionary
            
        Returns:
            Assistant prompt string
        """
        context = context or {}
        context["response"] = response
        return self.get_prompt("assistant", context)
    
    def get_chat_context(
        self,
        user_id: str,
        message: str,
        memory: Optional[Dict] = None
    ) -> Dict:
        """Get chat context.
        
        Args:
            user_id: User identifier
            message: User message
            memory: Optional memory dictionary
            
        Returns:
            Chat context dictionary
        """
        return {
            "user_id": user_id,
            "message": message,
            "memory": memory or {},
            "config": self.config
        } 