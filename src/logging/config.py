import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging():
    """Configure system logging."""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Configure test logger
    test_logger = logging.getLogger("test_logger")
    test_logger.setLevel(logging.DEBUG)
    
    # Add handlers to test logger
    test_console_handler = logging.StreamHandler()
    test_console_handler.setLevel(logging.DEBUG)
    test_console_handler.setFormatter(console_formatter)
    test_logger.addHandler(test_console_handler)
    
    test_file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "test.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    test_file_handler.setLevel(logging.DEBUG)
    test_file_handler.setFormatter(file_formatter)
    test_logger.addHandler(test_file_handler)
    
    return root_logger

# Create test logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)
