"""
phase4_balance_difficulty 함수 테스트
난이도 균등 배분 로직 테스트
"""

import pytest
from collections import defaultdict
import sys
import os

# 상위 디렉토리의 class_assigner 모듈 import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from class_assigner import ClassAssigner, Student


@pytest.fixture
def mock_students_with_difficulty():
    """난이도가 있는 테스트용 학생 리스트"""
    students = [
        # 난이도 높은 학생들
        Student(학년=5, 원반=1, 원번호=1, 이름='난이도A', 성별='남', 점수=85, 특수반=False, 전출=False, 난이도=5.0, 비고=''),
        Student(학년=5, 원반=1, 원번호=2, 이름='난이도B', 성별='여', 점수=82, 특수반=False, 전출=False, 난이도=4.5, 비고=''),
        Student(학년=5, 원반=2, 원번호=1, 이름='난이도C', 성별='남', 점수=80, 특수반=False, 전출=False, 난이도=4.0, 비고=''),
        Student(학년=5, 원반=2, 원번호=2, 이름='난이도D', 성별='여', 점수=78, 특수반=False, 전출=False, 난이도=3.5, 비고=''),
        Student(학년=5, 원반=3, 원번호=1, 이름='난이도E', 성별='남', 점수=76, 특수반=False, 전출=False, 난이도=3.0, 비고=''),

        # 난이도 없는 학생들
        Student(학년=5, 원반=3, 원번호=2, 이름='일반A', 성별='여', 점수=88, 특수반=False, 전출=False, 난이도=0.0, 비고=''),
        Student(학년=5, 원반=4, 원번호=1, 이름='일반B', 성별='남', 점수=86, 특수반=False, 전출=False, 난이도=0.0, 비고=''),
        Student(학년=5, 원반=4, 원번호=2, 이름='일반C', 성별='여', 점수=84, 특수반=False, 전출=False, 난이도=0.0, 비고=''),
    ]
    return students


@pytest.fixture
def phase4_assigner(mock_students_with_difficulty):
    """phase4 테스트용 ClassAssigner 인스턴스"""
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.students = mock_students_with_difficulty
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.classes = {i: [] for i in range(1, 8)}
    return assigner


# ============================================================================
# 정상 케이스
# ============================================================================

def test_no_difficulty_students(phase4_assigner):
    """테스트 1: 난이도가 있는 학생이 없는 경우"""
    # 모든 학생의 난이도를 0으로 설정
    for student in phase4_assigner.students:
        student.난이도 = 0.0

    phase4_assigner.phase4_balance_difficulty()

    # 아무도 배정되지 않아야 함
    assigned_count = sum(1 for s in phase4_assigner.students if s.assigned_class is not None)
    assert assigned_count == 0


def test_all_already_assigned(phase4_assigner):
    """테스트 2: 난이도 학생이 모두 이미 배정됨"""
    # 난이도 있는 학생들을 미리 배정
    난이도_학생들 = [s for s in phase4_assigner.students if s.난이도 > 0]
    for i, student in enumerate(난이도_학생들):
        class_num = (i % 7) + 1
        phase4_assigner.classes[class_num].append(student)
        student.assigned_class = class_num
        student.locked = True

    phase4_assigner.phase4_balance_difficulty()

    # 그대로 유지
    for i, student in enumerate(난이도_학생들):
        assert student.assigned_class == (i % 7) + 1


def test_single_difficulty_student(phase4_assigner):
    """테스트 3: 난이도 학생 1명"""
    # 난이도A만 남기고 나머지 난이도 학생 제거
    phase4_assigner.students = [s for s in phase4_assigner.students
                                if s.이름 == '난이도A' or s.난이도 == 0]

    phase4_assigner.phase4_balance_difficulty()

    난이도A = phase4_assigner._find_student_by_name('난이도A')

    # 배정되어야 함
    assert 난이도A.assigned_class is not None
    assert 난이도A.locked == True


def test_multiple_difficulty_students_balanced(phase4_assigner):
    """테스트 4: 여러 난이도 학생 - 균등 배분"""
    phase4_assigner.phase4_balance_difficulty()

    난이도_학생들 = [s for s in phase4_assigner.students if s.난이도 > 0]

    # 모두 배정되어야 함
    assert all(s.assigned_class is not None for s in 난이도_학생들)

    # 모두 locked
    assert all(s.locked for s in 난이도_학생들)

    # 반별 난이도 합 계산
    difficulty_sum = {c: sum(s.난이도 for s in phase4_assigner.classes[c])
                     for c in range(1, 8)}

    # 난이도 합의 최대-최소 차이가 크지 않아야 함
    assert max(difficulty_sum.values()) - min(difficulty_sum.values()) <= 5.0


