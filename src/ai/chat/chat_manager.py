"""
Chat manager implementation for Geometra AI.
Handles chat history and AI interactions.
"""

from typing import Dict, List, Optional
import json
from datetime import datetime

class ChatManager:
    """Chat manager for Geometra AI."""
    
    def __init__(self, db_manager, memory_manager, fallback_manager, prompt_manager):
        """Initialize chat manager.
        
        Args:
            db_manager: Database manager instance
            memory_manager: Memory manager instance
            fallback_manager: Fallback manager instance
            prompt_manager: Prompt manager instance
        """
        self.db = db_manager
        self.memory = memory_manager
        self.fallback = fallback_manager
        self.prompt = prompt_manager
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """Process user message.
        
        Args:
            user_id: User identifier
            message: User message
            context: Optional context dictionary
            
        Returns:
            Response dictionary
        """
        # Get relevant memory
        memory = await self._get_relevant_memory(user_id, message)
        
        # Get chat context
        chat_context = self.prompt.get_chat_context(
            user_id,
            message,
            memory
        )
        
        # Get system prompt
        system_prompt = self.prompt.get_system_prompt(chat_context)
        
        # Get user prompt
        user_prompt = self.prompt.get_user_prompt(message, chat_context)
        
        # Get AI response
        response = await self.fallback.get_completion(
            user_prompt,
            {"system": system_prompt, **context or {}}
        )
        
        # Store in memory
        await self.memory.store_stm(user_id, message)
        await self.memory.store_ltm(message)
        
        # Store in chat history
        await self._store_chat_history(user_id, message, response)
        
        return {
            "response": response,
            "memory": memory,
            "context": chat_context
        }
    
    async def _get_relevant_memory(
        self,
        user_id: str,
        message: str
    ) -> Dict:
        """Get relevant memory for message.
        
        Args:
            user_id: User identifier
            message: User message
            
        Returns:
            Memory dictionary
        """
        # Get short-term memory
        stm = await self.memory.get_stm(user_id)
        
        # Get long-term memory
        ltm = await self.memory.search_ltm(message)
        
        return {
            "short_term": stm,
            "long_term": ltm
        }
    
    async def _store_chat_history(
        self,
        user_id: str,
        message: str,
        response: str
    ):
        """Store chat history.
        
        Args:
            user_id: User identifier
            message: User message
            response: AI response
        """
        key = f"chat:{user_id}:{int(datetime.now().timestamp())}"
        data = {
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        await self.db.redis.setex(key, 86400, json.dumps(data))
    
    async def get_chat_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get chat history.
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries
            
        Returns:
            List of chat entries
        """
        pattern = f"chat:{user_id}:*"
        keys = await self.db.redis.keys(pattern)
        keys.sort(reverse=True)
        keys = keys[:limit]
        
        if not keys:
            return []
        
        values = await self.db.redis.mget(keys)
        return [json.loads(v) for v in values if v]
    
    async def analyze_chat(
        self,
        user_id: str,
        limit: int = 10
    ) -> Dict:
        """Analyze chat history.
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries to analyze
            
        Returns:
            Analysis dictionary
        """
        history = await self.get_chat_history(user_id, limit)
        
        if not history:
            return {}
        
        # Calculate metrics
        total_messages = len(history)
        avg_response_length = sum(
            len(h["response"]) for h in history
        ) / total_messages
        
        # Get common topics
        topics = {}
        for entry in history:
            # Simple word-based topic extraction
            words = entry["message"].lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    topics[word] = topics.get(word, 0) + 1
        
        # Get top topics
        top_topics = sorted(
            topics.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_messages": total_messages,
            "avg_response_length": avg_response_length,
            "top_topics": dict(top_topics)
        } 