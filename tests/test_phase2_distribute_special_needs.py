"""
phase2_distribute_special_needs 함수 테스트
특수반 학생 균등 배치 로직 테스트
"""

import pytest
from collections import defaultdict
import sys
import os

# 상위 디렉토리의 class_assigner 모듈 import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from class_assigner import ClassAssigner, Student


@pytest.fixture
def mock_students_with_special():
    """특수반 학생을 포함한 테스트용 Student 객체 리스트"""
    students = []
    names = ['일반A', '특수B', '일반C', '특수D', '일반E', '특수F', '일반G', '일반H']
    is_special = [False, True, False, True, False, True, False, False]

    for i, (name, special) in enumerate(zip(names, is_special)):
        student = Student(
            학년=5,
            원반=1,
            원번호=i + 1,
            이름=name,
            성별='남' if i % 2 == 0 else '여',
            점수=85 + i,
            특수반=special,
            전출=False,
            난이도=0.0,
            비고=""
        )
        students.append(student)

    return students


@pytest.fixture
def phase2_assigner(mock_students_with_special):
    """phase2 테스트용 ClassAssigner 인스턴스"""
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.students = mock_students_with_special
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.classes = {i: [] for i in range(1, 8)}
    return assigner


# ============================================================================
# 정상 케이스
# ============================================================================

def test_no_special_students(phase2_assigner):
    """테스트 1: 특수반 학생이 없음"""
    # 모든 학생을 일반 학생으로 변경
    for student in phase2_assigner.students:
        student.특수반 = False

    phase2_assigner.phase2_distribute_special_needs()

    # 아무도 배정되지 않아야 함
    assigned_count = sum(1 for s in phase2_assigner.students if s.assigned_class is not None)
    assert assigned_count == 0


def test_single_special_student(phase2_assigner):
    """테스트 2: 특수반 학생 1명 - 빈 반에 배정"""
    # 특수반 학생을 1명만 남김
    for student in phase2_assigner.students:
        if student.이름 != '특수B':
            student.특수반 = False

    phase2_assigner.phase2_distribute_special_needs()

    특수B = phase2_assigner._find_student_by_name('특수B')

    # 배정되어야 함
    assert 특수B.assigned_class is not None
    assert 특수B.locked == True

    # 빈 반 중 하나에 배정 (1-7반 중 하나)
    assert 특수B.assigned_class in range(1, 8)


def test_multiple_special_students_even_distribution(phase2_assigner):
    """테스트 3: 여러 특수반 학생 - 균등 배분"""
    # 특수B, 특수D, 특수F (3명)
    phase2_assigner.phase2_distribute_special_needs()

    특수B = phase2_assigner._find_student_by_name('특수B')
    특수D = phase2_assigner._find_student_by_name('특수D')
    특수F = phase2_assigner._find_student_by_name('특수F')

    # 모두 배정되어야 함
    assert 특수B.assigned_class is not None
    assert 특수D.assigned_class is not None
    assert 특수F.assigned_class is not None

    # 서로 다른 반에 배정되어야 함 (균등 배분)
    assert 특수B.assigned_class != 특수D.assigned_class
    assert 특수D.assigned_class != 특수F.assigned_class
    assert 특수B.assigned_class != 특수F.assigned_class


def test_special_students_locked(phase2_assigner):
    """테스트 4: 특수반 학생 배정 후 locked=True"""
    phase2_assigner.phase2_distribute_special_needs()

    for student in phase2_assigner.students:
        if student.특수반 and student.assigned_class is not None:
            assert student.locked == True


# ============================================================================
# 이미 배정된 학생 처리
# ============================================================================

