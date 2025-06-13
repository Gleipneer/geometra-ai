#!/usr/bin/env python3
"""
Chat Engine Module

This module serves as the main interface for chat interactions,
integrating with the model router for intelligent model selection
and handling chat context and memory.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from .model_router import get_completion
from .prompt_builder import PromptBuilder
from memory.memory_manager import MemoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/chat_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChatEngine:
    """
    Main chat engine class that handles chat interactions and model routing.
    """
    
    def __init__(self, memory_manager=None, prompt_builder=None):
        """Initialize the chat engine with required components."""
        self.memory_manager = memory_manager or MemoryManager()
        self.prompt_builder = prompt_builder or PromptBuilder()
        
    def detect_intent(self, prompt: str) -> str:
        """
        Detect the intent of the user's prompt.
        
        Args:
            prompt (str): The user's input prompt
            
        Returns:
            str: The detected intent (e.g., 'summarization', 'troubleshooting')
        """
        # Simple keyword-based intent detection
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['summarize', 'summary', 'overview']):
            return 'summarization'
        elif any(word in prompt_lower for word in ['fix', 'error', 'problem', 'issue']):
            return 'troubleshooting'
        elif any(word in prompt_lower for word in ['code', 'implement', 'function']):
            return 'code_generation'
        else:
            return 'general_dialogue'
            
    def process_message(self, user_id: str, message: str) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            user_id (str): The ID of the user
            message (str): The user's message
            
        Returns:
            str: The generated response
        """
        try:
            # Get relevant context from memory
            context = self.memory_manager.get_context(user_id)
            
            # Build the prompt with context
            prompt = self.prompt_builder.build_prompt(message, context)
            
            # Detect intent
            intent = self.detect_intent(message)
            
            # Prepare context info for model routing
            context_info = {
                "intent": intent,
                "token_length": len(prompt),
                "user_id": user_id
            }
            
            # Get completion from appropriate model
            response = get_completion(prompt, context_info)
            
            # Store interaction in memory
            self.memory_manager.store_interaction(user_id, message, response)
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            return error_msg
            
    def get_chat_history(self, user_id: str) -> list:
        """
        Retrieve chat history for a user.
        
        Args:
            user_id (str): The ID of the user
            
        Returns:
            list: The chat history
        """
        return self.memory_manager.get_history(user_id)

    def get_chat_context(self, user_id: str, limit: int = 10) -> List[str]:
        """Get chat context for a user.
        
        Args:
            user_id: The ID of the user to get context for
            limit: Maximum number of memories to return (default: 10)
            
        Returns:
            List of memory contents as strings
        """
        return self.memory_manager.get_chat_context(user_id, limit=limit) 