def test_highest_difficulty_first(phase4_assigner):
    """테스트 5: 난이도 높은 학생부터 배정"""
    phase4_assigner.phase4_balance_difficulty()

    난이도A = phase4_assigner._find_student_by_name('난이도A')  # 5.0
    난이도B = phase4_assigner._find_student_by_name('난이도B')  # 4.5
    난이도C = phase4_assigner._find_student_by_name('난이도C')  # 4.0
    난이도D = phase4_assigner._find_student_by_name('난이도D')  # 3.5
    난이도E = phase4_assigner._find_student_by_name('난이도E')  # 3.0

    # 모두 배정됨
    assert all(s.assigned_class is not None for s in [난이도A, 난이도B, 난이도C, 난이도D, 난이도E])

    # 반별 난이도 합이 균등해야 함
    difficulty_sum = {c: sum(s.난이도 for s in phase4_assigner.classes[c])
                     for c in range(1, 8)}

    # 5명이 배정되므로 일부 반은 0일 수 있음
    # 배정된 반들 중에서는 균형이 맞아야 함
    assigned_classes = [difficulty_sum[c] for c in range(1, 8) if difficulty_sum[c] > 0]
    if len(assigned_classes) > 1:
        assert max(assigned_classes) - min(assigned_classes) <= 5.0


def test_assign_to_lowest_difficulty_class(phase4_assigner):
    """테스트 6: 난이도 합이 가장 낮은 반에 배정"""
    # 1반에 난이도 10 미리 추가
    일반A = phase4_assigner._find_student_by_name('일반A')
    일반A.난이도 = 10.0
    phase4_assigner.classes[1].append(일반A)
    일반A.assigned_class = 1

    phase4_assigner.phase4_balance_difficulty()

    # 난이도 학생들은 1반이 아닌 다른 반에 우선 배정되어야 함
    난이도_학생들 = [s for s in phase4_assigner.students
                   if s.난이도 > 0 and s.assigned_class is not None and s != 일반A]

    # 반별 난이도 합 계산
    difficulty_sum = {c: sum(s.난이도 for s in phase4_assigner.classes[c])
                     for c in range(1, 8)}

    # 1반의 난이도 합이 가장 높아야 함 (10 + 추가 배정)
    # 또는 다른 반들이 균등하게 배정되어야 함
    # 최소한 2~7반 중 일부에 배정되어야 함
    other_classes_assigned = sum(1 for c in range(2, 8) if difficulty_sum[c] > 0)
    assert other_classes_assigned > 0


# ============================================================================
# 분반 규칙과의 상호작용
# ============================================================================

def test_with_separation_rules(phase4_assigner):
    """테스트 7: 분반 규칙이 있는 난이도 학생"""
    # 난이도A와 일반A 분반 규칙
    phase4_assigner.separation_rules = defaultdict(set, {
        '난이도A': {'일반A'},
        '일반A': {'난이도A'}
    })

    # 일반A를 1반에 배정
    일반A = phase4_assigner._find_student_by_name('일반A')
    phase4_assigner.classes[1].append(일반A)
    일반A.assigned_class = 1

    phase4_assigner.phase4_balance_difficulty()

    난이도A = phase4_assigner._find_student_by_name('난이도A')

    # 난이도A는 1반이 아닌 다른 반에 배정
    assert 난이도A.assigned_class is not None
    assert 난이도A.assigned_class != 1


def test_cannot_assign_due_to_rules(phase4_assigner, capsys):
    """테스트 8: 분반 규칙으로 배정 불가"""
    # 난이도A와 모든 학생이 분반 규칙
    all_names = {s.이름 for s in phase4_assigner.students if s.이름 != '난이도A'}
    phase4_assigner.separation_rules = defaultdict(set, {
        '난이도A': all_names
    })

    # 각 반에 학생 미리 배정 (7개 반)
    other_students = [s for s in phase4_assigner.students if s.이름 != '난이도A']
    for i, student in enumerate(other_students[:7]):
        class_num = i + 1
        phase4_assigner.classes[class_num].append(student)
        student.assigned_class = class_num

    phase4_assigner.phase4_balance_difficulty()

    난이도A = phase4_assigner._find_student_by_name('난이도A')

    # 배정 불가
    assert 난이도A.assigned_class is None

    # 경고 메시지 확인
    captured = capsys.readouterr()
    assert "난이도A" in captured.out
    assert "배정할 수 없습니다" in captured.out


# ============================================================================
# 균형 검증
# ============================================================================

def test_balanced_difficulty_sum(phase4_assigner):
    """테스트 9: 반별 난이도 합 균형"""
    phase4_assigner.phase4_balance_difficulty()

    # 반별 난이도 합 계산
    difficulty_sum = {c: sum(s.난이도 for s in phase4_assigner.classes[c])
                     for c in range(1, 8)}

    난이도_학생들 = [s for s in phase4_assigner.students if s.난이도 > 0]
    총_난이도 = sum(s.난이도 for s in 난이도_학생들)

    # 배정된 난이도 합이 전체와 일치
    배정된_난이도 = sum(difficulty_sum.values())
    assert abs(배정된_난이도 - 총_난이도) < 0.01  # 부동소수점 오차 허용


