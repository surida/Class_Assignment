import logging
import os
import sys
import platform

from logging.handlers import RotatingFileHandler


def get_app_data_dir():
    """OS별 앱 데이터 폴더 반환 (권한 문제 없는 사용자 폴더)"""
    system = platform.system()

    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif system == "Darwin":  # Mac
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:  # Linux
        base = os.path.join(os.path.expanduser("~"), ".local", "share")

    app_dir = os.path.join(base, "ClassAssigner")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def get_log_dir():
    """로그 폴더 반환"""
    log_dir = os.path.join(get_app_data_dir(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def setup_logging():
    """
    Sets up logging to user data folder with rotation and console output.
    - Windows: %APPDATA%/ClassAssigner/logs/
    - Mac: ~/Library/Application Support/ClassAssigner/logs/
    - Linux: ~/.local/share/ClassAssigner/logs/
    """
    # Ensure logs directory exists in user data folder
    log_dir = get_log_dir()
        
    log_file = os.path.join(log_dir, "class_assigner.log")
    
    # Create logger
    logger = logging.getLogger("ClassAssigner")
    logger.setLevel(logging.DEBUG)
    
    # Check if handlers are already added to avoid duplicates
    if not logger.handlers:
        # File Handler (Reset on startup)
        try:
            # use FileHandler with mode='w' to clear previous logs
            file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
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
