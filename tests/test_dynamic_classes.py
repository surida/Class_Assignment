"""
dynamic_classes_test 함수 테스트
동적 학급 수 설정 (target_class_count) 테스트
"""

import pytest
import sys
import os
from collections import defaultdict

# 상위 디렉토리의 class_assigner 모듈 import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from class_assigner import ClassAssigner, Student

@pytest.fixture
def mock_students_dynamic():
    """테스트용 학생 리스트 (60명)"""
    students = []
    for i in range(60):
        student = Student(
            학년=5,
            원반=(i % 5) + 1,
            원번호=i // 5 + 1,
            이름=f'학생{i+1}',
            성별='남' if i % 2 == 0 else '여',
            점수=90,
            특수반=False,
            전출=False,
            난이도=0.0,
            비고=""
        )
        students.append(student)
    return students

def test_assign_to_6_classes(mock_students_dynamic):
    """테스트 1: 6개 반으로 배정"""
    target_count = 6
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.students = mock_students_dynamic
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.target_class_count = target_count
    assigner.classes = {i: [] for i in range(1, target_count + 1)}
    assigner.special_student_weight = 3.0

    # Phase 5 (balance remaining) simulates the full assignment for basic distribution
    assigner.phase5_balance_remaining()

    # 모든 학생 배정 확인
    assert all(s.assigned_class is not None for s in assigner.students)

    # 1~6반에만 배정되었는지 확인
    classes = {s.assigned_class for s in assigner.students}
    assert classes == set(range(1, target_count + 1))
    
    # 균등 배분 확인 (60명 / 6반 = 10명씩)
    for c in range(1, target_count + 1):
        assert len(assigner.classes[c]) == 10

def test_assign_to_8_classes(mock_students_dynamic):
    """테스트 2: 8개 반으로 배정"""
    target_count = 8
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.students = mock_students_dynamic
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.target_class_count = target_count
    assigner.classes = {i: [] for i in range(1, target_count + 1)}
    assigner.special_student_weight = 3.0

    assigner.phase5_balance_remaining()

    # 모든 학생 배정 확인
    assert all(s.assigned_class is not None for s in assigner.students)

    # 1~8반에만 배정되었는지 확인
    classes = {s.assigned_class for s in assigner.students}
    assert classes == set(range(1, target_count + 1))

    # 균등 배분 확인 (60명 / 8반 = 7.5명 -> 7명 또는 8명)
    class_sizes = [len(assigner.classes[c]) for c in range(1, target_count + 1)]
    assert max(class_sizes) - min(class_sizes) <= 1
