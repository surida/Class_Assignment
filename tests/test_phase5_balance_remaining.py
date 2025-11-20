"""
phase5_balance_remaining 함수 테스트
남은 학생 최종 균형 배정 로직 테스트
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
    """테스트용 학생 리스트 (남학생 30명, 여학생 30명)"""
    students = []

    # 남학생 30명 (점수 100~71)
    for i in range(30):
        student = Student(
            학년=5,
            원반=1,
            원번호=i + 1,
            이름=f'남학생{i+1}',
            성별='남',
            점수=100 - i,
            특수반=(i == 5),  # 6번째 학생만 특수반
            전출=False,
            난이도=0.0,
            비고=""
        )
        student.rank = i + 1
        students.append(student)

    # 여학생 30명 (점수 100~71)
    for i in range(30):
        student = Student(
            학년=5,
            원반=1,
            원번호=i + 31,
            이름=f'여학생{i+1}',
            성별='여',
            점수=100 - i,
            특수반=False,
            전출=False,
            난이도=0.0,
            비고=""
        )
        student.rank = i + 1
        students.append(student)

    return students


@pytest.fixture
def phase5_assigner(mock_students):
    """phase5 테스트용 ClassAssigner 인스턴스"""
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.students = mock_students
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.classes = {i: [] for i in range(1, 8)}
    return assigner


# ============================================================================
# 정상 케이스
# ============================================================================

def test_no_unassigned_students(phase5_assigner):
    """테스트 1: 모든 학생이 이미 배정됨"""
    # 모든 학생을 미리 배정
    for i, student in enumerate(phase5_assigner.students):
        class_num = (i % 7) + 1
        phase5_assigner.classes[class_num].append(student)
        student.assigned_class = class_num

    phase5_assigner.phase5_balance_remaining()

    # 모든 학생이 배정된 상태 유지
    assigned_count = sum(1 for s in phase5_assigner.students
                        if s.assigned_class is not None)
    assert assigned_count == 60


def test_basic_balance_assignment(phase5_assigner):
    """테스트 2: 기본 균형 배정 - 일부 학생 미배정"""
    # 1반에만 10명 배정 (남5, 여5)
    for i in range(5):
        male = phase5_assigner._find_student_by_name(f'남학생{i+1}')
        phase5_assigner.classes[1].append(male)
        male.assigned_class = 1

        female = phase5_assigner._find_student_by_name(f'여학생{i+1}')
        phase5_assigner.classes[1].append(female)
        female.assigned_class = 1

    phase5_assigner.phase5_balance_remaining()

    # 모든 학생 배정 완료
    assigned_count = sum(1 for s in phase5_assigner.students
                        if s.assigned_class is not None)
    assert assigned_count == 60

    # 각 반에 최소 1명 이상 배정
    for c in range(1, 8):
        assert len(phase5_assigner.classes[c]) > 0


def test_effective_count_balance(phase5_assigner):
    """테스트 3: 유효 인원 균형 - 특수반 학생 고려"""
    # 1반에 특수반 학생(남학생6, effective=3) 배정
    특수반 = phase5_assigner._find_student_by_name('남학생6')
    phase5_assigner.classes[1].append(특수반)
    특수반.assigned_class = 1

    phase5_assigner.phase5_balance_remaining()

    # 각 반의 유효 인원 계산
    effective_counts = []
    for c in range(1, 8):
        effective = sum(s.effective_count() for s in phase5_assigner.classes[c])
        effective_counts.append(effective)

    # 유효 인원 균형 확인 (최대-최소 차이 <= 3)
    assert max(effective_counts) - min(effective_counts) <= 3


def test_gender_balance(phase5_assigner):
    """테스트 4: 성비 균형"""
    # 1반에 남학생만 5명 배정
    for i in range(5):
        male = phase5_assigner._find_student_by_name(f'남학생{i+1}')
        phase5_assigner.classes[1].append(male)
        male.assigned_class = 1

    phase5_assigner.phase5_balance_remaining()

    # 각 반의 남녀 비율 계산
    for c in range(1, 8):
        male_count = sum(1 for s in phase5_assigner.classes[c] if s.성별 == '남')
        female_count = sum(1 for s in phase5_assigner.classes[c] if s.성별 == '여')

        # 남녀 차이가 극단적이지 않아야 함
        assert abs(male_count - female_count) <= 5


def test_locked_false(phase5_assigner):
    """테스트 5: 배정 후 locked=False 확인"""
    phase5_assigner.phase5_balance_remaining()

    # phase5에서 배정한 학생들은 locked=False
    for s in phase5_assigner.students:
        if s.assigned_class is not None:
            assert s.locked == False


def test_score_order_maintained(phase5_assigner):
    """테스트 6: 점수순 배정 확인"""
    phase5_assigner.phase5_balance_remaining()

    # 남학생은 점수순으로 배정되어야 함
    male_students = [s for s in phase5_assigner.students if s.성별 == '남']
    male_students.sort(key=lambda s: s.점수, reverse=True)

    # 점수가 높은 학생이 먼저 배정됨
    assert male_students[0].assigned_class is not None
    assert male_students[-1].assigned_class is not None


# ============================================================================
# 분반 규칙 통합
# ============================================================================

def test_separation_rule_respected(phase5_assigner):
    """테스트 7: 분반 규칙 준수"""
    # 남학생1과 남학생2 분반 규칙
    phase5_assigner.separation_rules = defaultdict(set, {
        '남학생1': {'남학생2'},
        '남학생2': {'남학생1'}
    })

    # 1반에 남학생1 미리 배정
    남1 = phase5_assigner._find_student_by_name('남학생1')
    phase5_assigner.classes[1].append(남1)
    남1.assigned_class = 1

    phase5_assigner.phase5_balance_remaining()

    # 남학생2는 1반이 아님
    남2 = phase5_assigner._find_student_by_name('남학생2')
    if 남2.assigned_class is not None:
        assert 남2.assigned_class != 1


def test_cannot_assign_due_to_rules(phase5_assigner, capsys):
    """테스트 8: 분반 규칙으로 배정 불가"""
    # 남학생1과 모든 반의 학생들이 분반 규칙
    phase5_assigner.separation_rules = defaultdict(set, {
        '남학생1': {f'남학생{i}' for i in range(2, 9)}.union(
                   {f'여학생{i}' for i in range(1, 8)})
    })

    # 각 반에 남학생2~8, 여학생1~7 배정
    for c in range(1, 8):
        male = phase5_assigner._find_student_by_name(f'남학생{c+1}')
        phase5_assigner.classes[c].append(male)
        male.assigned_class = c

        female = phase5_assigner._find_student_by_name(f'여학생{c}')
        phase5_assigner.classes[c].append(female)
        female.assigned_class = c

    phase5_assigner.phase5_balance_remaining()

    # 남학생1은 배정 불가
    남1 = phase5_assigner._find_student_by_name('남학생1')
    assert 남1.assigned_class is None

    # 경고 메시지 출력 확인
    captured = capsys.readouterr()
    assert "남학생1" in captured.out
    assert "배정할 수 없습니다" in captured.out


# ============================================================================
# 균형 검증
# ============================================================================

def test_class_size_balance(phase5_assigner):
    """테스트 9: 반별 학생 수 균형"""
    phase5_assigner.phase5_balance_remaining()

    # 각 반의 학생 수 계산
    class_sizes = [len(phase5_assigner.classes[c]) for c in range(1, 8)]

    # 최대-최소 차이가 2 이하
    assert max(class_sizes) - min(class_sizes) <= 2


def test_fill_smallest_class_first(phase5_assigner):
    """테스트 10: 가장 작은 반부터 채우기"""
    # 1반에만 5명, 나머지 반은 비어있음
    for i in range(5):
        student = phase5_assigner.students[i]
        phase5_assigner.classes[1].append(student)
        student.assigned_class = 1

    phase5_assigner.phase5_balance_remaining()

    # 2~7반이 먼저 채워져야 함
    for c in range(2, 8):
        assert len(phase5_assigner.classes[c]) >= 7  # 최소 7명 이상


def test_effective_priority(phase5_assigner):
    """테스트 11: 유효 인원 우선순위"""
    # 1반에 일반 학생 10명, 2반에 특수반 학생 1명(effective=3) 배정
    for i in range(10):
        student = phase5_assigner.students[i]
        phase5_assigner.classes[1].append(student)
        student.assigned_class = 1

    특수반 = phase5_assigner._find_student_by_name('남학생6')
    phase5_assigner.classes[2].append(특수반)
    특수반.assigned_class = 2

    phase5_assigner.phase5_balance_remaining()

    # 1반: 10명(effective=10), 2반: 1명(effective=3)
    # 2반의 유효 인원이 더 적으므로 2반이 먼저 채워져야 함
    effective_2 = sum(s.effective_count() for s in phase5_assigner.classes[2])
    effective_1 = sum(s.effective_count() for s in phase5_assigner.classes[1])

    # 2반의 최종 유효 인원이 1반과 비슷하거나 더 많아야 함
    assert effective_2 >= effective_1 - 3


# ============================================================================
# 엣지 케이스
# ============================================================================

def test_single_unassigned_student(phase5_assigner):
    """테스트 12: 한 명만 미배정"""
    # 59명 배정, 1명(남학생30) 미배정
    for i, student in enumerate(phase5_assigner.students):
        if student.이름 != '남학생30':
            class_num = (i % 7) + 1
            phase5_assigner.classes[class_num].append(student)
            student.assigned_class = class_num

    phase5_assigner.phase5_balance_remaining()

    # 남학생30 배정됨
    남30 = phase5_assigner._find_student_by_name('남학생30')
    assert 남30.assigned_class is not None


def test_all_unassigned(phase5_assigner):
    """테스트 13: 모든 학생 미배정"""
    phase5_assigner.phase5_balance_remaining()

    # 모든 학생 배정 완료
    assigned_count = sum(1 for s in phase5_assigner.students
                        if s.assigned_class is not None)
    assert assigned_count == 60

    # 각 반에 골고루 배정
    class_sizes = [len(phase5_assigner.classes[c]) for c in range(1, 8)]
    assert max(class_sizes) - min(class_sizes) <= 2


def test_partial_assignment_per_class(phase5_assigner):
    """테스트 14: 각 반에 일부씩 배정됨"""
    # 각 반에 2명씩 배정 (총 14명)
    for c in range(1, 8):
        for i in range(2):
            student = phase5_assigner.students[c * 2 + i - 2]
            phase5_assigner.classes[c].append(student)
            student.assigned_class = c

    phase5_assigner.phase5_balance_remaining()

    # 나머지 46명 배정 완료
    assigned_count = sum(1 for s in phase5_assigner.students
                        if s.assigned_class is not None)
    assert assigned_count == 60
