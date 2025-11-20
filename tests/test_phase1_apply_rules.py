"""
phase1_apply_rules 함수 테스트
합반/분반 규칙 적용 로직 테스트
"""

import pytest
from collections import defaultdict
import sys
import os

# 상위 디렉토리의 class_assigner 모듈 import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from class_assigner import ClassAssigner, Student


@pytest.fixture
def mock_students():
    """테스트용 Student 객체 리스트 생성"""
    students = []
    names = ['학생A', '학생B', '학생C', '학생D', '학생E', '학생F', '학생G', '학생H']

    for i, name in enumerate(names):
        student = Student(
            학년=5,
            원반=1,
            원번호=i + 1,
            이름=name,
            성별='남' if i % 2 == 0 else '여',
            점수=85 + i,
            특수반=False,
            전출=False,
            난이도=0.0,
            비고=""
        )
        students.append(student)

    return students


@pytest.fixture
def phase1_assigner(mock_students):
    """phase1 테스트용 ClassAssigner 인스턴스"""
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.students = mock_students
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.classes = {i: [] for i in range(1, 8)}
    return assigner


# ============================================================================
# 합반 그룹 테스트
# ============================================================================

def test_empty_rules(phase1_assigner):
    """테스트 1: 빈 규칙 - 아무도 배정되지 않음"""
    phase1_assigner.phase1_apply_rules()

    # 아무도 배정되지 않아야 함
    assigned_count = sum(1 for s in phase1_assigner.students if s.assigned_class is not None)
    assert assigned_count == 0


def test_single_together_group(phase1_assigner):
    """테스트 2: 단일 합반 그룹 - 같은 반에 배정"""
    phase1_assigner.together_groups = [{'학생A', '학생B'}]

    phase1_assigner.phase1_apply_rules()

    학생A = phase1_assigner._find_student_by_name('학생A')
    학생B = phase1_assigner._find_student_by_name('학생B')

    # 같은 반에 배정되어야 함
    assert 학생A.assigned_class is not None
    assert 학생A.assigned_class == 학생B.assigned_class

    # 잠금 설정 확인
    assert 학생A.locked == True
    assert 학생B.locked == True


def test_together_group_to_smallest_class(phase1_assigner):
    """테스트 3: 합반 그룹이 학생 수가 가장 적은 반에 배정"""
    # 1반에 먼저 1명 배정
    phase1_assigner.classes[1].append(phase1_assigner.students[0])
    phase1_assigner.students[0].assigned_class = 1

    # 2반에 2명 배정
    phase1_assigner.classes[2].append(phase1_assigner.students[1])
    phase1_assigner.students[1].assigned_class = 2
    phase1_assigner.classes[2].append(phase1_assigner.students[2])
    phase1_assigner.students[2].assigned_class = 2

    # 합반 그룹 (3, 4번 학생)
    phase1_assigner.together_groups = [{'학생D', '학생E'}]

    phase1_assigner.phase1_apply_rules()

    학생D = phase1_assigner._find_student_by_name('학생D')
    학생E = phase1_assigner._find_student_by_name('학생E')

    # 3반(0명)에 배정되어야 함 (가장 학생 수가 적음)
    assert 학생D.assigned_class == 3
    assert 학생E.assigned_class == 3


def test_together_students_locked(phase1_assigner):
    """테스트 4: 합반 그룹 학생들이 locked=True"""
    phase1_assigner.together_groups = [{'학생A', '학생B', '학생C'}]

    phase1_assigner.phase1_apply_rules()

    for name in ['학생A', '학생B', '학생C']:
        student = phase1_assigner._find_student_by_name(name)
        assert student.locked == True


def test_multiple_together_groups(phase1_assigner):
    """테스트 5: 여러 합반 그룹 - 각각 다른 반에 배정"""
    phase1_assigner.together_groups = [
        {'학생A', '학생B'},
        {'학생C', '학생D'},
        {'학생E', '학생F'}
    ]

    phase1_assigner.phase1_apply_rules()

    # 각 그룹의 학생들
    학생A = phase1_assigner._find_student_by_name('학생A')
    학생B = phase1_assigner._find_student_by_name('학생B')
    학생C = phase1_assigner._find_student_by_name('학생C')
    학생D = phase1_assigner._find_student_by_name('학생D')
    학생E = phase1_assigner._find_student_by_name('학생E')
    학생F = phase1_assigner._find_student_by_name('학생F')

    # 그룹 1: A, B가 같은 반
    assert 학생A.assigned_class == 학생B.assigned_class

    # 그룹 2: C, D가 같은 반
    assert 학생C.assigned_class == 학생D.assigned_class

    # 그룹 3: E, F가 같은 반
    assert 학생E.assigned_class == 학생F.assigned_class

    # 각 그룹은 다른 반에 배정 (학생 수가 적은 반 순서로)
    assert 학생A.assigned_class != 학생C.assigned_class
    assert 학생C.assigned_class != 학생E.assigned_class


