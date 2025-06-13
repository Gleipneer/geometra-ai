#!/usr/bin/env python3
"""
Model Router Module

This module handles intelligent routing of prompts to different AI models
based on intent, complexity, and system load. It implements a fallback
mechanism and token-based model selection.
"""

import os
import logging
from typing import Dict, Any, Optional
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/model_router.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Model constants
GPT4OMNI = "gpt-4o"
GPT35 = "gpt-3.5-turbo"

# API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
fallback_key = os.getenv("FALLBACK_API_KEY")

def route_model(prompt: str, context_info: Dict[str, Any]) -> str:
    """
    Dynamically selects the appropriate model based on intent and load.
    
    Args:
        prompt (str): The input prompt to be processed
        context_info (Dict[str, Any]): Context information including:
            - intent: The detected intent of the prompt
            - token_length: Length of the prompt in tokens
            
    Returns:
        str: The selected model identifier
        
    Selection criteria:
    - GPT-3.5 for:
        - File summarization
        - Long prompts (>6000 tokens)
        - Simple operations
    - GPT-4o for:
        - Complex analysis
        - Decision support
        - General dialogue
    """
    try:
        # Check for summarization intent
        if "summarization" in context_info.get("intent", "").lower():
            logger.info("Selected GPT-3.5 for summarization task")
            return GPT35
            
        # Check token length
        if context_info.get("token_length", 0) > 6000:
            logger.info("Selected GPT-3.5 for long prompt")
            return GPT35
            
        # Default to GPT-4o for complex tasks
        logger.info("Selected GPT-4o for complex task")
        return GPT4OMNI
        
    except Exception as e:
        logger.error(f"Error in model routing: {str(e)}")
        return GPT35  # Fallback to GPT-3.5 on error

def get_completion(prompt: str, context_info: Dict[str, Any]) -> str:
    """
    Gets a completion from the appropriate model based on routing logic.
    
    Args:
        prompt (str): The input prompt
        context_info (Dict[str, Any]): Context information for routing
        
    Returns:
        str: The model's response
        
    Raises:
        Exception: If the API call fails
    """
    try:
        # Route to appropriate model
        model = route_model(prompt, context_info)
        
        # Select API key based on model
        key = fallback_key if model == GPT35 else os.getenv("OPENAI_API_KEY")
        openai.api_key = key
        
        # Log the request
        logger.info(f"Requesting completion from {model}")
        
        # Get completion
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Log success
        logger.info(f"Successfully got completion from {model}")
        
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = f"❌ Model call failed: {str(e)}"
        logger.error(error_msg)
        return error_msg 