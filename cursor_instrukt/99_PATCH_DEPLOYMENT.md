# Deployment och CI/CD Implementation

## 1. Implementera GitHub Actions Workflow

### .github/workflows/main.yml
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:6
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Install Node.js dependencies
      run: |
        cd frontend
        npm install
    
    - name: Run backend tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm test
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
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
        file: ./Dockerfile.backend
        push: true
        tags: ${{ secrets.DOCKERHUB_USERNAME }}/geometra-ai-backend:latest
    
    - name: Build and push frontend
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        file: ./frontend/Dockerfile
        push: true
        tags: ${{ secrets.DOCKERHUB_USERNAME }}/geometra-ai-frontend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: eu-north-1
    
    - name: Update ECS service
      run: |
        aws ecs update-service --cluster geometra-ai --service geometra-ai-service --force-new-deployment
```

## 2. Implementera Dockerfile för Backend

### Dockerfile.backend
```dockerfile
# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install Python packages
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 3. Implementera Dockerfile för Frontend

### frontend/Dockerfile
```dockerfile
# Build stage
FROM node:16-alpine as builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

## 4. Implementera Nginx-konfiguration

### frontend/nginx.conf
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml application/javascript;
    gzip_disable "MSIE [1-6]\.";

    # Cache control
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 5. Implementera AWS ECS Task Definition

### aws/task-definition.json
```json
{
  "family": "geometra-ai",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/geometra-ai-task-role",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "yourusername/geometra-ai-backend:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@db:5432/geometra"
        },
        {
          "name": "REDIS_URL",
          "value": "redis://redis:6379"
        },
        {
          "name": "OPENAI_API_KEY",
          "value": "your-api-key"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:ssm:eu-north-1:123456789012:parameter/geometra-ai/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/geometra-ai",
          "awslogs-region": "eu-north-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    },
    {
      "name": "frontend",
      "image": "yourusername/geometra-ai-frontend:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/geometra-ai",
          "awslogs-region": "eu-north-1",
          "awslogs-stream-prefix": "frontend"
        }
      }
    }
  ]
}
```

## 6. Implementera AWS ECS Service

### aws/service.json
```json
{
  "cluster": "geometra-ai",
  "serviceName": "geometra-ai-service",
  "taskDefinition": "geometra-ai",
  "desiredCount": 2,
  "launchType": "FARGATE",
  "platformVersion": "LATEST",
  "deploymentConfiguration": {
    "maximumPercent": 200,
    "minimumHealthyPercent": 100,
    "deploymentCircuitBreaker": {
      "enable": true,
      "rollback": true
    }
  },
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": ["subnet-12345678", "subnet-87654321"],
      "securityGroups": ["sg-12345678"],
      "assignPublicIp": "ENABLED"
    }
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:elasticloadbalancing:eu-north-1:123456789012:targetgroup/geometra-ai/1234567890123456",
      "containerName": "frontend",
      "containerPort": 80
    }
  ],
  "healthCheckGracePeriodSeconds": 60,
  "propagateTags": "SERVICE"
}
```

## 7. Verifiera Implementation

```bash
# Testa lokalt med Docker Compose
docker-compose up -d

# Verifiera GitHub Actions
git push origin main

# Verifiera AWS ECS
aws ecs describe-services --cluster geometra-ai --services geometra-ai-service
```

## 8. Nästa steg

Efter att ha implementerat deployment och CI/CD, kör:

```bash
# Skapa AWS-resurser
aws cloudformation create-stack \
  --stack-name geometra-ai \
  --template-body file://aws/cloudformation.yml \
  --capabilities CAPABILITY_IAM

# Vänta på att stacken skapas
aws cloudformation wait stack-create-complete --stack-name geometra-ai

# Uppdatera ECS-tjänsten
aws ecs update-service \
  --cluster geometra-ai \
  --service geometra-ai-service \
  --task-definition geometra-ai \
  --force-new-deployment
```

Detta implementerar:
- Kontinuerlig integration med GitHub Actions
- Automatiserad testning
- Docker-containerisering
- AWS ECS-deployment
- Load balancing
- Säkerhetskonfiguration
- Loggning
- Övervakning

Nästa steg är att implementera övervakning och loggning. 