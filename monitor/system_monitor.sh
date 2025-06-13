#!/bin/bash

# Loggning
LOG_FILE="monitor/logs/system_monitor.log"
ERROR_LOG="monitor/logs/error.log"

# Konfiguration
API_URL="https://api.geometra.ai"
CHROMA_URL="https://api.geometra.ai/memory/chroma"
REDIS_URL="https://api.geometra.ai/memory/redis"
ALERT_EMAIL="alerts@geometra.ai"
SLACK_WEBHOOK="https://hooks.slack.com/..."

# Färger för output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Loggning
log() {
    echo "$(date) - $1" >> "$LOG_FILE"
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo "$(date) - ERROR: $1" >> "$ERROR_LOG"
    echo -e "${RED}✗ $1${NC}"
    # Skicka alert
    send_alert "$1"
}

warning() {
    echo "$(date) - WARNING: $1" >> "$LOG_FILE"
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Skicka alerts
send_alert() {
    # Slack
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"🚨 $1\"}" \
        "$SLACK_WEBHOOK"
    
    # Email
    echo "Alert: $1" | mail -s "Geometra AI Alert" "$ALERT_EMAIL"
}

# Kontrollera API
check_api() {
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")
    if [ "$response" -eq 200 ]; then
        log "API är online"
    else
        error "API är offline (Status: $response)"
    fi
}

# Kontrollera minne
check_memory() {
    # ChromaDB
    chroma_status=$(curl -s "$CHROMA_URL/status")
    if [ "$chroma_status" = "ok" ]; then
        log "ChromaDB är online"
    else
        error "ChromaDB är offline"
    fi
    
    # Redis
    redis_status=$(curl -s "$REDIS_URL/status")
    if [ "$redis_status" = "ok" ]; then
        log "Redis är online"
    else
        error "Redis är offline"
    fi
}

# Kontrollera RAM
check_ram() {
    total_ram=$(free -m | awk '/^Mem:/{print $2}')
    used_ram=$(free -m | awk '/^Mem:/{print $3}')
    ram_percent=$((used_ram * 100 / total_ram))
    
    if [ "$ram_percent" -gt 90 ]; then
        error "RAM-användning är kritisk: $ram_percent%"
    elif [ "$ram_percent" -gt 80 ]; then
        warning "RAM-användning är hög: $ram_percent%"
    else
        log "RAM-användning är OK: $ram_percent%"
    fi
}

# Kontrollera portar
check_ports() {
    # API port
    if nc -z localhost 8000; then
        log "API port (8000) är öppen"
    else
        error "API port (8000) är stängd"
    fi
    
    # Redis port
    if nc -z localhost 6379; then
        log "Redis port (6379) är öppen"
    else
        error "Redis port (6379) är stängd"
    fi
    
    # ChromaDB port
    if nc -z localhost 8000; then
        log "ChromaDB port (8000) är öppen"
    else
        error "ChromaDB port (8000) är stängd"
    fi
}

# Kontrollera token-avgifter
check_token_usage() {
    usage=$(curl -s "$API_URL/metrics/tokens")
    if [ "$usage" -gt 1000000 ]; then
        warning "Token-användning är hög: $usage"
    else
        log "Token-användning är OK: $usage"
    fi
}

# Huvudfunktion
main() {
    log "Startar system monitoring..."
    
    # Kör alla kontroller
    check_api
    check_memory
    check_ram
    check_ports
    check_token_usage
    
    log "Monitoring slutförd"
}

# Kör huvudfunktionen
main

# Kör som cron job
# */5 * * * * /path/to/system_monitor.sh 