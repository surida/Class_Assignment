"""
phase3_separate_same_names 함수 테스트
동명이인 분리 로직 테스트
"""

import pytest
from collections import defaultdict, Counter
import sys
import os

# 상위 디렉토리의 class_assigner 모듈 import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from class_assigner import ClassAssigner, Student


@pytest.fixture
def mock_students_with_duplicates():
    """동명이인이 있는 테스트용 학생 리스트"""
    students = [
        # 김철수 3명 (동명이인)
        Student(학년=5, 원반=1, 원번호=1, 이름='김철수', 성별='남', 점수=95, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=2, 원번호=1, 이름='김철수', 성별='남', 점수=90, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=3, 원번호=1, 이름='김철수', 성별='남', 점수=85, 특수반=False, 전출=False, 난이도=0, 비고=''),

        # 이영희 2명 (동명이인)
        Student(학년=5, 원반=1, 원번호=2, 이름='이영희', 성별='여', 점수=92, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=2, 원번호=2, 이름='이영희', 성별='여', 점수=88, 특수반=False, 전출=False, 난이도=0, 비고=''),

        # 유일한 이름들
        Student(학년=5, 원반=1, 원번호=3, 이름='박민수', 성별='남', 점수=87, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=2, 원번호=3, 이름='최지훈', 성별='남', 점수=83, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=3, 원번호=2, 이름='정수진', 성별='여', 점수=80, 특수반=False, 전출=False, 난이도=0, 비고=''),
    ]
    return students


@pytest.fixture
def phase3_assigner(mock_students_with_duplicates):
    """phase3 테스트용 ClassAssigner 인스턴스"""
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.students = mock_students_with_duplicates
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.classes = {i: [] for i in range(1, 8)}
    return assigner


# ============================================================================
# 정상 케이스
# ============================================================================

def test_no_duplicate_names(phase3_assigner):
    """테스트 1: 동명이인이 없는 경우"""
    # 모든 학생 이름을 유일하게 변경
    for i, student in enumerate(phase3_assigner.students):
        student.이름 = f'학생{i+1}'

    phase3_assigner.phase3_separate_same_names()

    # 아무도 배정되지 않아야 함 (동명이인이 없으므로)
    assigned_count = sum(1 for s in phase3_assigner.students if s.assigned_class is not None)
    assert assigned_count == 0


def test_two_students_same_name(phase3_assigner):
    """테스트 2: 2명의 동명이인 - 다른 반 배정"""
    # 이영희 2명만 남기고 나머지 제거
    phase3_assigner.students = [s for s in phase3_assigner.students if s.이름 == '이영희']

    phase3_assigner.phase3_separate_same_names()

    이영희들 = [s for s in phase3_assigner.students if s.이름 == '이영희']

    # 둘 다 배정되어야 함
    assert all(s.assigned_class is not None for s in 이영희들)

    # 서로 다른 반에 배정
    assert 이영희들[0].assigned_class != 이영희들[1].assigned_class

    # 둘 다 locked
    assert all(s.locked for s in 이영희들)


def test_three_students_same_name(phase3_assigner):
    """테스트 3: 3명의 동명이인 - 모두 다른 반 배정"""
    # 김철수 3명만 남기고 나머지 제거
    phase3_assigner.students = [s for s in phase3_assigner.students if s.이름 == '김철수']

    phase3_assigner.phase3_separate_same_names()

    김철수들 = [s for s in phase3_assigner.students if s.이름 == '김철수']

    # 셋 다 배정되어야 함
    assert all(s.assigned_class is not None for s in 김철수들)

    # 모두 다른 반에 배정
    assigned_classes = [s.assigned_class for s in 김철수들]
    assert len(assigned_classes) == len(set(assigned_classes))  # 중복 없음

    # 셋 다 locked
    assert all(s.locked for s in 김철수들)


def test_multiple_duplicate_groups(phase3_assigner):
    """테스트 4: 여러 동명이인 그룹"""
    phase3_assigner.phase3_separate_same_names()

    # 김철수 3명
    김철수들 = [s for s in phase3_assigner.students if s.이름 == '김철수']
    김철수_classes = [s.assigned_class for s in 김철수들]
    assert len(김철수_classes) == len(set(김철수_classes))  # 모두 다른 반

    # 이영희 2명
    이영희들 = [s for s in phase3_assigner.students if s.이름 == '이영희']
    이영희_classes = [s.assigned_class for s in 이영희들]
    assert len(이영희_classes) == len(set(이영희_classes))  # 모두 다른 반

    # 유일한 이름들은 배정 안 됨
    박민수 = phase3_assigner._find_student_by_name('박민수')
    assert 박민수.assigned_class is None


