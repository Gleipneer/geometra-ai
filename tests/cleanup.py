"""Cleanup routine for test environment."""

import os
import shutil
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='bootstrap_status.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_status(message: str, level: str = 'INFO'):
    """Log status message."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    
    if level == 'ERROR':
        logging.error(log_message)
        print(f"\033[91m{log_message}\033[0m")  # Red
    elif level == 'WARNING':
        logging.warning(log_message)
        print(f"\033[93m{log_message}\033[0m")  # Yellow
    else:
        logging.info(log_message)
        print(f"\033[92m{log_message}\033[0m")  # Green

def cleanup_test_environment():
    """Clean up test environment before running tests."""
    try:
        # Clean up __pycache__ directories
        for cache_dir in Path('.').rglob('__pycache__'):
            shutil.rmtree(cache_dir)
            log_status(f"Removed {cache_dir}")
            
        # Clean up .pytest_cache
        pytest_cache = Path('.pytest_cache')
        if pytest_cache.exists():
            shutil.rmtree(pytest_cache)
            log_status("Removed .pytest_cache")
            
        # Clean up test coverage files
        coverage_file = Path('.coverage')
        if coverage_file.exists():
            coverage_file.unlink()
            log_status("Removed .coverage")
            
        # Clean up HTML coverage report
        htmlcov_dir = Path('htmlcov')
        if htmlcov_dir.exists():
            shutil.rmtree(htmlcov_dir)
            log_status("Removed htmlcov directory")
            
        # Clean up temporary test files
        temp_dirs = [
            'logs/generated_modules',
            'tests/tmp',
            'tests/fixtures/temp'
        ]
        
        for temp_dir in temp_dirs:
            temp_path = Path(temp_dir)
            if temp_path.exists():
                shutil.rmtree(temp_path)
                log_status(f"Removed {temp_dir}")
                
        # Create necessary directories
        for dir_path in temp_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            log_status(f"Created {dir_path}")
            
        # Clear bootstrap_status.log
        with open('bootstrap_status.log', 'w') as f:
            f.write(f"=== Test run started at {datetime.now()} ===\n")
        log_status("Cleared bootstrap_status.log")
        
        # Verify environment variables
        required_vars = [
            'PYTHONPATH',
            'OPENAI_API_KEY',
            'REDIS_URL',
            'POSTGRES_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            log_status(
                f"Warning: Missing environment variables: {', '.join(missing_vars)}",
                level='WARNING'
            )
            
        # Verify Python packages
        required_packages = [
            'pytest',
            'pytest-cov',
            'pytest-mock',
            'pytest-asyncio',
            'pytest-xdist'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            log_status(
                f"Warning: Missing Python packages: {', '.join(missing_packages)}",
                level='WARNING'
            )
            
        log_status("Cleanup completed successfully")
        return True
        
    except Exception as e:
        log_status(f"Error during cleanup: {str(e)}", level='ERROR')
        return False

if __name__ == '__main__':
    cleanup_test_environment() 