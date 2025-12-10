"""
규칙 검증 로직 테스트
합반 vs 분반, 합반 vs 동명이인 충돌 검증
"""

import pytest
from collections import defaultdict
import sys
import os

# 상위 디렉토리의 class_assigner 모듈 import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from class_assigner import ClassAssigner, Student


@pytest.fixture
def empty_assigner():
    """빈 ClassAssigner 인스턴스"""
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.students = []
    assigner.classes = {i: [] for i in range(1, 8)}
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.separation_pairs = []
    return assigner


@pytest.fixture
def assigner_with_students():
    """학생 명단이 있는 ClassAssigner 인스턴스"""
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.classes = {i: [] for i in range(1, 8)}
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.separation_pairs = []

    # 학생 명단 생성
    assigner.students = [
        Student(학년=5, 원반=1, 원번호=1, 이름='김철수', 성별='남', 점수=95, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=1, 원번호=2, 이름='이영희', 성별='여', 점수=90, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=2, 원번호=1, 이름='박민수', 성별='남', 점수=85, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=2, 원번호=2, 이름='최지훈', 성별='남', 점수=80, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=3, 원번호=1, 이름='정수진', 성별='여', 점수=75, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=3, 원번호=2, 이름='강감찬', 성별='남', 점수=70, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=4, 원번호=1, 이름='이순신', 성별='남', 점수=65, 특수반=False, 전출=False, 난이도=0, 비고=''),
    ]

    return assigner


@pytest.fixture
def assigner_with_duplicates():
    """동명이인이 있는 학생 명단"""
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.classes = {i: [] for i in range(1, 8)}
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.separation_pairs = []

    # 김철수가 2명, 이영희가 3명 있는 명단
    assigner.students = [
        Student(학년=5, 원반=1, 원번호=1, 이름='김철수', 성별='남', 점수=95, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=1, 원번호=2, 이름='이영희', 성별='여', 점수=90, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=2, 원번호=1, 이름='김철수', 성별='남', 점수=85, 특수반=False, 전출=False, 난이도=0, 비고=''),  # 동명이인
        Student(학년=5, 원반=2, 원번호=2, 이름='박민수', 성별='남', 점수=80, 특수반=False, 전출=False, 난이도=0, 비고=''),
        Student(학년=5, 원반=3, 원번호=1, 이름='이영희', 성별='여', 점수=75, 특수반=False, 전출=False, 난이도=0, 비고=''),  # 동명이인
        Student(학년=5, 원반=3, 원번호=2, 이름='이영희', 성별='여', 점수=70, 특수반=False, 전출=False, 난이도=0, 비고=''),  # 동명이인
    ]

    return assigner


# ============================================================================
# 합반 vs 분반 충돌 테스트
# ============================================================================

def test_together_separation_conflict(empty_assigner):
    """테스트 1: 합반 그룹에 분반 규칙이 있는 경우 예외 발생"""
    # 김철수와 이영희는 합반해야 함
    empty_assigner.together_groups = [{'김철수', '이영희'}]

    # 동시에 김철수와 이영희는 분반해야 함 (모순!)
    empty_assigner.separation_rules = defaultdict(set, {
        '김철수': {'이영희'},
        '이영희': {'김철수'}
    })

    with pytest.raises(ValueError, match="규칙 충돌이 발견되었습니다"):
        empty_assigner._validate_rules()


def test_together_separation_no_conflict(empty_assigner):
    """테스트 2: 합반 그룹과 분반 규칙이 겹치지 않으면 정상"""
    # 김철수와 이영희는 합반
    empty_assigner.together_groups = [{'김철수', '이영희'}]

    # 박민수와 최지훈은 분반 (합반 그룹과 무관)
    empty_assigner.separation_rules = defaultdict(set, {
        '박민수': {'최지훈'},
        '최지훈': {'박민수'}
    })

    # 예외 발생하지 않아야 함
    empty_assigner._validate_rules()


def test_multiple_together_groups_with_separation(empty_assigner):
    """테스트 3: 여러 합반 그룹과 분반 규칙 혼합"""
    # 그룹1: 김철수, 이영희
    # 그룹2: 박민수, 최지훈
    empty_assigner.together_groups = [
        {'김철수', '이영희'},
        {'박민수', '최지훈'}
    ]

    # 그룹2 내부에 분반 규칙 (충돌!)
    empty_assigner.separation_rules = defaultdict(set, {
        '박민수': {'최지훈'},
        '최지훈': {'박민수'}
    })

    with pytest.raises(ValueError, match="규칙 충돌이 발견되었습니다"):
        empty_assigner._validate_rules()


# ============================================================================
# 합반 vs 동명이인 충돌 테스트
# ============================================================================

def test_together_duplicate_names_conflict(assigner_with_duplicates):
    """테스트 4: 합반 그룹에 동명이인이 있는 경우 예외 발생"""
    # 김철수는 명단에 2명 있음, 합반 그룹에 포함하면 충돌!
    assigner_with_duplicates.together_groups = [{'김철수', '박민수'}]

    with pytest.raises(ValueError, match="규칙 충돌이 발견되었습니다"):
        assigner_with_duplicates._validate_rules()


