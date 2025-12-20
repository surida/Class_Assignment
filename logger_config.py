import logging
import os
import sys

def setup_logging():
    """
    Sets up logging to a file 'class_assigner_debug.log' and also to console.
    """
    log_file = "class_assigner_debug.log"
    
    # Create logger
    logger = logging.getLogger("ClassAssigner")
    logger.setLevel(logging.DEBUG)
    
    # Check if handlers are already added to avoid duplicates
    if not logger.handlers:
        # File Handler
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to setup file logging: {e}")

        # Console Handler (Optional, for development)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

# Create a global logger instance
logger = setup_logging()

def log_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    Handler for uncaught exceptions to log them before crashing.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught Exception", exc_info=(exc_type, exc_value, exc_traceback))

# Set the global exception hook
sys.excepthook = log_uncaught_exception
