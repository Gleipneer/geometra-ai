#!/bin/bash

# System check script for Geometra AI
# Verifies system health, dependencies, and security components

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Log file
LOG_FILE="bootstrap_status.log"

# Create logs directory if it doesn't exist
[ -d logs ] || mkdir -p logs
[ -d monitor/logs ] || mkdir -p monitor/logs
[ -d tests/logs ] || mkdir -p tests/logs

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$LOG_FILE"
    echo -e "${RED}✗${NC} $1"
    return 1
}

warning() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1" >> "$LOG_FILE"
    echo -e "${YELLOW}⚠${NC} $1"
}

# API Check
check_api() {
    log "Checking API..."
    if curl -s http://localhost:8000/health > /dev/null; then
        log "API is online"
        return 0
    else
        error "API is offline"
        return 1
    fi
}

# Memory Check
check_memory() {
    log "Checking memory systems..."
    
    # ChromaDB
    if curl -s http://localhost:8000/api/v1/memory/chroma/health > /dev/null; then
        log "ChromaDB is online"
    else
        error "ChromaDB is offline"
        return 1
    fi
    
    # Redis
    if redis-cli ping > /dev/null; then
        log "Redis is online"
    else
        error "Redis is offline"
        return 1
    fi
    
    return 0
}

# OpenAI Check
check_openai() {
    log "Checking OpenAI..."
    if python3 -c "
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client.models.list()
" > /dev/null; then
        log "OpenAI is online"
        return 0
    else
        error "OpenAI is offline"
        return 1
    fi
}

# Docker Check
check_docker() {
    log "Checking Docker..."
    if docker info > /dev/null 2>&1; then
        log "Docker is online"
        return 0
    else
        error "Docker is offline"
        return 1
    fi
}

# Monitoring Check
check_monitoring() {
    log "Checking monitoring system..."
    
    # Check monitoring script
    if [ -f "monitoring/scripts/monitor.py" ]; then
        log "Monitoring script exists"
    else
        error "Monitoring script not found"
        return 1
    fi
    
    # Check monitoring config
    if [ -f "monitoring/config/monitoring_config.yml" ]; then
        log "Monitoring config exists"
    else
        error "Monitoring config not found"
        return 1
    fi
    
    # Check log rotation
    if [ -f "monitoring/config/logrotate.conf" ]; then
        log "Log rotation config exists"
    else
        error "Log rotation config not found"
        return 1
    fi
    
    # Check systemd service
    if [ -f "monitoring/config/geometra-monitor.service" ]; then
        log "Systemd service config exists"
    else
        error "Systemd service config not found"
        return 1
    fi
    
    return 0
}

# Environment Check
check_environment() {
    log "Checking environment variables..."
    
    required_vars=(
        "OPENAI_API_KEY"
        "REDIS_URL"
        "DATABASE_URL"
        "RAILWAY_API_KEY"
    )
    
    missing_vars=0
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            warning "Environment variable $var is not set"
            missing_vars=1
        else
            log "Environment variable $var is set"
        fi
    done
    
    return $missing_vars
}

# Main function
main() {
    log "Starting system check..."
    
    # Create a temporary file for results
    TEMP_FILE=$(mktemp)
    
    # Run all checks and collect results
    {
        check_docker
        check_api
        check_memory
        check_openai
        check_monitoring
        check_environment
    } 2>&1 | tee "$TEMP_FILE"
    
    # Check if any checks failed
    if grep -q "ERROR" "$TEMP_FILE"; then
        error "System check failed - see above for details"
        rm "$TEMP_FILE"
        exit 1
    else
        log "All system checks passed successfully!"
        rm "$TEMP_FILE"
        exit 0
    fi
}

# Run main function
main 