def test_together_three_duplicate_names_conflict(assigner_with_duplicates):
    """테스트 5: 합반 그룹에 3명 동명이인이 있는 경우"""
    # 이영희는 명단에 3명 있음, 합반 그룹에 포함하면 충돌!
    assigner_with_duplicates.together_groups = [{'이영희', '박민수'}]

    with pytest.raises(ValueError, match="규칙 충돌이 발견되었습니다"):
        assigner_with_duplicates._validate_rules()


def test_together_multiple_duplicates_conflict(assigner_with_duplicates):
    """테스트 6: 합반 그룹에 여러 동명이인이 포함된 경우"""
    # 김철수(2명), 이영희(3명) 모두 합반 그룹에 포함 (모순!)
    assigner_with_duplicates.together_groups = [{'김철수', '이영희'}]

    with pytest.raises(ValueError, match="규칙 충돌이 발견되었습니다"):
        assigner_with_duplicates._validate_rules()


def test_together_unique_names_no_conflict(assigner_with_students):
    """테스트 7: 합반 그룹에 동명이인이 아닌 학생들만 있으면 정상"""
    # 모두 유일한 이름
    assigner_with_students.together_groups = [{'김철수', '이영희', '박민수'}]

    # 예외 발생하지 않아야 함
    assigner_with_students._validate_rules()


# ============================================================================
# 복합 충돌 테스트
# ============================================================================

def test_both_conflicts(assigner_with_duplicates):
    """테스트 8: 합반 vs 분반 + 합반 vs 동명이인 충돌 동시 발생"""
    # 김철수(명단에 2명), 박민수가 합반
    assigner_with_duplicates.together_groups = [{'김철수', '박민수'}]

    # 김철수와 박민수는 분반
    assigner_with_duplicates.separation_rules = defaultdict(set, {
        '김철수': {'박민수'},
        '박민수': {'김철수'}
    })

    # 2개의 충돌이 모두 감지되어야 함
    with pytest.raises(ValueError, match="규칙 충돌이 발견되었습니다"):
        assigner_with_duplicates._validate_rules()


def test_multiple_groups_some_conflicts(assigner_with_duplicates):
    """테스트 9: 여러 그룹 중 일부만 충돌"""
    # 그룹1: 정상
    # 그룹2: 충돌 (이영희는 명단에 3명)
    assigner_with_duplicates.together_groups = [
        {'박민수'},
        {'이영희'}  # 충돌!
    ]

    with pytest.raises(ValueError, match="규칙 충돌이 발견되었습니다"):
        assigner_with_duplicates._validate_rules()


# ============================================================================
# 정상 케이스 종합
# ============================================================================

def test_no_conflicts_empty_rules(assigner_with_students):
    """테스트 10: 규칙이 전혀 없으면 정상"""
    # 빈 규칙
    assigner_with_students.together_groups = []
    assigner_with_students.separation_rules = defaultdict(set)

    # 예외 발생하지 않아야 함
    assigner_with_students._validate_rules()


def test_no_conflicts_complex_valid_rules(assigner_with_students):
    """테스트 11: 복잡하지만 유효한 규칙 조합"""
    # 3개의 합반 그룹 (모두 유일한 이름)
    assigner_with_students.together_groups = [
        {'김철수', '이영희'},
        {'박민수', '최지훈', '정수진'},
        {'강감찬', '이순신'}
    ]

    # 그룹 간 분반 규칙 (그룹 내부가 아님)
    assigner_with_students.separation_rules = defaultdict(set, {
        '김철수': {'박민수', '강감찬'},
        '박민수': {'김철수'},
        '강감찬': {'김철수', '이영희'}
    })

    # 예외 발생하지 않아야 함
    assigner_with_students._validate_rules()


# ============================================================================
# 엣지 케이스
# ============================================================================

def test_single_student_together_group(assigner_with_students):
    """테스트 12: 합반 그룹에 학생 1명만 있는 경우"""
    # 1명만 있는 그룹 (의미는 없지만 오류는 아님)
    assigner_with_students.together_groups = [{'김철수'}]

    # 예외 발생하지 않아야 함
    assigner_with_students._validate_rules()


def test_empty_together_group(assigner_with_students):
    """테스트 13: 빈 합반 그룹이 있는 경우"""
    # 빈 그룹
    assigner_with_students.together_groups = [set()]

    # 예외 발생하지 않아야 함
    assigner_with_students._validate_rules()


def test_large_together_group_with_duplicates(assigner_with_duplicates):
    """테스트 14: 큰 합반 그룹에 동명이인이 섞여있는 경우"""
    # 김철수는 명단에 2명, 합반 그룹에 포함하면 충돌
    assigner_with_duplicates.together_groups = [{'김철수', '박민수'}]

    with pytest.raises(ValueError, match="규칙 충돌이 발견되었습니다"):
        assigner_with_duplicates._validate_rules()
