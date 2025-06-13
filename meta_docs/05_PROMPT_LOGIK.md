# Implementera Prompt-logik

Detta dokument beskriver hur man implementerar prompt-logik och AI-integration i Geometra AI-systemet.

## Översikt

Prompt-logiken hanterar:

1. **Prompt-generering**
   - Kontext-sammanställning
   - Minnesintegration
   - Systeminstruktioner

2. **AI-integration**
   - OpenAI-anrop
   - Modellval
   - Parameterhantering

3. **Svarshantering**
   - Parsning
   - Validering
   - Formatering

## Installation

1. Installera OpenAI-klient:
```bash
pip install openai
```

2. Skapa prompt-struktur:
```bash
mkdir -p prompts/{templates,utils}
```

## Konfiguration

### Prompt-hanterare

1. Skapa `prompts/manager.py`:
```python
"""Prompt manager for handling AI interactions."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from ..memory.chroma.manager import ChromaManager
from ..memory.redis.manager import RedisManager

class PromptManager:
    """Manages prompt generation and AI interactions."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """Initialize prompt manager."""
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.chroma = ChromaManager()
        self.redis = RedisManager()
        
        openai.api_key = api_key
    
    def generate_prompt(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a prompt with context and memory."""
        # Hämta relevanta minnen
        memories = self.chroma.get_memory(message)
        
        # Hämta session-kontext
        session_context = None
        if session_id:
            session_context = self.redis.get_context(session_id)
        
        # Bygg prompt
        prompt_parts = [
            "Du är Geometra AI, en assistent som hjälper till med geometriska beräkningar och visualiseringar.",
            "Använd följande kontext för att ge ett relevant svar:",
            f"Användarfråga: {message}"
        ]
        
        # Lägg till minnen
        if memories:
            prompt_parts.append("\nRelevant kontext från tidigare konversationer:")
            for memory in memories:
                prompt_parts.append(f"- {memory['text']}")
        
        # Lägg till session-kontext
        if session_context:
            prompt_parts.append("\nAktiv konversationskontext:")
            prompt_parts.append(str(session_context))
        
        # Lägg till systeminstruktioner
        prompt_parts.extend([
            "\nInstruktioner:",
            "1. Ge ett tydligt och pedagogiskt svar",
            "2. Inkludera relevanta formler och beräkningar",
            "3. Förklara steg för steg hur du kom fram till svaret",
            "4. Använd LaTeX för matematiska uttryck"
        ])
        
        return "\n".join(prompt_parts)
    
    async def get_ai_response(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get response from AI model."""
        # Generera prompt
        prompt = self.generate_prompt(message, session_id, context)
        
        # Anropa OpenAI
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Extrahera svar
        ai_response = response.choices[0].message.content
        
        # Uppdatera session-kontext
        if session_id:
            self.redis.set_context(
                session_id,
                {
                    "last_message": message,
                    "last_response": ai_response,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # Spara i långtidsminne
        self.chroma.add_memory(
            message,
            {
                "type": "conversation",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {
            "message": ai_response,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
```

### Prompt-mallar

1. Skapa `prompts/templates/system.py`:
```python
"""System prompt templates."""

SYSTEM_PROMPT = """Du är Geometra AI, en assistent som hjälper till med geometriska beräkningar och visualiseringar.

Dina huvuduppgifter är:
1. Hjälpa användare med geometriska beräkningar
2. Förklara geometriska koncept
3. Generera visualiseringar
4. Lösa geometriska problem

Använd följande format för svar:
1. Kort sammanfattning av problemet
2. Steg-för-steg lösning med formler
3. Slutsvar med enheter
4. Relevanta visualiseringar (om tillämpligt)

Använd LaTeX för matematiska uttryck och formler."""

ERROR_PROMPT = """Ett fel uppstod vid bearbetning av din fråga. 
Vänligen försök igen med en tydligare formulering eller dela upp frågan i mindre delar."""

HELP_PROMPT = """Jag kan hjälpa dig med:
1. Beräkningar av area, omkrets, volym
2. Trigonometriska funktioner
3. Vektorer och matriser
4. Geometriska transformationer
5. Visualiseringar och grafer

För att få bästa resultat:
1. Var tydlig med vad du vill beräkna
2. Ange alla nödvändiga mått
3. Specificera önskade enheter
4. Beskriv eventuella begränsningar"""
```

### Prompt-verktyg

1. Skapa `prompts/utils/formatting.py`:
```python
"""Prompt formatting utilities."""

from typing import List, Dict, Any
import re

def format_latex(text: str) -> str:
    """Format LaTeX expressions in text."""
    # Hitta LaTeX-uttryck
    latex_pattern = r'\$([^$]+)\$'
    
    def replace_latex(match):
        expr = match.group(1)
        return f"$${expr}$$"
    
    return re.sub(latex_pattern, replace_latex, text)

def format_context(context: Dict[str, Any]) -> str:
    """Format context for prompt."""
    parts = []
    
    if "last_message" in context:
        parts.append(f"Senaste meddelande: {context['last_message']}")
    
    if "last_response" in context:
        parts.append(f"Senaste svar: {context['last_response']}")
    
    if "timestamp" in context:
        parts.append(f"Tidpunkt: {context['timestamp']}")
    
    return "\n".join(parts)

def format_memories(memories: List[Dict[str, Any]]) -> str:
    """Format memories for prompt."""
    if not memories:
        return "Inga relevanta minnen hittades."
    
    parts = ["Relevanta minnen:"]
    for memory in memories:
        parts.append(f"- {memory['text']}")
        if "metadata" in memory:
            parts.append(f"  Metadata: {memory['metadata']}")
    
    return "\n".join(parts)
```

## Validering

1. Testa prompt-generering:
```python
from prompts.manager import PromptManager

manager = PromptManager(api_key="your-api-key")
prompt = manager.generate_prompt("Beräkna arean av en cirkel med radie 5 cm")
print(prompt)
```

2. Testa AI-integration:
```python
response = await manager.get_ai_response(
    "Beräkna arean av en cirkel med radie 5 cm",
    session_id="test-session"
)
print(response)
```

3. Kör prompt-tester:
```bash
python -m pytest tests/prompts/
```

## Felsökning

### Prompt-problem

1. **Kontext-problem**
   - Verifiera minneshämtning
   - Kontrollera session-hantering
   - Validera prompt-format

2. **AI-problem**
   - Kontrollera API-nyckel
   - Verifiera modell-tillgänglighet
   - Kontrollera token-gränser

3. **Formateringsproblem**
   - Validera LaTeX-syntax
   - Kontrollera kontext-format
   - Verifiera minnes-format

## Loggning

1. Skapa loggkatalog:
```bash
mkdir -p logs/prompts
```

2. Konfigurera loggning i `prompts/utils/logging.py`:
```python
"""Logging configuration for prompts."""

import logging
import os
from datetime import datetime

def setup_prompt_logging():
    """Configure logging for prompts."""
    log_dir = "logs/prompts"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"prompts_{datetime.now().strftime('%Y%m%d')}.log"
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

1. Konfigurera [Fallback-logik](06_FALLBACK_LOGIK.md)
2. Bygg [Frontend](07_FRONTEND.md)
3. Implementera [Visualiseringar](08_VISUALISERINGAR.md) 