# ⚠️ Auto-generated from test: verify before use

"""
Prompt builder for constructing context-aware prompts.
Integrates with memory and intent systems.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

class PromptBuilder:
    """Builds context-aware prompts with memory integration."""
    
    def __init__(self):
        """Initialize prompt builder."""
        self.logger = logging.getLogger(__name__)
    
    def build_messages(
        self,
        message: str,
        context: str,
        memory_context: Optional[str] = None,
        intent: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Build messages for OpenAI API.
        
        Args:
            message: User message
            context: Conversation context
            memory_context: Optional memory context
            intent: Optional conversation intent
            
        Returns:
            List of message dictionaries for OpenAI API
        """
        # Build system message
        system_message = self._build_system_message(intent)
        
        # Build context message
        context_message = self._build_context_message(
            context,
            memory_context
        )
        
        # Build user message
        user_message = self._build_user_message(message)
        
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": context_message},
            {"role": "user", "content": user_message}
        ]
    
    def _build_system_message(self, intent: Optional[str] = None) -> str:
        """Build system message with intent.
        
        Args:
            intent: Optional conversation intent
            
        Returns:
            System message
        """
        base_message = """Du är en hjälpsam AI-assistent som kan:
- Svara på frågor om AI och maskininlärning
- Förklara koncept på ett tydligt sätt
- Ge exempel och analogier
- Anpassa svaret efter användarens nivå"""
        
        if intent:
            base_message += f"\n\nNuvarande syfte: {intent}"
        
        return base_message
    
    def _build_context_message(
        self,
        context: str,
        memory_context: Optional[str] = None
    ) -> str:
        """Build context message with memory.
        
        Args:
            context: Conversation context
            memory_context: Optional memory context
            
        Returns:
            Context message
        """
        context_parts = []
        
        if context:
            context_parts.append(f"Konversationskontext:\n{context}")
        
        if memory_context:
            context_parts.append(f"Relevant minneskontext:\n{memory_context}")
        
        return "\n\n".join(context_parts) if context_parts else ""
    
    def _build_user_message(self, message: str) -> str:
        """Build user message.
        
        Args:
            message: User message
            
        Returns:
            User message
        """
        return f"Användare: {message}"
    
    def format_memories(self, memories: List[str]) -> str:
        """Format memories for prompt.
        
        Args:
            memories: List of memory strings
            
        Returns:
            Formatted memory string
        """
        if not memories:
            return ""
        
        formatted = "Tidigare relevanta interaktioner:\n"
        for i, memory in enumerate(memories, 1):
            formatted += f"{i}. {memory}\n"
        
        return formatted
    
    def inject_context(self, prompt: str, intent: str) -> str:
        """Inject intent context into prompt.
        
        Args:
            prompt: Base prompt
            intent: Conversation intent
            
        Returns:
            Prompt with injected context
        """
        intent_context = {
            "summarization": "Fokusera på att sammanfatta huvudpunkter",
            "explanation": "Förklara konceptet steg för steg",
            "comparison": "Jämför och kontrastera olika aspekter",
            "analysis": "Analysera djupare och ge insikter"
        }
        
        if intent in intent_context:
            return f"{prompt}\n\n{intent_context[intent]}"
        
        return prompt 