def test_assign_to_smallest_class(phase3_assigner):
    """테스트 5: 가장 학생 수가 적은 반에 배정"""
    # 1반에 학생 5명 미리 배정
    for i in range(5):
        student = phase3_assigner.students[i]
        student.이름 = f'일반{i+1}'  # 동명이인 아님
        phase3_assigner.classes[1].append(student)
        student.assigned_class = 1

    # 김철수 2명만 남기기
    phase3_assigner.students = [s for s in phase3_assigner.students if s.이름 == '김철수'][:2]

    phase3_assigner.phase3_separate_same_names()

    김철수들 = [s for s in phase3_assigner.students if s.이름 == '김철수']

    # 1반은 이미 5명이므로 2~7반 중에서 배정되어야 함
    for student in 김철수들:
        assert student.assigned_class != 1
        assert student.assigned_class in range(2, 8)


# ============================================================================
# 일부 배정된 경우
# ============================================================================

def test_one_already_assigned(phase3_assigner):
    """테스트 6: 동명이인 중 1명이 이미 배정됨"""
    # 김철수 3명 중 1명을 1반에 미리 배정
    김철수들 = [s for s in phase3_assigner.students if s.이름 == '김철수']
    phase3_assigner.classes[1].append(김철수들[0])
    김철수들[0].assigned_class = 1
    김철수들[0].locked = True

    phase3_assigner.phase3_separate_same_names()

    # 나머지 2명도 배정되어야 함
    assert all(s.assigned_class is not None for s in 김철수들)

    # 모두 다른 반
    assigned_classes = [s.assigned_class for s in 김철수들]
    assert len(assigned_classes) == len(set(assigned_classes))

    # 나머지 2명은 1반이 아님
    assert 김철수들[1].assigned_class != 1
    assert 김철수들[2].assigned_class != 1


def test_all_already_assigned(phase3_assigner):
    """테스트 7: 모든 동명이인이 이미 배정됨"""
    # 이영희 2명을 다른 반에 미리 배정
    이영희들 = [s for s in phase3_assigner.students if s.이름 == '이영희']
    phase3_assigner.classes[1].append(이영희들[0])
    이영희들[0].assigned_class = 1
    이영희들[0].locked = True

    phase3_assigner.classes[2].append(이영희들[1])
    이영희들[1].assigned_class = 2
    이영희들[1].locked = True

    phase3_assigner.phase3_separate_same_names()

    # 그대로 유지
    assert 이영희들[0].assigned_class == 1
    assert 이영희들[1].assigned_class == 2


# ============================================================================
# 분반 규칙과의 상호작용
# ============================================================================

def test_with_separation_rules(phase3_assigner):
    """테스트 8: 분반 규칙이 있는 동명이인"""
    # 김철수와 박민수는 분반 규칙
    phase3_assigner.separation_rules = defaultdict(set, {
        '김철수': {'박민수'},
        '박민수': {'김철수'}
    })

    # 박민수를 1반에 미리 배정
    박민수 = phase3_assigner._find_student_by_name('박민수')
    phase3_assigner.classes[1].append(박민수)
    박민수.assigned_class = 1

    phase3_assigner.phase3_separate_same_names()

    # 김철수 3명 모두 1반이 아니어야 함 (박민수와 분반)
    김철수들 = [s for s in phase3_assigner.students if s.이름 == '김철수']
    for student in 김철수들:
        assert student.assigned_class != 1