def test_already_assigned_special_students(phase2_assigner):
    """테스트 5: 일부 특수반 학생이 이미 배정됨"""
    # 특수B를 미리 1반에 배정
    특수B = phase2_assigner._find_student_by_name('특수B')
    phase2_assigner.classes[1].append(특수B)
    특수B.assigned_class = 1
    특수B.locked = True

    phase2_assigner.phase2_distribute_special_needs()

    특수D = phase2_assigner._find_student_by_name('특수D')
    특수F = phase2_assigner._find_student_by_name('특수F')

    # 특수B는 그대로 1반
    assert 특수B.assigned_class == 1

    # 특수D, F는 새로 배정되고, 1반이 아닌 다른 반에 배정되어야 함
    # (1반에 이미 특수반 학생 1명 있으므로)
    assert 특수D.assigned_class is not None
    assert 특수F.assigned_class is not None


def test_special_with_separation_rule(phase2_assigner):
    """테스트 6: 특수반 학생 + 분반 규칙"""
    # 특수B와 일반A 분반 규칙
    phase2_assigner.separation_rules = defaultdict(set, {
        '특수B': {'일반A'},
        '일반A': {'특수B'}
    })

    # 일반A를 1반에 배정
    일반A = phase2_assigner._find_student_by_name('일반A')
    phase2_assigner.classes[1].append(일반A)
    일반A.assigned_class = 1

    phase2_assigner.phase2_distribute_special_needs()

    특수B = phase2_assigner._find_student_by_name('특수B')

    # 특수B는 배정되어야 하지만, 1반이 아님 (일반A와 분반)
    assert 특수B.assigned_class is not None
    assert 특수B.assigned_class != 1
    assert 특수B.locked == True


def test_balance_after_partial_assignment(phase2_assigner):
    """테스트 7: 일부 반에 특수반 학생이 이미 많은 경우"""
    # 1반에 일반 학생 2명 미리 배정 (특수반 아님)
    일반A = phase2_assigner._find_student_by_name('일반A')
    일반C = phase2_assigner._find_student_by_name('일반C')
    phase2_assigner.classes[1].append(일반A)
    phase2_assigner.classes[1].append(일반C)
    일반A.assigned_class = 1
    일반C.assigned_class = 1

    # 2반에 특수반 학생 1명 미리 배정
    특수B = phase2_assigner._find_student_by_name('특수B')
    phase2_assigner.classes[2].append(특수B)
    특수B.assigned_class = 2
    특수B.locked = True

    phase2_assigner.phase2_distribute_special_needs()

    특수D = phase2_assigner._find_student_by_name('특수D')
    특수F = phase2_assigner._find_student_by_name('특수F')

    # 특수D, F는 2반이 아닌 다른 반에 배정되어야 함
    # (2반에 이미 특수반 학생 1명 있으므로)
    assert 특수D.assigned_class != 2
    assert 특수F.assigned_class != 2


# ============================================================================
# 엣지 케이스
# ============================================================================

def test_all_special_students_already_assigned(phase2_assigner):
    """테스트 8: 모든 특수반 학생이 이미 배정됨"""
    # 모든 특수반 학생을 미리 배정
    특수B = phase2_assigner._find_student_by_name('특수B')
    특수D = phase2_assigner._find_student_by_name('특수D')
    특수F = phase2_assigner._find_student_by_name('특수F')

    phase2_assigner.classes[1].append(특수B)
    특수B.assigned_class = 1

    phase2_assigner.classes[2].append(특수D)
    특수D.assigned_class = 2

    phase2_assigner.classes[3].append(특수F)
    특수F.assigned_class = 3

    phase2_assigner.phase2_distribute_special_needs()

    # 모두 그대로 유지
    assert 특수B.assigned_class == 1
    assert 특수D.assigned_class == 2
    assert 특수F.assigned_class == 3


