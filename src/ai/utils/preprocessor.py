"""
Text preprocessor implementation for Geometra AI.
Handles text cleaning and normalization.
"""

from typing import List, Dict
import re
import unicodedata

class Preprocessor:
    """Text preprocessor for Geometra AI."""
    
    def __init__(self):
        """Initialize preprocessor."""
        self.whitespace_pattern = re.compile(r'\s+')
        self.special_chars_pattern = re.compile(r'[^\w\s]')
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove special characters
        text = self.special_chars_pattern.sub(' ', text)
        
        # Normalize whitespace
        text = self.whitespace_pattern.sub(' ', text)
        
        return text.strip()
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting on common punctuation
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction (words longer than 3 chars)
        words = text.split()
        return [w for w in words if len(w) > 3]
    
    def normalize_numbers(self, text: str) -> str:
        """Normalize number formats in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized numbers
        """
        # Convert written numbers to digits
        number_map = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3',
            'four': '4', 'five': '5', 'six': '6', 'seven': '7',
            'eight': '8', 'nine': '9', 'ten': '10'
        }
        
        for word, digit in number_map.items():
            text = text.replace(word, digit)
        
        return text 