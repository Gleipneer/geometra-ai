"""
Text postprocessor implementation for Geometra AI.
Handles response formatting and cleanup.
"""

from typing import List, Dict
import re
import json

class Postprocessor:
    """Text postprocessor for Geometra AI."""
    
    def __init__(self):
        """Initialize postprocessor."""
        self.whitespace_pattern = re.compile(r'\s+')
        self.markdown_pattern = re.compile(r'```[\s\S]*?```')
    
    def format_response(self, text: str) -> str:
        """Format response text.
        
        Args:
            text: Input text to format
            
        Returns:
            Formatted text
        """
        # Normalize whitespace
        text = self.whitespace_pattern.sub(' ', text)
        
        # Preserve markdown code blocks
        code_blocks = self.markdown_pattern.findall(text)
        text = self.markdown_pattern.sub('CODE_BLOCK', text)
        
        # Clean up text
        text = text.strip()
        
        # Restore code blocks
        for block in code_blocks:
            text = text.replace('CODE_BLOCK', block, 1)
        
        return text
    
    def extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from text.
        
        Args:
            text: Input text
            
        Returns:
            List of code blocks
        """
        return self.markdown_pattern.findall(text)
    
    def format_json(self, text: str) -> Dict:
        """Format text as JSON.
        
        Args:
            text: Input text containing JSON
            
        Returns:
            Formatted JSON dictionary
        """
        try:
            # Try to parse as JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # If not valid JSON, try to extract JSON-like structure
            json_pattern = re.compile(r'\{[\s\S]*\}')
            match = json_pattern.search(text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return {}
    
    def format_list(self, text: str) -> List[str]:
        """Format text as list.
        
        Args:
            text: Input text containing list items
            
        Returns:
            List of items
        """
        # Split on common list markers
        items = re.split(r'[\n-]', text)
        return [item.strip() for item in items if item.strip()] 