def test_cannot_assign_due_to_rules(phase3_assigner, capsys):
    """테스트 9: 분반 규칙으로 배정 불가"""
    # 김철수와 모든 이미 배정된 학생들이 분반 규칙
    phase3_assigner.separation_rules = defaultdict(set, {
        '김철수': {'박민수', '최지훈', '정수진', '이영희'}
    })

    # 각 반에 학생 미리 배정 (1~7반)
    박민수 = phase3_assigner._find_student_by_name('박민수')
    phase3_assigner.classes[1].append(박민수)
    박민수.assigned_class = 1

    최지훈 = phase3_assigner._find_student_by_name('최지훈')
    phase3_assigner.classes[2].append(최지훈)
    최지훈.assigned_class = 2

    정수진 = phase3_assigner._find_student_by_name('정수진')
    phase3_assigner.classes[3].append(정수진)
    정수진.assigned_class = 3

    이영희들 = [s for s in phase3_assigner.students if s.이름 == '이영희']
    phase3_assigner.classes[4].append(이영희들[0])
    이영희들[0].assigned_class = 4

    phase3_assigner.classes[5].append(이영희들[1])
    이영희들[1].assigned_class = 5

    # 김철수 중 한 명을 6반에 배정 (분반 규칙 위반하지 않음)
    김철수들 = [s for s in phase3_assigner.students if s.이름 == '김철수']
    phase3_assigner.classes[6].append(김철수들[0])
    김철수들[0].assigned_class = 6
    김철수들[0].locked = True

    phase3_assigner.phase3_separate_same_names()

    # 나머지 김철수 2명 중 1명은 7반에 배정 가능
    # 하지만 마지막 1명은 배정 불가 (모든 반에 분반 규칙 학생 있음)
    unassigned = [s for s in 김철수들 if s.assigned_class is None]

    # 최소 1명은 배정 불가
    assert len(unassigned) >= 1

    # 경고 메시지 확인
    captured = capsys.readouterr()
    assert "김철수" in captured.out
    assert "배정할 수 없습니다" in captured.out


# ============================================================================
# 균형 검증
# ============================================================================

def test_balanced_distribution(phase3_assigner):
    """테스트 10: 동명이인이 균등하게 분산됨"""
    phase3_assigner.phase3_separate_same_names()

    # 반별 학생 수 차이가 크지 않아야 함
    class_sizes = [len(phase3_assigner.classes[c]) for c in range(1, 8)]

    # 김철수 3명 + 이영희 2명 = 5명 배정
    assert sum(class_sizes) == 5

    # 최대 차이 <= 1 (균등 배분)
    assert max(class_sizes) - min(class_sizes) <= 1


# ============================================================================
# 엣지 케이스
# ============================================================================

def test_seven_students_same_name(phase3_assigner):
    """테스트 11: 동명이인 7명 - 각 반에 1명씩"""
    # 모든 학생 이름을 '김철수'로 변경
    for i in range(7):
        phase3_assigner.students[i].이름 = '김철수'

    # 7명만 남기기
    phase3_assigner.students = phase3_assigner.students[:7]

    phase3_assigner.phase3_separate_same_names()

    김철수들 = [s for s in phase3_assigner.students if s.이름 == '김철수']

    # 모두 배정됨
    assert all(s.assigned_class is not None for s in 김철수들)

    # 각 반에 1명씩
    assigned_classes = [s.assigned_class for s in 김철수들]
    assert sorted(assigned_classes) == [1, 2, 3, 4, 5, 6, 7]


def test_eight_students_same_name(phase3_assigner, capsys):
    """테스트 12: 동명이인 8명 - 최대 7명만 배정 가능"""
    # 기존 학생 리스트 초기화 후 김철수 8명만 생성
    phase3_assigner.students = []
    for i in range(8):
        student = Student(
            학년=5, 원반=1, 원번호=i+1,
            이름='김철수',
            성별='남' if i % 2 == 0 else '여',
            점수=90-i,
            특수반=False, 전출=False, 난이도=0, 비고=''
        )
        phase3_assigner.students.append(student)

    phase3_assigner.phase3_separate_same_names()

    김철수들 = [s for s in phase3_assigner.students if s.이름 == '김철수']

    # 동명이인은 같은 반에 배정 불가 → 7개 반에 최대 7명만 배정 가능
    # 8명 중 7명만 배정, 1명은 배정 불가
    assigned = [s for s in 김철수들 if s.assigned_class is not None]
    unassigned = [s for s in 김철수들 if s.assigned_class is None]

    assert len(assigned) == 7
    assert len(unassigned) == 1

    # 각 반에 1명씩 배정됨
    assigned_classes = [s.assigned_class for s in assigned]
    assert sorted(assigned_classes) == [1, 2, 3, 4, 5, 6, 7]

    # 경고 메시지 확인
    captured = capsys.readouterr()
    assert "김철수" in captured.out
    assert "배정할 수 없습니다" in captured.out


def test_output_messages(phase3_assigner, capsys):
    """테스트 13: 출력 메시지 검증"""
    phase3_assigner.phase3_separate_same_names()

    captured = capsys.readouterr()

    # 동명이인 정보 출력
    assert "동명이인:" in captured.out
    assert "김철수" in captured.out
    assert "이영희" in captured.out

    # 완료 메시지
    assert "동명이인 분리 완료" in captured.out