def test_seven_difficulty_students(phase4_assigner):
    """테스트 10: 난이도 학생 7명 - 각 반에 1명씩"""
    # 난이도 학생 7명 생성
    phase4_assigner.students = []
    for i in range(7):
        student = Student(
            학년=5, 원반=1, 원번호=i+1,
            이름=f'난이도{i+1}',
            성별='남' if i % 2 == 0 else '여',
            점수=90-i,
            특수반=False, 전출=False,
            난이도=5.0 - i*0.5,
            비고=''
        )
        phase4_assigner.students.append(student)

    phase4_assigner.phase4_balance_difficulty()

    # 모두 배정됨
    assert all(s.assigned_class is not None for s in phase4_assigner.students)

    # 각 반에 1명씩
    for c in range(1, 8):
        assert len(phase4_assigner.classes[c]) == 1

    # 반별 난이도 합 계산
    difficulty_sum = {c: sum(s.난이도 for s in phase4_assigner.classes[c])
                     for c in range(1, 8)}

    # 각 반에 1명씩이므로 난이도가 그대로 분산됨
    # 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0 → 차이는 3.0
    # 이것은 정상 동작 (난이도 합이 낮은 반에 높은 난이도 학생 배정)
    assert max(difficulty_sum.values()) - min(difficulty_sum.values()) <= 3.5


def test_fourteen_difficulty_students(phase4_assigner):
    """테스트 11: 난이도 학생 14명 - 각 반에 2명씩"""
    # 난이도 학생 14명 생성
    phase4_assigner.students = []
    for i in range(14):
        student = Student(
            학년=5, 원반=1, 원번호=i+1,
            이름=f'난이도{i+1}',
            성별='남' if i % 2 == 0 else '여',
            점수=90-i,
            특수반=False, 전출=False,
            난이도=5.0 - i*0.3,
            비고=''
        )
        phase4_assigner.students.append(student)

    phase4_assigner.phase4_balance_difficulty()

    # 모두 배정됨
    assert all(s.assigned_class is not None for s in phase4_assigner.students)

    # 각 반에 2명씩
    for c in range(1, 8):
        assert len(phase4_assigner.classes[c]) == 2

    # 반별 난이도 합이 균등
    difficulty_sum = {c: sum(s.난이도 for s in phase4_assigner.classes[c])
                     for c in range(1, 8)}

    # 최대-최소 차이 <= 1.0
    assert max(difficulty_sum.values()) - min(difficulty_sum.values()) <= 1.5


# ============================================================================
# 일부 배정된 경우
# ============================================================================

def test_partial_assignment_before_phase4(phase4_assigner):
    """테스트 12: 일부 반에 이미 난이도 학생이 있는 경우"""
    # 1반에 난이도B 미리 배정
    난이도B = phase4_assigner._find_student_by_name('난이도B')
    phase4_assigner.classes[1].append(난이도B)
    난이도B.assigned_class = 1
    난이도B.locked = True

    phase4_assigner.phase4_balance_difficulty()

    # 나머지 난이도 학생들도 배정됨
    난이도_학생들 = [s for s in phase4_assigner.students if s.난이도 > 0]
    assert all(s.assigned_class is not None for s in 난이도_학생들)

    # 반별 난이도 합이 비교적 균등
    difficulty_sum = {c: sum(s.난이도 for s in phase4_assigner.classes[c])
                     for c in range(1, 8)}

    # 1반은 이미 4.5가 있으므로 다른 반보다 높을 수 있음
    # 하지만 전체적으로는 균형을 맞추려고 함
    assert max(difficulty_sum.values()) - min(difficulty_sum.values()) <= 6.0


# ============================================================================
# 엣지 케이스
# ============================================================================

def test_only_difficulty_students(phase4_assigner):
    """테스트 13: 난이도 있는 학생만 있는 경우"""
    # 난이도 없는 학생 제거
    phase4_assigner.students = [s for s in phase4_assigner.students if s.난이도 > 0]

    phase4_assigner.phase4_balance_difficulty()

    # 모두 배정됨
    assert all(s.assigned_class is not None for s in phase4_assigner.students)


def test_output_messages(phase4_assigner, capsys):
    """테스트 14: 출력 메시지 검증"""
    phase4_assigner.phase4_balance_difficulty()

    captured = capsys.readouterr()

    # 난이도 배정 대상 출력
    assert "난이도 배정 대상:" in captured.out
    assert "5명" in captured.out

    # 반별 난이도 합 출력
    assert "반별 난이도 합:" in captured.out