# ============================================================================
# 분반 규칙 테스트
# ============================================================================

def test_separation_rule_applied(phase1_assigner):
    """테스트 6: 분반 규칙 적용 - 다른 반에 배정"""
    # 학생A를 1반에 미리 배정
    phase1_assigner.together_groups = [{'학생A'}]
    phase1_assigner.separation_rules = defaultdict(set, {
        '학생A': {'학생B'},
        '학생B': {'학생A'}
    })

    phase1_assigner.phase1_apply_rules()

    학생A = phase1_assigner._find_student_by_name('학생A')
    학생B = phase1_assigner._find_student_by_name('학생B')

    # 학생A는 배정됨
    assert 학생A.assigned_class is not None

    # 학생B도 배정되고, 학생A와 다른 반
    assert 학생B.assigned_class is not None
    assert 학생A.assigned_class != 학생B.assigned_class

    # 둘 다 잠김
    assert 학생A.locked == True
    assert 학생B.locked == True


def test_separation_after_together(phase1_assigner):
    """테스트 7: 합반 후 분반 규칙 적용"""
    # 합반: A, B가 같은 반
    # 분반: A ↔ C
    phase1_assigner.together_groups = [{'학생A', '학생B'}]
    phase1_assigner.separation_rules = defaultdict(set, {
        '학생A': {'학생C'},
        '학생C': {'학생A'}
    })

    phase1_assigner.phase1_apply_rules()

    학생A = phase1_assigner._find_student_by_name('학생A')
    학생B = phase1_assigner._find_student_by_name('학생B')
    학생C = phase1_assigner._find_student_by_name('학생C')

    # A, B는 같은 반
    assert 학생A.assigned_class == 학생B.assigned_class

    # C는 A와 다른 반
    assert 학생C.assigned_class is not None
    assert 학생C.assigned_class != 학생A.assigned_class


def test_separation_applies_to_unassigned_only(phase1_assigner):
    """테스트 8: 분반 규칙은 미배정 학생에게만 적용됨"""
    # 학생A를 합반으로 먼저 배정
    phase1_assigner.together_groups = [{'학생A'}]

    # A ↔ C 분반 규칙 설정
    phase1_assigner.separation_rules = defaultdict(set, {
        '학생A': {'학생C'},
        '학생C': {'학생A'}
    })

    # 학생B를 미리 다른 로직으로 배정했다고 가정 (phase1 외부)
    학생B = phase1_assigner._find_student_by_name('학생B')
    phase1_assigner.classes[5].append(학생B)
    학생B.assigned_class = 5
    학생B.locked = True

    phase1_assigner.phase1_apply_rules()

    학생A = phase1_assigner._find_student_by_name('학생A')
    학생C = phase1_assigner._find_student_by_name('학생C')

    # 학생A는 배정됨
    assert 학생A.assigned_class is not None

    # 학생C는 분반 규칙으로 A와 다른 반에 배정됨
    assert 학생C.assigned_class is not None
    assert 학생C.assigned_class != 학생A.assigned_class
    assert 학생C.locked == True

    # 학생B는 이미 배정되어 있어서 phase1에서 건드리지 않음
    assert 학생B.assigned_class == 5
    assert 학생B.locked == True


# ============================================================================
# 예외 및 엣지 케이스
# ============================================================================

def test_student_not_found_warning(phase1_assigner, capsys):
    """테스트 9: 명단에 없는 학생 경고"""
    phase1_assigner.together_groups = [{'학생A', '존재하지않는학생'}]

    phase1_assigner.phase1_apply_rules()

    # 경고 메시지 확인
    captured = capsys.readouterr()
    assert "존재하지않는학생" in captured.out
    assert "명단에서 찾을 수 없습니다" in captured.out

    # 학생A는 정상 배정
    학생A = phase1_assigner._find_student_by_name('학생A')
    assert 학생A.assigned_class is not None


