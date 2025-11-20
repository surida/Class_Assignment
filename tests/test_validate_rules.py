"""
_validate_rules 함수 테스트
합반/분반 규칙 충돌 검증 로직 테스트
"""

import pytest
from collections import defaultdict
import sys
import os

# 상위 디렉토리의 class_assigner 모듈 import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from class_assigner import ClassAssigner


@pytest.fixture
def mock_assigner():
    """
    ClassAssigner 인스턴스를 파일 로드 없이 생성하는 fixture
    separation_rules와 together_groups를 직접 설정 가능
    """
    assigner = ClassAssigner.__new__(ClassAssigner)
    assigner.separation_rules = defaultdict(set)
    assigner.together_groups = []
    assigner.classes = {i: [] for i in range(1, 8)}
    assigner.students = []
    return assigner


# ============================================================================
# 정상 케이스 (예외 없음)
# ============================================================================

def test_empty_rules(mock_assigner):
    """테스트 1: 빈 규칙 - 충돌 없음"""
    # 기본 상태: separation_rules={}, together_groups=[]
    mock_assigner._validate_rules()
    # 예외가 발생하지 않으면 성공


def test_only_separation_rules(mock_assigner):
    """테스트 2: 분반 규칙만 있음 - 충돌 없음"""
    mock_assigner.separation_rules = defaultdict(set, {
        '강준우': {'강하서'},
        '강하서': {'강준우'},
        '권하나': {'박철수'}
    })
    mock_assigner.together_groups = []

    mock_assigner._validate_rules()
    # 합반 그룹이 없으므로 충돌 발생 불가


def test_only_together_rules(mock_assigner):
    """테스트 3: 합반 규칙만 있음 - 충돌 없음"""
    mock_assigner.separation_rules = defaultdict(set)
    mock_assigner.together_groups = [
        {'오시후', '오예아'},
        {'김철수', '박영희'}
    ]

    mock_assigner._validate_rules()
    # 분반 규칙이 없으므로 충돌 발생 불가


def test_no_conflict_mixed(mock_assigner):
    """테스트 4: 충돌 없는 혼합 규칙"""
    # A와 B는 합반, A와 C는 분반 (충돌 없음)
    mock_assigner.separation_rules = defaultdict(set, {
        '강준우': {'권서은'},
        '권서은': {'강준우'}
    })
    mock_assigner.together_groups = [
        {'강준우', '강하서'},  # 강준우-강하서 합반 (권서은과는 관련 없음)
        {'김철수', '박영희'}
    ]

    mock_assigner._validate_rules()
    # 합반 그룹 내에서 분반 규칙이 없으므로 충돌 없음


def test_single_person_group(mock_assigner):
    """테스트 5: 1명만 있는 합반 그룹 - 충돌 없음"""
    mock_assigner.separation_rules = defaultdict(set, {
        '강준우': {'강하서'}
    })
    mock_assigner.together_groups = [
        {'강준우'}  # 1명 그룹: 자기 자신과 비교 안 함 (name1 != name2 조건)
    ]

    mock_assigner._validate_rules()
    # 1명 그룹은 충돌 불가


# ============================================================================
# 충돌 케이스 (ValueError 발생)
# ============================================================================

def test_conflict_two_persons(mock_assigner):
    """테스트 6: 2명 합반 그룹에서 서로 분반 규칙 - 충돌"""
    mock_assigner.separation_rules = defaultdict(set, {
        '강준우': {'강하서'},
        '강하서': {'강준우'}
    })
    mock_assigner.together_groups = [
        {'강준우', '강하서'}  # 동시에 합반이면서 분반
    ]

    with pytest.raises(ValueError) as exc_info:
        mock_assigner._validate_rules()

    # 예외 메시지 검증
    assert "규칙 충돌" in str(exc_info.value)


def test_conflict_three_persons(mock_assigner, capsys):
    """테스트 7: 3명 그룹에서 일부 분반 충돌"""
    # A, B, C가 합반인데 A-C는 분반 규칙
    mock_assigner.separation_rules = defaultdict(set, {
        '강준우': {'권서은'},
        '권서은': {'강준우'}
    })
    mock_assigner.together_groups = [
        {'강준우', '강하서', '권서은'}  # 강준우-권서은 충돌
    ]

    with pytest.raises(ValueError) as exc_info:
        mock_assigner._validate_rules()

    assert "규칙 충돌" in str(exc_info.value)

    # 출력 메시지에서 학생 이름 확인
    captured = capsys.readouterr()
    assert "강준우" in captured.out and "권서은" in captured.out


