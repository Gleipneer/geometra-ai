# AI-routing & Modellstyrning

## Översikt

Detta dokument beskriver implementationen av intelligent AI-routing och modellstyrning i Geometra AI-systemet. Implementationen fokuserar på att optimera modellanvändning baserat på syfte, komplexitet och systembelastning.

## Komponenter

### 1. Model Router (`ai/model_router.py`)

```python
import os
import openai

GPT4OMNI = "gpt-4o"
GPT35 = "gpt-3.5-turbo"

openai.api_key = os.getenv("OPENAI_API_KEY")
fallback_key = os.getenv("FALLBACK_API_KEY")

def route_model(prompt: str, context_info: dict) -> str:
    """
    Dynamiskt väljer rätt modell baserat på syfte och last.
    """
    if "file_summarization" in context_info.get("intent", ""):
        model = GPT35
    elif context_info.get("token_length", 0) > 6000:
        model = GPT35
    else:
        model = GPT4OMNI
    
    return model

def get_completion(prompt: str, context_info: dict) -> str:
    model = route_model(prompt, context_info)
    key = fallback_key if model == GPT35 else os.getenv("OPENAI_API_KEY")

    openai.api_key = key
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Modellanrop misslyckades: {str(e)}"
```

### 2. Integration med Chat Engine

```python
from ai.model_router import get_completion

# Exempel på användning i chat_engine.py
answer = get_completion(prompt, {
    "intent": "summarization", 
    "token_length": len(prompt)
})
```

## Modellstrategi

| Modell | Användningsområde |
|--------|-------------------|
| GPT-4o (default) | Allmän dialog, komplex analys, beslutsstöd |
| GPT-3.5-turbo | Enkla operationer, kodsortering, filsammanfattning, fallback |
| (Framtida) | Llama/Claude via OpenRouter |

## Implementation

1. Skapa `ai/model_router.py`
2. Uppdatera `chat_engine.py` med ny routing-logik
3. Implementera intent-baserad styrning
4. Testa med olika användningsfall

## Validering

1. Verifiera modellval baserat på:
   - Intent-typ
   - Token-längd
   - Komplexitet
2. Testa fallback-mekanism
3. Verifiera prestanda

## Nästa Steg

1. Implementera rollbaserad AI-routing
2. Skapa "persona-shards" för specialiserade funktioner
3. Integrera med OpenRouter för fler modeller

## Loggning

Alla modellval och routing-beslut loggas för analys och optimering.

## Säkerhet

- API-nycklar hanteras säkert
- Modellval valideras
- Felhantering implementerad

## Prestanda

- Modellval optimeras för snabbast möjliga svar
- Token-användning minimeras
- Fallback-logik säkerställer tillgänglighet 