import pandas as pd
import os

file1 = "/Users/kwansooahn/WorkSpace/Class_Assignment 2/02 분반 합반할 학생 규칙.xlsx"
file2 = "/Users/kwansooahn/WorkSpace/Class_Assignment 2/crash-issue/02 분반 합반 규칙(실전_이름 바꿈).xlsx"

def inspect_file(filepath):
    print(f"\n--- Intepecting: {os.path.basename(filepath)} ---")
    if not os.path.exists(filepath):
        print("File not found.")
        return

    try:
        # Load exactly as load_rules does
        df = pd.read_excel(filepath, sheet_name='Sheet1')
        print("Columns:", df.columns.tolist())
        print("Shape:", df.shape)
        
        # Check expected columns
        expected = ['Unnamed: 1', 'Unnamed: 4', 'Unnamed: 7', 'Unnamed: 10']
        missing = [col for col in expected if col not in df.columns]
        if missing:
            print(f"❌ Missing columns: {missing}")
        else:
            print("✅ All expected columns present.")
            
    except Exception as e:
        print(f"Error reading file: {e}")

inspect_file(file1)
inspect_file(file2)
