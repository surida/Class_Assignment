import pandas as pd
import sys
import os
import unittest
from unittest.mock import MagicMock

# Ensure the current directory is in sys.path
sys.path.append(os.getcwd())

from class_assigner import ClassAssigner

class TestCrashFix(unittest.TestCase):
    def test_load_rules_with_few_columns(self):
        # Create a dummy Excel file with fewer columns than expected (e.g., only 5 columns)
        # Expected: Column K (index 10) needed.
        
        df = pd.DataFrame({
            0: range(5),
            1: range(5),
            2: range(5),
            3: range(5),
            4: range(5)  # Max index 4
        })
        
        test_file = "test_malformed_rules.xlsx"
        
        # Save as '규칙' sheet
        with pd.ExcelWriter(test_file) as writer:
            df.to_excel(writer, sheet_name='규칙', index=False, header=False)
            
        print(f"Created {test_file} with 5 columns.")
        
        assigner = ClassAssigner("dummy.xlsx", "dummy.xlsx")
        
        try:
            assigner._load_rules_from_sheet(test_file)
            print("SUCCESS: _load_rules_from_sheet completed without crash.")
        except IndexError as e:
            print(f"FAILED: Crash reproduced - {e}")
            self.fail(f"Crash reproduced: {e}")
        except Exception as e:
            print(f"FAILED: Other error - {e}")
            # Other errors might happen (e.g. validtion) but IndexError shouldn't
            if "single positional indexer is out-of-bounds" in str(e):
                 self.fail(f"Crash reproduced: {e}")
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

if __name__ == "__main__":
    unittest.main()
