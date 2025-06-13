#!/bin/bash

# Färger för output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Setting up environment variables...${NC}"

# Skapa .env-fil
touch .env

# Funktion för att läsa in värden
read_env_value() {
    local prompt=$1
    local var_name=$2
    local default_value=$3
    
    echo -e "${YELLOW}$prompt${NC}"
    if [ ! -z "$default_value" ]; then
        echo -e "Default value: $default_value"
        echo -e "Press Enter to use default value or type new value:"
    else
        echo -e "Enter value:"
    fi
    
    read -r new_value
    
    if [ -z "$new_value" ] && [ ! -z "$default_value" ]; then
        new_value=$default_value
    fi
    
    if [ ! -z "$new_value" ]; then
        echo "$var_name=$new_value" >> .env
    fi
}

# Database
read_env_value "Enter Database URL:" "DATABASE_URL" "postgresql://user:password@localhost:5432/geometra"
read_env_value "Enter Redis URL:" "REDIS_URL" "redis://localhost:6379/0"

# API Keys
read_env_value "Enter OpenAI API Key:" "OPENAI_API_KEY"
read_env_value "Enter Railway API Key:" "RAILWAY_API_KEY"
read_env_value "Enter API Key:" "API_KEY"

# Server
read_env_value "Enter Port:" "PORT" "8000"
read_env_value "Enter Host:" "HOST" "0.0.0.0"
read_env_value "Enable Debug Mode? (y/n):" "DEBUG" "True"

# Security
read_env_value "Enter JWT Secret:" "JWT_SECRET"
read_env_value "Enter JWT Algorithm:" "JWT_ALGORITHM" "HS256"
read_env_value "Enter Access Token Expire Minutes:" "ACCESS_TOKEN_EXPIRE_MINUTES" "30"

# Monitoring
read_env_value "Enable Metrics? (y/n):" "ENABLE_METRICS" "True"
read_env_value "Enter Prometheus Multiproc Dir:" "PROMETHEUS_MULTIPROC_DIR" "/tmp"

# Frontend
read_env_value "Enter Frontend API URL:" "REACT_APP_API_URL" "http://localhost:8000"
read_env_value "Enter Frontend Environment:" "REACT_APP_ENV" "development"

echo -e "\n${GREEN}Environment variables have been set up!${NC}"

# Logga att .env har skapats
echo "$(date) - 00_START_HÄR: Environment variables configured" >> logs/bootstrap_status.log

# Verifiera miljövariabler
echo -e "${YELLOW}Verifying environment variables...${NC}"
if [ -f .env ]; then
    source .env
    required_vars=(
        "DATABASE_URL"
        "REDIS_URL"
        "API_KEY"
        "OPENAI_API_KEY"
        "JWT_SECRET"
    )
    
    missing_vars=0
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}Missing required environment variable: $var${NC}"
            missing_vars=1
        fi
    done
    
    if [ $missing_vars -eq 0 ]; then
        echo -e "${GREEN}All required environment variables are set!${NC}"
    else
        echo -e "${RED}Some required environment variables are missing. Please check your .env file.${NC}"
        exit 1
    fi
fi 