def test_conflict_bidirectional(mock_assigner):
    """테스트 8: 양방향 분반 규칙과 합반 충돌"""
    # A → B 분반, B → A 분반 (양방향)
    mock_assigner.separation_rules = defaultdict(set, {
        '김철수': {'박영희'},
        '박영희': {'김철수'}
    })
    mock_assigner.together_groups = [
        {'김철수', '박영희'}
    ]

    with pytest.raises(ValueError) as exc_info:
        mock_assigner._validate_rules()

    assert "규칙 충돌" in str(exc_info.value)


def test_multiple_groups_with_conflict(mock_assigner):
    """테스트 9: 여러 그룹에서 동시 충돌"""
    mock_assigner.separation_rules = defaultdict(set, {
        '학생A': {'학생B'},
        '학생B': {'학생A'},
        '학생C': {'학생D'},
        '학생D': {'학생C'}
    })
    mock_assigner.together_groups = [
        {'학생A', '학생B'},  # 첫 번째 충돌
        {'학생C', '학생D'}   # 두 번째 충돌
    ]

    with pytest.raises(ValueError) as exc_info:
        mock_assigner._validate_rules()

    # 최소 하나의 충돌이 감지되어야 함
    assert "규칙 충돌" in str(exc_info.value)


# ============================================================================
# 엣지 케이스
# ============================================================================

def test_large_group_no_conflict(mock_assigner):
    """테스트 10: 대용량 그룹 (10명) - 충돌 없음"""
    # 10명이 모두 합반이지만 서로 분반 규칙 없음
    large_group = {f'학생{i}' for i in range(1, 11)}

    mock_assigner.separation_rules = defaultdict(set, {
        '학생1': {'외부학생'},  # 그룹 외부와의 분반 규칙
        '외부학생': {'학생1'}
    })
    mock_assigner.together_groups = [large_group]

    mock_assigner._validate_rules()
    # 그룹 내부에는 분반 규칙이 없으므로 충돌 없음


def test_complex_separation_network(mock_assigner):
    """테스트 11: 복잡한 분반 네트워크 - 충돌 없음"""
    # 복잡한 분반 관계가 있지만 합반 그룹과 겹치지 않음
    mock_assigner.separation_rules = defaultdict(set, {
        'A': {'X', 'Y', 'Z'},
        'B': {'X', 'Y'},
        'C': {'Z'},
        'X': {'A', 'B'},
        'Y': {'A', 'B'},
        'Z': {'A', 'C'}
    })
    mock_assigner.together_groups = [
        {'A', 'B', 'C'},  # A, B, C는 서로 분반 규칙 없음
        {'D', 'E', 'F'}
    ]

    mock_assigner._validate_rules()
    # A-B, A-C, B-C 간에는 분반 규칙이 없으므로 충돌 없음


def test_partial_overlap_conflict(mock_assigner, capsys):
    """테스트 12: 부분 중첩 충돌"""
    # 여러 그룹 중 하나만 충돌
    mock_assigner.separation_rules = defaultdict(set, {
        '충돌A': {'충돌B'}
    })
    mock_assigner.together_groups = [
        {'정상1', '정상2', '정상3'},  # 충돌 없음
        {'충돌A', '충돌B'},            # 충돌 있음
        {'정상4', '정상5'}             # 충돌 없음
    ]

    with pytest.raises(ValueError) as exc_info:
        mock_assigner._validate_rules()

    assert "규칙 충돌" in str(exc_info.value)

    # 출력 메시지에서 학생 이름 확인
    captured = capsys.readouterr()
    assert "충돌A" in captured.out and "충돌B" in captured.out


# ============================================================================
# 출력 메시지 검증 (선택적)
# ============================================================================

def test_success_message_output(mock_assigner, capsys):
    """테스트 13: 성공 시 출력 메시지 검증"""
    mock_assigner.separation_rules = defaultdict(set)
    mock_assigner.together_groups = []

    mock_assigner._validate_rules()

    captured = capsys.readouterr()
    assert "규칙 충돌 없음" in captured.out
    assert "모든 규칙이 논리적으로 일관됨" in captured.out


def test_conflict_message_output(mock_assigner, capsys):
    """테스트 14: 충돌 시 출력 메시지 검증"""
    mock_assigner.separation_rules = defaultdict(set, {
        '학생A': {'학생B'}
    })
    mock_assigner.together_groups = [
        {'학생A', '학생B'}
    ]

    with pytest.raises(ValueError):
        mock_assigner._validate_rules()

    captured = capsys.readouterr()
    assert "규칙 충돌 발견" in captured.out
    assert "학생A" in captured.out and "학생B" in captured.out
    assert "해결 방법" in captured.out