def test_empty_together_group_after_not_found(phase1_assigner):
    """테스트 10: 모든 학생이 명단에 없는 합반 그룹"""
    phase1_assigner.together_groups = [{'없는학생1', '없는학생2'}]

    phase1_assigner.phase1_apply_rules()

    # 아무도 배정되지 않아야 함
    assigned_count = sum(1 for s in phase1_assigner.students if s.assigned_class is not None)
    assert assigned_count == 0


def test_complex_scenario(phase1_assigner):
    """테스트 11: 복합 시나리오 - 합반 + 분반 동시 적용"""
    # 합반: (A, B), (C, D)
    # 분반: A ↔ E, C ↔ F
    phase1_assigner.together_groups = [
        {'학생A', '학생B'},
        {'학생C', '학생D'}
    ]
    phase1_assigner.separation_rules = defaultdict(set, {
        '학생A': {'학생E'},
        '학생E': {'학생A'},
        '학생C': {'학생F'},
        '학생F': {'학생C'}
    })

    phase1_assigner.phase1_apply_rules()

    학생A = phase1_assigner._find_student_by_name('학생A')
    학생B = phase1_assigner._find_student_by_name('학생B')
    학생C = phase1_assigner._find_student_by_name('학생C')
    학생D = phase1_assigner._find_student_by_name('학생D')
    학생E = phase1_assigner._find_student_by_name('학생E')
    학생F = phase1_assigner._find_student_by_name('학생F')

    # 합반 그룹 검증
    assert 학생A.assigned_class == 학생B.assigned_class
    assert 학생C.assigned_class == 학생D.assigned_class

    # 분반 규칙 검증
    assert 학생E.assigned_class != 학생A.assigned_class
    assert 학생F.assigned_class != 학생C.assigned_class

    # 모두 잠김
    for name in ['학생A', '학생B', '학생C', '학생D', '학생E', '학생F']:
        student = phase1_assigner._find_student_by_name(name)
        assert student.locked == True


def test_assigned_count_output(phase1_assigner, capsys):
    """테스트 12: 배정된 학생 수 출력 확인"""
    phase1_assigner.together_groups = [
        {'학생A', '학생B'},
        {'학생C', '학생D'}
    ]

    phase1_assigner.phase1_apply_rules()

    captured = capsys.readouterr()
    assert "Phase 1 완료" in captured.out
    assert "4명 배정됨" in captured.out


def test_separation_to_smallest_available_class(phase1_assigner):
    """테스트 13: 분반 시 가능한 반 중 가장 학생 수 적은 반 선택"""
    # 학생A를 1반에 배정
    phase1_assigner.together_groups = [{'학생A'}]

    # A ↔ D 분반 규칙
    phase1_assigner.separation_rules = defaultdict(set, {
        '학생A': {'학생D'},
        '학생D': {'학생A'}
    })

    # 다른 학생들을 미리 일부 반에 배정 (학생D가 아닌)
    # 학생B → 2반
    학생B = phase1_assigner._find_student_by_name('학생B')
    phase1_assigner.classes[2].append(학생B)
    학생B.assigned_class = 2

    # 학생C → 2반
    학생C = phase1_assigner._find_student_by_name('학생C')
    phase1_assigner.classes[2].append(학생C)
    학생C.assigned_class = 2

    # 학생E → 3반
    학생E = phase1_assigner._find_student_by_name('학생E')
    phase1_assigner.classes[3].append(학생E)
    학생E.assigned_class = 3

    phase1_assigner.phase1_apply_rules()

    학생A = phase1_assigner._find_student_by_name('학생A')
    학생D = phase1_assigner._find_student_by_name('학생D')

    # 학생A는 1반에 배정됨
    assert 학생A.assigned_class == 1

    # 학생D는 A와 다른 반 중 가장 학생 수가 적은 반에 배정
    # 가능한 반: 2(2명), 3(1명), 4(0명), 5(0명), 6(0명), 7(0명)
    # → 4, 5, 6, 7 중 하나 (모두 0명이므로 가장 작은 번호인 4반 또는 첫 번째)
    assert 학생D.assigned_class != 학생A.assigned_class
    assert 학생D.assigned_class in [4, 5, 6, 7]  # 빈 반 중 하나
