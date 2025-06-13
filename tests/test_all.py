"""Run all tests in sequence."""

import pytest
import sys
from pathlib import Path
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_test_result(test_name, result):
    """Log test result to file."""
    log_file = Path("logs/test_results.json")
    if not log_file.exists():
        results = []
    else:
        with open(log_file) as f:
            results = json.load(f)
    
    results.append({
        "test": test_name,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })
    
    with open(log_file, "w") as f:
        json.dump(results, f, indent=2)

def run_test_suite(suite_name, test_path):
    """Run a test suite and log results."""
    logger.info(f"Running {suite_name} tests...")
    try:
        result = pytest.main([str(test_path), "-v"])
        status = "passed" if result == 0 else "failed"
        logger.info(f"{suite_name} tests {status}")
        log_test_result(suite_name, status)
        return result == 0
    except Exception as e:
        logger.error(f"Error running {suite_name} tests: {str(e)}")
        log_test_result(suite_name, "error")
        return False

def test_system_setup():
    """Test system setup."""
    return run_test_suite("System Setup", "tests/unit/system")

def test_installation():
    """Test installation."""
    return run_test_suite("Installation", "tests/unit/installation")

def test_backend_setup():
    """Test backend setup."""
    return run_test_suite("Backend Setup", "tests/unit/backend")

def test_frontend_setup():
    """Test frontend setup."""
    return run_test_suite("Frontend Setup", "tests/unit/frontend")

def test_ai_setup():
    """Test AI setup."""
    return run_test_suite("AI Setup", "tests/unit/ai")

def test_database_setup():
    """Test database setup."""
    return run_test_suite("Database Setup", "tests/unit/db")

def test_api_setup():
    """Test API setup."""
    return run_test_suite("API Setup", "tests/unit/api")

def test_auth_setup():
    """Test authentication setup."""
    return run_test_suite("Authentication Setup", "tests/unit/auth")

def test_logging_setup():
    """Test logging setup."""
    return run_test_suite("Logging Setup", "tests/unit/logging")

def test_integration():
    """Test integration."""
    return run_test_suite("Integration", "tests/integration")

def test_e2e():
    """Test end-to-end."""
    return run_test_suite("End-to-End", "tests/e2e")

def test_all():
    """Run all tests in sequence."""
    logger.info("Starting test suite...")
    
    # Create test results directory
    Path("logs").mkdir(exist_ok=True)
    
    # Define test sequence
    test_sequence = [
        ("System Setup", test_system_setup),
        ("Installation", test_installation),
        ("Backend Setup", test_backend_setup),
        ("Frontend Setup", test_frontend_setup),
        ("AI Setup", test_ai_setup),
        ("Database Setup", test_database_setup),
        ("API Setup", test_api_setup),
        ("Authentication Setup", test_auth_setup),
        ("Logging Setup", test_logging_setup),
        ("Integration", test_integration),
        ("End-to-End", test_e2e)
    ]
    
    # Run tests in sequence
    results = {}
    for name, test_func in test_sequence:
        logger.info(f"Starting {name}...")
        result = test_func()
        results[name] = result
        if not result:
            logger.error(f"{name} failed. Stopping test sequence.")
            break
        logger.info(f"{name} completed successfully.")
    
    # Generate test report
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "status": "success" if all(results.values()) else "failure"
    }
    
    with open("logs/test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info("Test suite completed.")
    return all(results.values())

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1) 