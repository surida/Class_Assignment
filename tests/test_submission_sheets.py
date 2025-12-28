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

def test_transfer_student_sorting(temp_files):
    student_file, rules_file, output_file = temp_files
    
    # Modify data to have transfers
    df = pd.read_excel(student_file)
    # Make the first student in name order (Student_1_10?) a transfer student
    # Note: Sorting is by Name. 
    # Let's pick a student who would normally be first, and make them transfer.
    # Names are "학생_1_1", "학생_1_10"...
    # "학생_1_1" comes before "학생_1_2".
    
    # Let's explicitly set a name '가학생' to be transfer, and '나학생' to be normal.
    # '가학생' should end up AFTER '나학생'.
    
    df.loc[0, '이름'] = '가학생' # Normal sorts first
    df.loc[0, '전출'] = True   # But is transfer
    
    df.loc[1, '이름'] = '나학생'
    df.loc[1, '전출'] = False
    
    df.to_excel(student_file, index=False)
    
    assigner = ClassAssigner(student_file, rules_file, target_class_count=1) # 1 class to force them together
    assigner.run(output_file)
    
    xl = pd.ExcelFile(output_file)
    # Check 6-1 sheet (assigned class)
    df_result = pd.read_excel(output_file, sheet_name="6-1")
    
    # We expect '나학생' to come before '가학생' because '가학생' is transfer
    names = df_result['이름'].tolist()
    print(f"Sorted names: {names}")
    
    idx_ga = names.index('가학생')
    idx_na = names.index('나학생')
    
    assert idx_na < idx_ga, "Normal student should come before Transfer student regardless of name"
    
    # Also check the assigned number in 5-n sheet
    # '가학생' was originally class 1.
    df_5_1 = pd.read_excel(output_file, sheet_name="5-1")
    
    # Find row for 가학생
    row_ga = df_5_1[df_5_1['이름'] == '가학생'].iloc[0]
    row_na = df_5_1[df_5_1['이름'] == '나학생'].iloc[0]
    
    # Assigned number should be higher for Ga (Transfer) than Na
    assert row_ga['배정번호'] > row_na['배정번호']

