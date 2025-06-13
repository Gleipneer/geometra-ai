# Konfigurera Fallback-logik

Detta dokument beskriver hur man implementerar fallback-logik och felhantering i Geometra AI-systemet.

## Översikt

Fallback-logiken hanterar:

1. **Modell-fallback**
   - Primär modell (GPT-4)
   - Sekundär modell (GPT-3.5)
   - Lokal fallback

2. **Felhantering**
   - API-fel
   - Timeout
   - Rate limiting

3. **Återhämtning**
   - Automatisk återförsök
   - Felrapportering
   - Loggning

## Installation

1. Installera beroenden:
```bash
pip install tenacity python-dotenv
```

2. Skapa fallback-struktur:
```bash
mkdir -p fallback/{handlers,utils}
```

## Konfiguration

### Fallback-hanterare

1. Skapa `fallback/manager.py`:
```python
"""Fallback manager for handling model failures."""

from typing import Dict, Any, Optional, Callable
from datetime import datetime
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from ..prompts.manager import PromptManager
from ..memory.chroma.manager import ChromaManager
from ..memory.redis.manager import RedisManager

class FallbackManager:
    """Manages fallback logic for AI interactions."""
    
    def __init__(
        self,
        primary_api_key: str,
        fallback_api_key: Optional[str] = None,
        primary_model: str = "gpt-4",
        fallback_model: str = "gpt-3.5-turbo",
        max_retries: int = 3
    ):
        """Initialize fallback manager."""
        self.primary_api_key = primary_api_key
        self.fallback_api_key = fallback_api_key
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.max_retries = max_retries
        
        self.prompt_manager = PromptManager(
            api_key=primary_api_key,
            model=primary_model
        )
        
        self.chroma = ChromaManager()
        self.redis = RedisManager()
        
        self.logger = logging.getLogger(__name__)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_ai_response(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get AI response with fallback handling."""
        try:
            # Försök med primär modell
            return await self.prompt_manager.get_ai_response(
                message,
                session_id,
                context
            )
        except Exception as e:
            self.logger.error(f"Primary model failed: {str(e)}")
            
            if self.fallback_api_key:
                try:
                    # Försök med fallback-modell
                    fallback_manager = PromptManager(
                        api_key=self.fallback_api_key,
                        model=self.fallback_model
                    )
                    return await fallback_manager.get_ai_response(
                        message,
                        session_id,
                        context
                    )
                except Exception as e:
                    self.logger.error(f"Fallback model failed: {str(e)}")
            
            # Använd lokal fallback
            return self._get_local_fallback(message)
    
    def _get_local_fallback(self, message: str) -> Dict[str, Any]:
        """Get local fallback response."""
        # Hämta relevanta minnen
        memories = self.chroma.get_memory(message)
        
        # Bygg fallback-svar
        response_parts = [
            "Jag beklagar, men jag kunde inte bearbeta din fråga just nu.",
            "Här är några relevanta svar från tidigare konversationer:"
        ]
        
        if memories:
            for memory in memories[:3]:  # Visa max 3 minnen
                response_parts.append(f"- {memory['text']}")
        else:
            response_parts.append("Inga relevanta svar hittades.")
        
        response_parts.extend([
            "\nVänligen försök igen om några minuter.",
            "Om problemet kvarstår, kontakta support."
        ])
        
        return {
            "message": "\n".join(response_parts),
            "timestamp": datetime.now().isoformat(),
            "is_fallback": True
        }
```

### Felhanterare

1. Skapa `fallback/handlers/error_handler.py`:
```python
"""Error handling utilities."""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import traceback

class ErrorHandler:
    """Handles error logging and reporting."""
    
    def __init__(self):
        """Initialize error handler."""
        self.logger = logging.getLogger(__name__)
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle and log error."""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc()
        }
        
        if context:
            error_info["context"] = context
        
        # Logga fel
        self.logger.error(
            f"Error occurred: {error_info['error_type']} - {error_info['error_message']}"
        )
        
        # Spara fel i Redis för analys
        self._save_error(error_info)
        
        return error_info
    
    def _save_error(self, error_info: Dict[str, Any]):
        """Save error information for analysis."""
        # Här kan vi implementera logik för att spara
        # felinformation i Redis eller annan databas
        pass
```

### Återhämtningshanterare

1. Skapa `fallback/handlers/recovery_handler.py`:
```python
"""Recovery handling utilities."""

from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging
import asyncio

class RecoveryHandler:
    """Handles system recovery and retries."""
    
    def __init__(self, max_retries: int = 3):
        """Initialize recovery handler."""
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
    
    async def with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry logic."""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}"
                )
                
                if attempt == self.max_retries - 1:
                    raise
                
                # Vänta exponentiellt längre för varje försök
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
    
    async def recover_session(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """Attempt to recover a failed session."""
        try:
            # Här kan vi implementera logik för att
            # återställa en misslyckad session
            return True
        except Exception as e:
            self.logger.error(f"Session recovery failed: {str(e)}")
            return False
```

## Validering

1. Testa fallback-logik:
```python
from fallback.manager import FallbackManager

manager = FallbackManager(
    primary_api_key="your-api-key",
    fallback_api_key="your-fallback-key"
)

# Testa med ogiltig API-nyckel för att trigga fallback
response = await manager.get_ai_response(
    "Beräkna arean av en cirkel med radie 5 cm"
)
print(response)
```

2. Testa felhantering:
```python
from fallback.handlers.error_handler import ErrorHandler

handler = ErrorHandler()
error_info = handler.handle_error(
    ValueError("Invalid input"),
    context={"message": "test"}
)
print(error_info)
```

3. Kör fallback-tester:
```bash
python -m pytest tests/fallback/
```

## Felsökning

### Fallback-problem

1. **Modell-problem**
   - Verifiera API-nycklar
   - Kontrollera modell-tillgänglighet
   - Validera fallback-logik

2. **Felhanteringsproblem**
   - Kontrollera loggning
   - Verifiera felrapportering
   - Validera återhämtning

3. **Session-problem**
   - Verifiera session-återställning
   - Kontrollera kontext-hantering
   - Validera minneshantering

## Loggning

1. Skapa loggkatalog:
```bash
mkdir -p logs/fallback
```

2. Konfigurera loggning i `fallback/utils/logging.py`:
```python
"""Logging configuration for fallback system."""

import logging
import os
from datetime import datetime

def setup_fallback_logging():
    """Configure logging for fallback system."""
    log_dir = "logs/fallback"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"fallback_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
```

## Nästa steg

1. Bygg [Frontend](07_FRONTEND.md)
2. Implementera [Visualiseringar](08_VISUALISERINGAR.md)
3. Konfigurera [Deployment](09_DEPLOYMENT.md) 