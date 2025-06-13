#!/bin/bash

# Färger för output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Verifying system requirements...${NC}"

# Verifiera Node.js
echo -e "\n${YELLOW}Checking Node.js...${NC}"
node_version=$(node --version 2>/dev/null)
if [ $? -eq 0 ]; then
    version_num=$(echo $node_version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ $version_num -ge 18 ]; then
        echo -e "${GREEN}✓ Node.js $node_version is installed${NC}"
    else
        echo -e "${RED}✗ Node.js version must be 18 or higher${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi

# Verifiera Python
echo -e "\n${YELLOW}Checking Python...${NC}"
python_version=$(python3 --version 2>/dev/null)
if [ $? -eq 0 ]; then
    version_num=$(echo $python_version | cut -d' ' -f2)
    major=$(echo $version_num | cut -d'.' -f1)
    minor=$(echo $version_num | cut -d'.' -f2)
    if [ $major -gt 3 ] || ([ $major -eq 3 ] && [ $minor -ge 9 ]); then
        echo -e "${GREEN}✓ Python $python_version is installed${NC}"
    else
        echo -e "${RED}✗ Python version must be 3.9 or higher${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Python is not installed${NC}"
    exit 1
fi

# Verifiera pnpm
echo -e "\n${YELLOW}Checking pnpm...${NC}"
pnpm_version=$(pnpm --version 2>/dev/null)
if [ $? -eq 0 ]; then
    version_num=$(echo $pnpm_version | cut -d'.' -f1)
    if [ $version_num -ge 8 ]; then
        echo -e "${GREEN}✓ pnpm $pnpm_version is installed${NC}"
    else
        echo -e "${RED}✗ pnpm version must be 8 or higher${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ pnpm is not installed${NC}"
    exit 1
fi

# Verifiera Docker
echo -e "\n${YELLOW}Checking Docker...${NC}"
docker_version=$(docker --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker $docker_version is installed${NC}"
else
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi

# Verifiera Git
echo -e "\n${YELLOW}Checking Git...${NC}"
git_version=$(git --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Git $git_version is installed${NC}"
else
    echo -e "${RED}✗ Git is not installed${NC}"
    exit 1
fi

# Verifiera VS Code
echo -e "\n${YELLOW}Checking VS Code...${NC}"
code_version=$(code --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ VS Code is installed${NC}"
else
    echo -e "${RED}✗ VS Code is not installed${NC}"
    exit 1
fi

# Verifiera Railway CLI
echo -e "\n${YELLOW}Checking Railway CLI...${NC}"
railway_version=$(railway --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Railway CLI is installed${NC}"
else
    echo -e "${RED}✗ Railway CLI is not installed${NC}"
    exit 1
fi

# Verifiera GitHub CLI
echo -e "\n${YELLOW}Checking GitHub CLI...${NC}"
gh_version=$(gh --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ GitHub CLI is installed${NC}"
else
    echo -e "${RED}✗ GitHub CLI is not installed${NC}"
    exit 1
fi

# Verifiera API-nycklar
echo -e "\n${YELLOW}Checking API keys...${NC}"
if [ -f .env ]; then
    source .env
    if [ -n "$OPENAI_API_KEY" ]; then
        echo -e "${GREEN}✓ OpenAI API key is set${NC}"
    else
        echo -e "${RED}✗ OpenAI API key is not set${NC}"
        exit 1
    fi
    
    if [ -n "$RAILWAY_API_KEY" ]; then
        echo -e "${GREEN}✓ Railway API key is set${NC}"
    else
        echo -e "${RED}✗ Railway API key is not set${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ .env file not found${NC}"
    exit 1
fi

echo -e "\n${GREEN}All system requirements verified successfully!${NC}"

# Logga verifieringen
echo "$(date) - 00_START_HÄR: System requirements verified" >> logs/bootstrap_status.log 