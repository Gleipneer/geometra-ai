#!/usr/bin/env python3
"""
Verifierar att alla nödvändiga miljövariabler är satta.
"""

import os
from dotenv import load_dotenv
import sys

def verify_env_variables():
    """Verifierar att alla nödvändiga miljövariabler är satta."""
    required_vars = [
        'REDIS_URL',
        'POSTGRES_URL',
        'API_HOST',
        'API_PORT',
        'JWT_SECRET_KEY',
        'OPENAI_API_KEY',
        'CHROMA_PERSIST_DIRECTORY',
        'LOG_LEVEL',
        'LOG_FILE'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Saknade miljövariabler:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    print("✅ Alla nödvändiga miljövariabler är satta")
    return True

def main():
    """Huvudfunktion."""
    # Ladda .env-fil
    if not load_dotenv():
        print("❌ Kunde inte hitta .env-fil")
        sys.exit(1)
    
    # Verifiera miljövariabler
    if not verify_env_variables():
        sys.exit(1)

if __name__ == "__main__":
    main() 