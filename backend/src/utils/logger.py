"""
Structured logging system for the chip-and-hole detection application.
Provides centralized logging configuration with file rotation and environment-based levels.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with file rotation and console output.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Path to log file (optional, defaults to logs/app.log)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If None, uses LOG_LEVEL from environment or defaults to INFO
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        format_string: Custom format string (optional)
    
    Returns:
        Configured logger instance
    """
    import os
    
    # Get log level
    if level is None:
        try:
            from ..config import Config
            level = Config.LOG_LEVEL.upper()
        except (ImportError, AttributeError):
            level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    log_level = getattr(logging, level, logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Default format
    if format_string is None:
        format_string = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(message)s'
        )
    
    formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')
    
    # Console handler (always output to console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (with rotation)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # Default log file location - use Config if available, otherwise relative path
        try:
            from ..config import Config
            logs_dir = Config.LOGS_DIR
        except ImportError:
            logs_dir = Path('logs')
        
        logs_dir.mkdir(parents=True, exist_ok=True)
        default_log_file = logs_dir / os.getenv("LOG_FILE", "app.log")
        
        file_handler = RotatingFileHandler(
            str(default_log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        try:
            from ..config import Config
            log_file = Config.LOG_FILE
        except (ImportError, AttributeError):
            import os
            log_file = os.getenv('LOG_FILE')
        return setup_logger(name, log_file=log_file)
    
    return logger

