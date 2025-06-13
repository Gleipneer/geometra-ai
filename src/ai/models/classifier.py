"""
Classifier model implementation for Geometra AI.
Handles text classification using GPT models.
"""

from typing import Dict, List, Optional
import openai
import json

class ClassifierModel:
    """Classifier model handler for Geometra AI."""
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.0):
        """Initialize classifier model.
        
        Args:
            model_name: Name of the GPT model to use
            temperature: Sampling temperature (0-1)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.client = openai.AsyncOpenAI()
    
    async def classify(
        self,
        text: str,
        categories: List[str],
        context: Optional[Dict] = None
    ) -> Dict[str, float]:
        """Classify text into categories.
        
        Args:
            text: Input text to classify
            categories: List of possible categories
            context: Optional context dictionary
            
        Returns:
            Dictionary of category probabilities
        """
        prompt = f"""Classify the following text into one of these categories: {', '.join(categories)}
        
Text: {text}

Return a JSON object with category probabilities, like:
{{
    "category1": 0.8,
    "category2": 0.2
}}"""

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a text classification assistant. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {category: 0.0 for category in categories}
    
    async def get_top_category(
        self,
        text: str,
        categories: List[str],
        context: Optional[Dict] = None
    ) -> str:
        """Get the most likely category for text.
        
        Args:
            text: Input text to classify
            categories: List of possible categories
            context: Optional context dictionary
            
        Returns:
            Name of the most likely category
        """
        probabilities = await self.classify(text, categories, context)
        return max(probabilities.items(), key=lambda x: x[1])[0] 