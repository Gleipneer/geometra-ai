#!/bin/bash

# Färger för output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}Verifying system components and dependencies...${NC}"

# Verifiera Node.js och npm/pnpm
echo -e "\n${YELLOW}Checking Node.js environment...${NC}"
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js is installed${NC}"
    node_version=$(node --version)
    echo -e "  Version: $node_version"
else
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi

# Verifiera Python och pip
echo -e "\n${YELLOW}Checking Python environment...${NC}"
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python is installed${NC}"
    python_version=$(python3 --version)
    echo -e "  Version: $python_version"
else
    echo -e "${RED}✗ Python is not installed${NC}"
    exit 1
fi

# Verifiera Docker
echo -e "\n${YELLOW}Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker is installed${NC}"
    docker_version=$(docker --version)
    echo -e "  Version: $docker_version"
    
    # Kontrollera Docker daemon
    if docker info &> /dev/null; then
        echo -e "${GREEN}✓ Docker daemon is running${NC}"
    else
        echo -e "${RED}✗ Docker daemon is not running${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi

# Verifiera Redis
echo -e "\n${YELLOW}Checking Redis...${NC}"
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✓ Redis CLI is installed${NC}"
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis server is running${NC}"
    else
        echo -e "${RED}✗ Redis server is not running${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Redis CLI is not installed${NC}"
    exit 1
fi

# Verifiera ChromaDB
echo -e "\n${YELLOW}Checking ChromaDB...${NC}"
if python3 -c "import chromadb" &> /dev/null; then
    echo -e "${GREEN}✓ ChromaDB is installed${NC}"
else
    echo -e "${RED}✗ ChromaDB is not installed${NC}"
    exit 1
fi

# Verifiera FastAPI
echo -e "\n${YELLOW}Checking FastAPI...${NC}"
if python3 -c "import fastapi" &> /dev/null; then
    echo -e "${GREEN}✓ FastAPI is installed${NC}"
else
    echo -e "${RED}✗ FastAPI is not installed${NC}"
    exit 1
fi

# Verifiera Next.js
echo -e "\n${YELLOW}Checking Next.js...${NC}"
if [ -f "frontend/package.json" ]; then
    if grep -q "\"next\"" "frontend/package.json"; then
        echo -e "${GREEN}✓ Next.js is configured${NC}"
    else
        echo -e "${RED}✗ Next.js is not configured${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Frontend package.json not found${NC}"
    exit 1
fi

# Verifiera Prometheus
echo -e "\n${YELLOW}Checking Prometheus...${NC}"
if [ -f "monitoring/prometheus/prometheus.yml" ]; then
    echo -e "${GREEN}✓ Prometheus configuration found${NC}"
else
    echo -e "${RED}✗ Prometheus configuration not found${NC}"
    exit 1
fi

# Verifiera GitHub Actions
echo -e "\n${YELLOW}Checking GitHub Actions...${NC}"
if [ -d ".github/workflows" ]; then
    echo -e "${GREEN}✓ GitHub Actions workflows found${NC}"
else
    echo -e "${RED}✗ GitHub Actions workflows not found${NC}"
    exit 1
fi

# Verifiera Railway
echo -e "\n${YELLOW}Checking Railway...${NC}"
if command -v railway &> /dev/null; then
    echo -e "${GREEN}✓ Railway CLI is installed${NC}"
    if railway whoami &> /dev/null; then
        echo -e "${GREEN}✓ Railway CLI is authenticated${NC}"
    else
        echo -e "${RED}✗ Railway CLI is not authenticated${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Railway CLI is not installed${NC}"
    exit 1
fi

echo -e "\n${GREEN}All system components verified successfully!${NC}"

# Logga verifieringen
echo "$(date) - 01_SYSTEMÖVERSIKT: System components verified" >> logs/bootstrap_status.log 