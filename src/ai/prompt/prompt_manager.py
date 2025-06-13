"""Prompt manager for handling AI prompts."""

from typing import Dict, List, Optional
import json
from pathlib import Path
import jinja2
from datetime import datetime

class PromptManager:
    """Manages AI prompts and templates."""
    
    def __init__(self, templates_dir: str = "templates/prompts"):
        """Initialize prompt manager."""
        self.templates_dir = Path(templates_dir)
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        self.prompt_history: List[Dict] = []
    
    def load_template(self, template_name: str) -> jinja2.Template:
        """Load a prompt template."""
        try:
            return self.env.get_template(f"{template_name}.j2")
        except Exception as e:
            raise Exception(f"Failed to load template {template_name}: {str(e)}")
    
    def format_prompt(
        self,
        template_name: str,
        context: Optional[Dict] = None,
        memory: Optional[List[Dict]] = None
    ) -> str:
        """Format a prompt using template and context."""
        template = self.load_template(template_name)
        
        # Prepare context
        context = context or {}
        if memory:
            context["memory"] = memory
        
        # Add timestamp
        context["timestamp"] = datetime.now().isoformat()
        
        # Format prompt
        prompt = template.render(**context)
        
        # Log prompt
        self.prompt_history.append({
            "template": template_name,
            "context": context,
            "prompt": prompt,
            "timestamp": context["timestamp"]
        })
        
        return prompt
    
    def get_prompt_history(self, limit: int = 10) -> List[Dict]:
        """Get recent prompt history."""
        return self.prompt_history[-limit:]
    
    def validate_prompt(self, prompt: str) -> bool:
        """Validate prompt format and content."""
        # Check minimum length
        if len(prompt) < 10:
            return False
        
        # Check for required sections
        required_sections = ["context", "instruction"]
        if not all(section in prompt.lower() for section in required_sections):
            return False
        
        # Check for forbidden content
        forbidden_content = ["password", "api_key", "secret"]
        if any(content in prompt.lower() for content in forbidden_content):
            return False
        
        return True
    
    def save_template(self, template_name: str, content: str) -> None:
        """Save a new prompt template."""
        template_path = self.templates_dir / f"{template_name}.j2"
        
        # Validate template syntax
        try:
            self.env.from_string(content)
        except Exception as e:
            raise Exception(f"Invalid template syntax: {str(e)}")
        
        # Save template
        template_path.write_text(content)
    
    def list_templates(self) -> List[str]:
        """List available prompt templates."""
        return [f.stem for f in self.templates_dir.glob("*.j2")] 