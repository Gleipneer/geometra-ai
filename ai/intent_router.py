#!/usr/bin/env python3
"""
Intent Router Module

This module handles the classification of user intents from prompts,
using a combination of keyword matching and pattern recognition.
"""

import re
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/intent_router.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntentRouter:
    """
    Routes and classifies user intents from prompts.
    """
    
    def __init__(self):
        """Initialize the intent router with pattern definitions."""
        # Define intent patterns
        self.intent_patterns = {
            'summarization': [
                r'summarize',
                r'summary',
                r'overview',
                r'brief',
                r'sum up'
            ],
            'troubleshooting': [
                r'fix',
                r'error',
                r'problem',
                r'issue',
                r'bug',
                r'not working',
                r'failed'
            ],
            'code_generation': [
                r'code',
                r'implement',
                r'function',
                r'class',
                r'method',
                r'algorithm'
            ],
            'reflective_dialogue': [
                r'think',
                r'consider',
                r'analyze',
                r'evaluate',
                r'discuss',
                r'explain'
            ]
        }
        
        # Compile patterns
        self.compiled_patterns = {
            intent: [re.compile(pattern, re.IGNORECASE) 
                    for pattern in patterns]
            for intent, patterns in self.intent_patterns.items()
        }
        
    def detect_intent(self, prompt: str) -> str:
        """
        Detect the intent of a prompt using pattern matching.
        
        Args:
            prompt (str): The user's input prompt
            
        Returns:
            str: The detected intent
        """
        try:
            # Check each intent's patterns
            for intent, patterns in self.compiled_patterns.items():
                if any(pattern.search(prompt) for pattern in patterns):
                    logger.info(f"Detected intent: {intent}")
                    return intent
                    
            # Default to general dialogue if no specific intent detected
            logger.info("No specific intent detected, defaulting to general_dialogue")
            return 'general_dialogue'
            
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            return 'general_dialogue'
            
    def get_intent_confidence(self, prompt: str, intent: str) -> float:
        """
        Calculate confidence score for the detected intent.
        
        Args:
            prompt (str): The user's input prompt
            intent (str): The detected intent
            
        Returns:
            float: Confidence score between 0 and 1
        """
        try:
            if intent == 'general_dialogue':
                return 0.5
                
            # Count matching patterns
            patterns = self.compiled_patterns.get(intent, [])
            matches = sum(1 for pattern in patterns if pattern.search(prompt))
            
            # Calculate confidence based on number of matches
            confidence = min(matches / len(patterns), 1.0)
            logger.info(f"Intent confidence for {intent}: {confidence}")
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating intent confidence: {str(e)}")
            return 0.0
            
    def get_all_intents(self, prompt: str) -> Dict[str, float]:
        """
        Get confidence scores for all possible intents.
        
        Args:
            prompt (str): The user's input prompt
            
        Returns:
            Dict[str, float]: Dictionary of intents and their confidence scores
        """
        return {
            intent: self.get_intent_confidence(prompt, intent)
            for intent in self.intent_patterns.keys()
        } 