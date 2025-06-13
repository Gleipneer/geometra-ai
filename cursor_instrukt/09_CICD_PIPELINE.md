# 🔄 09: CI/CD Pipeline

## 📦 Pipeline-komponenter

### GitHub Actions
- Automatiserad byggning
- Testning
- Deployment

### Workflows
- Pull Request
- Main Branch
- Staging

## 🛠️ Installation

1. **Skapa GitHub Actions-struktur**
```bash
mkdir -p .github/workflows
```

2. **Skapa PR Workflow**
```yaml
# .github/workflows/pr.yml
name: Pull Request

on:
  pull_request:
    branches: [ main, staging ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=api --cov=memory --cov=ai
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

3. **Skapa Main Workflow**
```yaml
# .github/workflows/main.yml
name: Main Branch

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: geometra-ai:latest
    
    - name: Deploy to Railway
      uses: railwayapp/cli@master
      with:
        token: ${{ secrets.RAILWAY_TOKEN }}
      run: |
        railway up
```

4. **Skapa Staging Workflow**
```yaml
# .github/workflows/staging.yml
name: Staging

on:
  push:
    branches: [ staging ]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest
    
    - name: Deploy to Staging
      uses: railwayapp/cli@master
      with:
        token: ${{ secrets.RAILWAY_TOKEN }}
      run: |
        railway up --environment staging
```

## 🔧 Konfiguration

1. **Skapa GitHub Secrets**
```bash
# Lägg till i GitHub repository settings:
RAILWAY_TOKEN=your_railway_token
OPENAI_API_KEY=your_openai_key
```

2. **Skapa Railway Config**
```json
# railway.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## ✅ Validering

Kör följande för att verifiera CI/CD:

```bash
# Testa lokalt
act -j test

# Verifiera GitHub Actions
gh workflow list

# Kontrollera Railway
railway status
```

## 🔍 Felsökning

### Vanliga problem

1. **GitHub Actions misslyckas**
   ```bash
   # Kontrollera loggar
   gh run list
   gh run view <run-id>
   
   # Kör lokalt
   act -j test --verbose
   ```

2. **Railway Deployment**
   ```bash
   # Kontrollera status
   railway status
   
   # Visa loggar
   railway logs
   ```

3. **Docker Build**
   ```bash
   # Testa lokalt
   docker build -t geometra-ai .
   
   # Verifiera image
   docker run -p 8000:8000 geometra-ai
   ```

## 📝 Loggning

```bash
echo "$(date) - 09_CICD_PIPELINE: CI/CD konfigurerad" >> bootstrap_status.log
```