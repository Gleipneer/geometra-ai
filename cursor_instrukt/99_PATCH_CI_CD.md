# CI/CD och Deployment Implementation

## 1. Skapa GitHub Actions Workflow

### .github/workflows/main.yml
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis
        ports:
          - 6379:6379
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: geometra_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '20'
        cache: 'pnpm'

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Install Node.js dependencies
      run: |
        pnpm install

    - name: Run backend tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/geometra_test
        REDIS_URL: redis://localhost:6379
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        pytest tests/unit/api/
        pytest tests/integration/

    - name: Run frontend tests
      run: |
        cd frontend
        pnpm test

    - name: Run linting
      run: |
        flake8 src/
        black --check src/
        cd frontend
        pnpm lint

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Log in to GitHub Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push backend image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./Dockerfile.backend
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:latest

    - name: Build and push frontend image
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        file: ./frontend/Dockerfile
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:latest

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
        aws ecs update-service --cluster geometra-cluster --service geometra-service --force-new-deployment
```

## 2. Skapa Dockerfile för Backend

### Dockerfile.backend
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installera systemberoenden
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Kopiera requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera applikationskod
COPY src/ src/
COPY alembic.ini .
COPY migrations/ migrations/

# Skapa användare
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Exponera port
EXPOSE 8000

# Starta applikation
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 3. Skapa Dockerfile för Frontend

### frontend/Dockerfile
```dockerfile
FROM node:20-slim as builder

WORKDIR /app

# Kopiera package.json och pnpm-lock.yaml
COPY package.json pnpm-lock.yaml ./

# Installera pnpm
RUN npm install -g pnpm

# Installera dependencies
RUN pnpm install

# Kopiera källkod
COPY . .

# Bygg applikation
RUN pnpm build

# Produktionssteg
FROM nginx:alpine

# Kopiera nginx-konfiguration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Kopiera byggda filer
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## 4. Skapa Nginx-konfiguration

### frontend/nginx.conf
```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip-komprimering
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache-kontroll
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }

    # API-proxy
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # SPA-routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Säkerhetsheaders
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self' https://api.openai.com;";
}
```

## 5. Skapa Docker Compose för Utveckling

### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/geometra
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=geometra
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 6. Skapa AWS ECS Task Definition

### aws/task-definition.json
```json
{
  "family": "geometra",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "${ECR_REGISTRY}/geometra/backend:latest",
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
          "value": "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}"
        },
        {
          "name": "REDIS_URL",
          "value": "redis://${REDIS_HOST}:6379"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:ssm:${AWS_REGION}:${AWS_ACCOUNT_ID}:parameter/geometra/openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/geometra",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "backend"
        }
      }
    },
    {
      "name": "frontend",
      "image": "${ECR_REGISTRY}/geometra/frontend:latest",
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
          "awslogs-group": "/ecs/geometra",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "frontend"
        }
      }
    }
  ]
}
```

## 7. Skapa AWS ECS Service

### aws/service.json
```json
{
  "cluster": "geometra-cluster",
  "serviceName": "geometra-service",
  "taskDefinition": "geometra",
  "desiredCount": 2,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": ["${SUBNET_1}", "${SUBNET_2}"],
      "securityGroups": ["${SECURITY_GROUP}"],
      "assignPublicIp": "ENABLED"
    }
  },
  "loadBalancers": [
    {
      "targetGroupArn": "${TARGET_GROUP_ARN}",
      "containerName": "frontend",
      "containerPort": 80
    }
  ],
  "deploymentConfiguration": {
    "maximumPercent": 200,
    "minimumHealthyPercent": 100,
    "deploymentCircuitBreaker": {
      "enable": true,
      "rollback": true
    }
  }
}
```

## 8. Verifiera Implementation

```bash
# Testa lokalt med Docker Compose
docker-compose up --build

# Verifiera GitHub Actions
git push origin main
```

## 9. Nästa steg

Efter att ha implementerat CI/CD och deployment, kör:

```bash
# Skapa AWS-resurser
aws cloudformation create-stack \
  --stack-name geometra-infrastructure \
  --template-body file://aws/infrastructure.yaml \
  --capabilities CAPABILITY_IAM

# Distribuera applikation
aws ecs create-service \
  --cli-input-json file://aws/service.json
```

Detta implementerar:
- Kontinuerlig integration med GitHub Actions
- Automatiserad testning
- Docker-containerisering
- AWS ECS-deployment
- Load balancing och skalning
- Säkerhetskonfiguration
- Loggning och övervakning

Nästa steg är att implementera övervakning och loggning. 