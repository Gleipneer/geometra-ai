# Konfigurera Deployment

Detta dokument beskriver hur man konfigurerar och hanterar deployment av Geometra AI-systemet.

## Översikt

Deployment-systemet innehåller:

1. **CI/CD-pipeline**
   - Automatiserad byggning
   - Testning
   - Deployment

2. **Infrastruktur**
   - Docker-containrar
   - Kubernetes
   - Cloud-resurser

3. **Övervakning**
   - Loggning
   - Metrics
   - Alerting

## Installation

1. Installera Docker:
```bash
curl -fsSL https://get.docker.com | sh
```

2. Installera Kubernetes-verktyg:
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

## Konfiguration

### Docker

1. Skapa `Dockerfile` för backend:
```dockerfile
"""Backend Dockerfile."""

FROM python:3.11-slim

WORKDIR /app

# Installera systemberoenden
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Kopiera requirements
COPY requirements.txt .

# Installera Python-beroenden
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera applikationskod
COPY . .

# Exponera port
EXPOSE 8000

# Starta applikation
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Skapa `Dockerfile` för frontend:
```dockerfile
"""Frontend Dockerfile."""

FROM node:18-alpine

WORKDIR /app

# Installera pnpm
RUN npm install -g pnpm

# Kopiera package.json och pnpm-lock.yaml
COPY package.json pnpm-lock.yaml ./

# Installera beroenden
RUN pnpm install

# Kopiera applikationskod
COPY . .

# Bygg applikation
RUN pnpm build

# Exponera port
EXPOSE 80

# Starta applikation
CMD ["pnpm", "start"]
```

3. Skapa `docker-compose.yml`:
```yaml
"""Docker Compose configuration."""

version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8001
      - REDIS_URL=redis://redis:6379
    depends_on:
      - chromadb
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

  chromadb:
    image: chromadb/chroma
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  chroma_data:
  redis_data:
```

### Kubernetes

1. Skapa `k8s/backend-deployment.yaml`:
```yaml
"""Backend Kubernetes deployment."""

apiVersion: apps/v1
kind: Deployment
metadata:
  name: geometra-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: geometra-backend
  template:
    metadata:
      labels:
        app: geometra-backend
    spec:
      containers:
      - name: backend
        image: geometra-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: CHROMA_HOST
          value: chromadb
        - name: CHROMA_PORT
          value: "8001"
        - name: REDIS_URL
          value: redis://redis:6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: geometra-backend
spec:
  selector:
    app: geometra-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

2. Skapa `k8s/frontend-deployment.yaml`:
```yaml
"""Frontend Kubernetes deployment."""

apiVersion: apps/v1
kind: Deployment
metadata:
  name: geometra-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: geometra-frontend
  template:
    metadata:
      labels:
        app: geometra-frontend
    spec:
      containers:
      - name: frontend
        image: geometra-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: geometra-frontend
spec:
  selector:
    app: geometra-frontend
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

### CI/CD

1. Skapa `.github/workflows/main.yml`:
```yaml
"""GitHub Actions workflow."""

name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install pnpm
      uses: pnpm/action-setup@v2
      with:
        version: 8
    
    - name: Install frontend dependencies
      run: |
        cd frontend
        pnpm install
    
    - name: Run frontend tests
      run: |
        cd frontend
        pnpm test

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push backend
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: geometra/backend:latest
    
    - name: Build and push frontend
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: true
        tags: geometra/frontend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
    
    - name: Set up kubeconfig
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" > kubeconfig.yaml
        export KUBECONFIG=kubeconfig.yaml
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/
```

## Validering

1. Bygg Docker-images:
```bash
docker-compose build
```

2. Starta tjänster lokalt:
```bash
docker-compose up -d
```

3. Verifiera deployment:
```bash
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

## Felsökning

### Deployment-problem

1. **Docker-problem**
   - Kontrollera Dockerfile
   - Verifiera volymer
   - Validera nätverk

2. **Kubernetes-problem**
   - Kontrollera deployment
   - Verifiera services
   - Validera resurser

3. **CI/CD-problem**
   - Kontrollera workflow
   - Verifiera secrets
   - Validera byggprocess

## Loggning

1. Konfigurera loggning i `deployment/utils/logging.py`:
```python
"""Deployment logging configuration."""

import logging
import os
from datetime import datetime

def setup_deployment_logging():
    """Configure logging for deployment."""
    log_dir = "logs/deployment"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"deployment_{datetime.now().strftime('%Y%m%d')}.log"
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

1. Skapa [Dokumentation](10_DOKUMENTATION.md)
2. Implementera [Tester](11_TESTER.md)
3. Konfigurera [Övervakning](12_ÖVERVAKNING.md) 