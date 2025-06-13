# 🔄 06: Fallback Logik

## 🎯 Syfte
Implementera robust fallback-mekanism från GPT-4 till GPT-3.5 med:
- Automatisk modellväxling
- Retry-logik
- Felhantering
- Prestandamätning

## 📦 Komponenter

### 1. Model Manager
- Hanterar modellväxling
- Övervakar prestanda
- Loggar fel

### 2. Fallback Chain
- GPT-4 → GPT-3.5
- Retry-logik
- Felhantering

## 🛠️ Installation

1. **Skapa Fallback-struktur**
```bash
mkdir -p ai/fallback
touch ai/fallback/{__init__.py,model_manager.py,fallback_chain.py}
```

2. **Implementera Model Manager**
```python
# ai/fallback/model_manager.py
from typing import Dict, Optional
import time
import logging
from openai import OpenAI

class ModelManager:
    def __init__(self, config: Dict):
        self.config = config
        self.client = OpenAI()
        self.setup_logging()
        self.performance_metrics = {}
    
    def setup_logging(self):
        logging.basicConfig(
            filename='logs/fallback.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def chat(self, message: str, user_id: str, fallback: bool = True) -> Dict:
        try:
            # Försök med GPT-4
            response = self._call_gpt4(message)
            self._log_success("gpt-4")
            return response
        except Exception as e:
            if fallback:
                logging.warning(f"GPT-4 failed: {str(e)}")
                return self._fallback_to_gpt35(message)
            raise
    
    def _call_gpt4(self, message: str) -> Dict:
        start_time = time.time()
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}]
        )
        self._update_metrics("gpt-4", time.time() - start_time)
        return response
    
    def _fallback_to_gpt35(self, message: str) -> Dict:
        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )
            self._update_metrics("gpt-3.5", time.time() - start_time)
            self._log_success("gpt-3.5")
            return response
        except Exception as e:
            logging.error(f"Fallback failed: {str(e)}")
            raise
    
    def _update_metrics(self, model: str, response_time: float):
        if model not in self.performance_metrics:
            self.performance_metrics[model] = []
        self.performance_metrics[model].append(response_time)
    
    def _log_success(self, model: str):
        logging.info(f"Successfully used {model}")
```

3. **Implementera Fallback Chain**
```python
# ai/fallback/fallback_chain.py
from typing import List, Optional
import time
import logging

class FallbackChain:
    def __init__(self, models: List[str], max_retries: int = 3):
        self.models = models
        self.max_retries = max_retries
        self.current_model_index = 0
    
    def execute(self, func, *args, **kwargs) -> Optional[Dict]:
        retries = 0
        while retries < self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries == self.max_retries:
                    logging.error(f"All retries failed: {str(e)}")
                    raise
                self._next_model()
                time.sleep(1)  # Backoff
    
    def _next_model(self):
        self.current_model_index = (self.current_model_index + 1) % len(self.models)
        logging.info(f"Switching to model: {self.models[self.current_model_index]}")
```

## 🔧 Konfiguration

1. **Skapa Fallback Config**
```python
# config/fallback_config.py
FALLBACK_CONFIG = {
    "models": ["gpt-4", "gpt-3.5-turbo"],
    "max_retries": 3,
    "timeout": 30,
    "backoff_factor": 1.5
}
```

2. **Uppdatera Miljövariabler**
```bash
# .env
FALLBACK_ENABLED=true
FALLBACK_MODEL=gpt-3.5-turbo
FALLBACK_MAX_RETRIES=3
```

## ✅ Validering

Kör följande för att verifiera fallback:

```bash
# Testa fallback
python -m pytest tests/test_fallback.py

# Kontrollera loggar
cat logs/fallback.log
```

## 🔍 Felsökning

### Vanliga problem

1. **Model not available**
```bash
# Kontrollera API-nyckel
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Verifiera modelltillgänglighet
python scripts/check_models.py
```

2. **High latency**
```bash
# Kontrollera prestanda
python scripts/check_performance.py

# Analysera loggar
grep "response_time" logs/fallback.log
```

3. **Fallback chain fails**
```bash
# Kontrollera fallback-logik
python scripts/test_fallback_chain.py

# Verifiera konfiguration
cat config/fallback_config.py
```

## 📝 Loggning

```bash
echo "$(date) - 06_FALLBACK_LOGIK: Fallback konfigurerad" >> bootstrap_status.log
```

## 🔄 Rollback

Om fallback-logiken behöver återställas:

```bash
# Återställ till senaste version
git checkout -- ai/fallback/

# Verifiera konfiguration
python scripts/verify_fallback.py
```

## 🧪 Testfall

### 1. GPT-4 Failure
```python
def test_gpt4_failure():
    manager = ModelManager(config)
    # Simulera GPT-4 fel
    with patch('openai.ChatCompletion.create', side_effect=Exception):
        response = manager.chat("Test", "user123", fallback=True)
        assert response.model == "gpt-3.5-turbo"
```

### 2. Memory Miss
```python
def test_memory_miss():
    manager = ModelManager(config)
    # Simulera minnesfel
    with patch('redis.Redis.get', side_effect=Exception):
        response = manager.chat("Test", "user123")
        assert response is not None
```

### 3. API Timeout
```python
def test_api_timeout():
    manager = ModelManager(config)
    # Simulera timeout
    with patch('requests.post', side_effect=Timeout):
        response = manager.chat("Test", "user123", fallback=True)
        assert response.model == "gpt-3.5-turbo"
```

## 📊 Prestandamätning

```python
def measure_performance():
    manager = ModelManager(config)
    results = {
        "gpt-4": [],
        "gpt-3.5": []
    }
    
    for _ in range(100):
        start = time.time()
        manager.chat("Test", "user123")
        results[manager.current_model].append(time.time() - start)
    
    return results
```