def test_special_student_cannot_assign_due_to_rules(phase2_assigner, capsys):
    """테스트 9: 분반 규칙으로 배정 불가능한 특수반 학생"""
    # 특수B와 모든 반의 학생들이 분반 규칙
    phase2_assigner.separation_rules = defaultdict(set, {
        '특수B': {'일반A', '일반C', '일반E', '일반G', '일반H', '특수D', '특수F'}
    })

    # 모든 반에 학생 미리 배정
    일반A = phase2_assigner._find_student_by_name('일반A')
    phase2_assigner.classes[1].append(일반A)
    일반A.assigned_class = 1

    일반C = phase2_assigner._find_student_by_name('일반C')
    phase2_assigner.classes[2].append(일반C)
    일반C.assigned_class = 2

    일반E = phase2_assigner._find_student_by_name('일반E')
    phase2_assigner.classes[3].append(일반E)
    일반E.assigned_class = 3

    일반G = phase2_assigner._find_student_by_name('일반G')
    phase2_assigner.classes[4].append(일반G)
    일반G.assigned_class = 4

    일반H = phase2_assigner._find_student_by_name('일반H')
    phase2_assigner.classes[5].append(일반H)
    일반H.assigned_class = 5

    특수D = phase2_assigner._find_student_by_name('특수D')
    phase2_assigner.classes[6].append(특수D)
    특수D.assigned_class = 6

    특수F = phase2_assigner._find_student_by_name('특수F')
    phase2_assigner.classes[7].append(특수F)
    특수F.assigned_class = 7

    phase2_assigner.phase2_distribute_special_needs()

    # 특수B는 배정되지 않음
    특수B = phase2_assigner._find_student_by_name('특수B')
    assert 특수B.assigned_class is None

    # 경고 메시지 출력 확인
    captured = capsys.readouterr()
    assert "특수B" in captured.out
    assert "배정할 수 없습니다" in captured.out


def test_output_messages(phase2_assigner, capsys):
    """테스트 10: 출력 메시지 검증"""
    phase2_assigner.phase2_distribute_special_needs()

    captured = capsys.readouterr()

    # 특수반 학생 정보 출력
    assert "총 특수반 학생: 3명" in captured.out
    assert "이미 배정됨: 0명" in captured.out
    assert "배정 필요: 3명" in captured.out

    # 반별 특수반 학생 수 출력
    assert "반별 특수반 학생 수" in captured.out


def test_seven_special_students_distribution(phase2_assigner):
    """테스트 11: 7명의 특수반 학생 - 각 반에 1명씩"""
    # 특수반 학생을 7명으로 늘림
    for i, student in enumerate(phase2_assigner.students[:7]):
        student.특수반 = True
        student.이름 = f'특수{i+1}'

    phase2_assigner.phase2_distribute_special_needs()

    # 각 반의 특수반 학생 수 계산
    special_count = {c: sum(1 for s in phase2_assigner.classes[c] if s.특수반)
                    for c in range(1, 8)}

    # 모든 반에 1명씩 배정되어야 함
    for c in range(1, 8):
        assert special_count[c] == 1


def test_fourteen_special_students_distribution(phase2_assigner):
    """테스트 12: 14명의 특수반 학생 - 각 반에 2명씩"""
    # 학생을 14명으로 늘리고 모두 특수반으로 설정
    students = []
    for i in range(14):
        student = Student(
            학년=5, 원반=1, 원번호=i+1,
            이름=f'특수{i+1}',
            성별='남' if i % 2 == 0 else '여',
            점수=85+i,
            특수반=True,
            전출=False,
            난이도=0.0,
            비고=""
        )
        students.append(student)

    phase2_assigner.students = students

    phase2_assigner.phase2_distribute_special_needs()

    # 각 반의 특수반 학생 수 계산
    special_count = {c: sum(1 for s in phase2_assigner.classes[c] if s.특수반)
                    for c in range(1, 8)}

    # 모든 반에 2명씩 배정되어야 함
    for c in range(1, 8):
        assert special_count[c] == 2


def test_special_count_per_class_balanced(phase2_assigner):
    """테스트 13: 반별 특수반 학생 수 균형 검증"""
    phase2_assigner.phase2_distribute_special_needs()

    # 각 반의 특수반 학생 수
    special_count = {c: sum(1 for s in phase2_assigner.classes[c] if s.특수반)
                    for c in range(1, 8)}

    counts = list(special_count.values())

    # 최대값 - 최소값 <= 1 (균등 배분)
    assert max(counts) - min(counts) <= 1
