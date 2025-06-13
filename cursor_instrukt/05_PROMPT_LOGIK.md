# 🧠 05: Prompt Logik

## 📦 Prompt-komponenter

### Prompt Builder
- Dynamisk promptgenerering
- Kontextinjektion
- Systemroll-hantering

### Prompt Templates
- Basmallar för olika syften
- Variabelinjektion
- Formatvalidering

## 🛠️ Installation

1. **Skapa prompt-struktur**
```bash
mkdir -p ai/{prompts,templates,utils}
touch ai/__init__.py
```

2. **Skapa PromptBuilder**
```python
# ai/prompts/builder.py
from typing import Dict, List, Optional
from ..templates.base import BaseTemplate
from ..utils.validator import validate_prompt

class PromptBuilder:
    def __init__(self):
        self.templates: Dict[str, BaseTemplate] = {}
        self.context: Dict[str, str] = {}
    
    def add_template(self, name: str, template: BaseTemplate):
        self.templates[name] = template
    
    def set_context(self, key: str, value: str):
        self.context[key] = value
    
    def build(self, template_name: str, **kwargs) -> str:
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")
        
        template = self.templates[template_name]
        prompt = template.render(**kwargs, **self.context)
        
        if not validate_prompt(prompt):
            raise ValueError("Invalid prompt format")
        
        return prompt
```

3. **Skapa BaseTemplate**
```python
# ai/templates/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTemplate(ABC):
    @abstractmethod
    def render(self, **kwargs) -> str:
        pass
    
    def validate(self, **kwargs) -> bool:
        return True
```

4. **Skapa ChatTemplate**
```python
# ai/templates/chat.py
from .base import BaseTemplate

class ChatTemplate(BaseTemplate):
    def render(self, **kwargs) -> str:
        system_role = kwargs.get("system_role", "assistant")
        context = kwargs.get("context", "")
        message = kwargs.get("message", "")
        
        return f"""System: Du är en {system_role}.
        
Kontext:
{context}

Användare: {message}

Assistent:"""
```

5. **Skapa PromptValidator**
```python
# ai/utils/validator.py
from typing import List
import re

def validate_prompt(prompt: str) -> bool:
    # Kontrollera minsta längd
    if len(prompt) < 10:
        return False
    
    # Kontrollera förbjudna mönster
    forbidden_patterns = [
        r"API_KEY",
        r"PASSWORD",
        r"SECRET"
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False
    
    return True
```

## 🔧 Konfiguration

1. **Skapa prompt_config.py**
```python
# ai/config.py
from pydantic import BaseSettings

class PromptSettings(BaseSettings):
    MAX_PROMPT_LENGTH: int = 4000
    DEFAULT_SYSTEM_ROLE: str = "assistant"
    CONTEXT_WINDOW: int = 5
    
    class Config:
        env_file = ".env"
```

2. **Skapa prompt_utils.py**
```python
# ai/utils/tokenizer.py
from typing import List
import tiktoken

def count_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-4")
    return len(encoding.encode(text))

def truncate_to_tokens(text: str, max_tokens: int) -> str:
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)
    return encoding.decode(tokens[:max_tokens])
```

## ✅ Validering

Kör följande för att verifiera prompt-logiken:

```bash
# Testa prompt builder
python -c "from ai.prompts.builder import PromptBuilder; from ai.templates.chat import ChatTemplate; builder = PromptBuilder(); builder.add_template('chat', ChatTemplate()); print(builder.build('chat', message='test'))"

# Verifiera tokenizer
python -c "from ai.utils.tokenizer import count_tokens; print(count_tokens('test'))"
```

## 🔍 Felsökning

### Vanliga problem

1. **Prompt för lång**
   ```bash
   # Kontrollera token-längd
   python -c "from ai.utils.tokenizer import count_tokens; print(count_tokens('$(cat long_prompt.txt)'))"
   
   # Trunkera prompt
   python -c "from ai.utils.tokenizer import truncate_to_tokens; print(truncate_to_tokens('$(cat long_prompt.txt)', 4000))"
   ```

2. **Ogiltig prompt-format**
   ```bash
   # Verifiera prompt
   python -c "from ai.utils.validator import validate_prompt; print(validate_prompt('$(cat prompt.txt)'))"
   ```

3. **Saknad template**
   ```bash
   # Lista tillgängliga templates
   python -c "from ai.prompts.builder import PromptBuilder; print(PromptBuilder().templates.keys())"
   ```

## 📝 Loggning

```bash
echo "$(date) - 05_PROMPT_LOGIK: Prompt-logik konfigurerad" >> bootstrap_status.log
```