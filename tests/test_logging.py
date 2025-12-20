import logging
import os
import sys
# Ensure the current directory is in sys.path
sys.path.append(os.getcwd())

from logger_config import logger

def test_logging():
    print("Testing logging...")
    
    # Log a standard message
    logger.info("Test Info Message")
    logger.debug("Test Debug Message")
    
    # Simulate an exception
    try:
        1 / 0
    except ZeroDivisionError:
        logger.error("Test ZeroDivisionError", exc_info=True)
        
    # Check if file exists
    if os.path.exists("class_assigner_debug.log"):
        print("Log file created successfully.")
        with open("class_assigner_debug.log", "r") as f:
            content = f.read()
            print("\n--- Log File Content ---")
            print(content)
            print("------------------------")
            
            if "Test Info Message" in content and "Test ZeroDivisionError" in content:
                print("Verification SUCCESS: Logs found in file.")
            else:
                print("Verification FAILED: Logs not found in file.")
    else:
        print("Verification FAILED: Log file not created.")

if __name__ == "__main__":
    test_logging()
