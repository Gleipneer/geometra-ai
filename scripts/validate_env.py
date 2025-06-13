#!/usr/bin/env python3
import os
import sys
from pathlib import Path

REQUIRED_ENV_VARS = {
    "OPENAI_API_KEY": str,
    "FALLBACK_OPENAI_API_KEY": str,
    "CHROMA_OPENAI_API_KEY": str,
    "CHROMA_SERVER_HOST": str,
    "CHROMA_SERVER_HTTP_PORT": int,
    "REDIS_HOST": str,
    "REDIS_PORT": int,
    "REDIS_DB": int,
    "REDIS_TTL_SECONDS": int,
    "DEFAULT_MODEL": str,
    "FALLBACK_MODEL": str,
    "MAX_TOKENS": int,
    "TEMPERATURE": float,
    "LOG_LEVEL": str,
    "LOG_DIR": str,
    "API_KEYS": str,
    "RATE_LIMIT_PER_MINUTE": int,
    "ENV": str,
    "RAILWAY_PROJECT_NAME": str,
    "RAILWAY_ENVIRONMENT": str,
    "ENABLE_SYSTEM_CHECK": lambda v: v.lower() in ["true", "false"],
    "SYSTEM_CHECK_INTERVAL_SECONDS": int,
    "CI_COMMIT_TAG": str,
    "CI_DEPLOY_BRANCH": str,
    "MEMORY_CONTEXT_WINDOW": int,
    "DEBUG_MODE": lambda v: v.lower() in ["true", "false"],
}

def colored(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def safe_convert(value, expected_type):
    """Safely convert a value to the expected type."""
    try:
        if callable(expected_type):
            return expected_type(value)
        elif expected_type == int:
            return int(float(value))  # Handle both int and float strings
        elif expected_type == float:
            return float(value)
        else:
            return expected_type(value)
    except (ValueError, TypeError):
        return None

def validate_env():
    all_ok = True
    errors = []

    print(colored("🔍 VALIDATING .env VARIABLES:\n", "1;36"))

    # First pass: Check if all variables exist
    for key in REQUIRED_ENV_VARS:
        if key not in os.environ:
            print(colored(f"✗ MISSING: {key}", "1;31"))
            errors.append(f"Missing required variable: {key}")
            all_ok = False

    # Second pass: Validate types and values
    for key, expected_type in REQUIRED_ENV_VARS.items():
        value = os.environ.get(key)
        if value is not None:
            converted_value = safe_convert(value, expected_type)
            if converted_value is None:
                print(colored(f"✗ INVALID FORMAT: {key} = {value} (expected {expected_type.__name__})", "1;31"))
                errors.append(f"Invalid format for {key}: got '{value}', expected {expected_type.__name__}")
                all_ok = False
            else:
                # Mask sensitive values
                display_value = value
                if "API_KEY" in key:
                    display_value = f"{value[:8]}...{value[-4:]}"
                print(colored(f"✓ OK: {key} = {display_value}", "1;32"))

    # Check if LOG_DIR exists
    log_dir = os.environ.get("LOG_DIR", "logs")
    if not Path(log_dir).exists():
        print(colored(f"⚠️ LOG_DIR '{log_dir}' does not exist. Creating it...", "1;33"))
        try:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            print(colored(f"✓ Created LOG_DIR: {log_dir}", "1;32"))
        except Exception as e:
            print(colored(f"✗ Failed to create LOG_DIR: {e}", "1;31"))
            errors.append(f"Failed to create LOG_DIR: {e}")
            all_ok = False

    # Final status
    if all_ok:
        print(colored("\n✅ All environment variables are valid!", "1;32"))
    else:
        print(colored("\n❌ Validation failed:", "1;31"))
        for error in errors:
            print(colored(f"  - {error}", "1;31"))
        print(colored("\nPlease fix the above issues and run the validation again.", "1;31"))
        sys.exit(1)

if __name__ == "__main__":
    validate_env()
