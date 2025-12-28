import pytest
import pandas as pd
import os
import shutil
from class_assigner import ClassAssigner

@pytest.fixture
def temp_files(tmp_path):
    # Setup dummy student data
    student_file = tmp_path / "students.xlsx"
    rules_file = tmp_path / "rules.xlsx"
    output_file = tmp_path / "output_test.xlsx"

    # Create dummy student data
    data = []
    # 5학년 1반 10명, 2반 10명
    for cls in [1, 2]:
        for i in range(1, 11):
            data.append({
                '학년': 5,
                '반': cls,
                '번호': i,
                '이름': f"학생_{cls}_{i}",
                '성별': '남' if i % 2 == 0 else '여',
                '점수': 80 + i,
                '특수반': False,
                '전출': False,
                '난이도': 0,
                '비고': ''
            })
    
    df = pd.DataFrame(data)
    df.to_excel(student_file, index=False)
    
    # Create empty rules file
    pd.DataFrame().to_excel(rules_file, index=False)
    
    return str(student_file), str(rules_file), str(output_file)

def test_submission_sheets_generated(temp_files):
    student_file, rules_file, output_file = temp_files
    
    assigner = ClassAssigner(student_file, rules_file, target_class_count=2)
    assigner.run(output_file)
    
    assert os.path.exists(output_file)
    
    xl = pd.ExcelFile(output_file)
    print(f"Generated sheets: {xl.sheet_names}")
    
    # Check 5-n sheets exist
    assert "5-1" in xl.sheet_names
    assert "5-2" in xl.sheet_names
    
    # Check content of 5-1
    df_5_1 = pd.read_excel(output_file, sheet_name="5-1")
    assert '배정반' in df_5_1.columns
    assert '배정번호' in df_5_1.columns
    
    # Check 6-n sheets exist
    assert "6-1" in xl.sheet_names
    assert "6-2" in xl.sheet_names

def test_smart_loading(temp_files):
    student_file, rules_file, output_file = temp_files
    
    # First run to generate output with mixed sheets (5-x and 6-x)
    assigner = ClassAssigner(student_file, rules_file, target_class_count=2)
    assigner.run(output_file)
    
    # Try to load from the result file
    # This should ONLY load 6-x sheets and ignore 5-x sheets
    assigner_loader = ClassAssigner(student_file, rules_file)
    assigner_loader.load_from_result(output_file)
    
    # target_class_count shoud be 2 (detected from 6-1, 6-2)
    # If it wrongly detected 5-1, 5-2, it might be confused or error out if logic was flawed
    assert assigner_loader.target_class_count == 2
    assert len(assigner_loader.classes) == 2
    
    # Verify loaded students correspond to 6th grade (assigned_class should match)
    # Since we loaded from result, all students should have assigned_class set
    for s in assigner_loader.students:
        assert s.assigned_class is not None
        
    print("Smart loading validation successful")
