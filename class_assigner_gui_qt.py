"""
자동 학급 편성 프로그램 - PyQt6 GUI 버전
PyQt6 기반 크로스플랫폼 사용자 인터페이스
"""

import sys
import os
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox, QFrame,
    QSpinBox, QListWidget, QListWidgetItem, QLineEdit, QGroupBox,
    QInputDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from class_assigner import ClassAssigner, get_base_path


class ClassAssignerStartGUI(QMainWindow):
    """시작 화면: 새로 시작 vs 결과 불러오기"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("🎓 자동 학급 편성 프로그램")
        self.setGeometry(100, 100, 500, 400)

        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        central_widget.setLayout(layout)

        # 제목
        title_label = QLabel("🎓 자동 학급 편성 프로그램")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 부제목
        subtitle_label = QLabel("시작 방법을 선택하세요")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)

        layout.addSpacing(20)

        # 새로 시작 버튼
        new_btn = QPushButton("🆕 새로 시작\n(자동 배정 실행)")
        new_btn.setMinimumHeight(100)
        btn_font = QFont()
        btn_font.setPointSize(14)
        new_btn.setFont(btn_font)
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        new_btn.clicked.connect(self.start_new_assignment)
        layout.addWidget(new_btn)

        # 결과 불러오기 버튼
        load_btn = QPushButton("📂 결과 파일 불러오기\n(수동 조정만)")
        load_btn.setMinimumHeight(100)
        load_btn.setFont(btn_font)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        load_btn.clicked.connect(self.load_result_file)
        layout.addWidget(load_btn)

        layout.addStretch()

    def start_new_assignment(self):
        """기존 ClassAssignerGUI 실행"""
        self.assignment_gui = ClassAssignerGUI()
        self.assignment_gui.show()
        self.close()

    def load_result_file(self):
        """결과 파일 선택 → InteractiveEditorGUI 실행"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "배정 결과 파일 선택",
            get_base_path(),
            "Excel files (*.xlsx)"
        )

        if not file_path:
            return

        # 파일 타입 검증
        if not ClassAssigner.is_result_file(file_path):
            QMessageBox.warning(
                self,
                "오류",
                "배정 결과 파일이 아닙니다.\n'새로 시작'을 선택하세요."
            )
            return

        # InteractiveEditorGUI 실행
        try:
            self.editor_gui = InteractiveEditorGUI(file_path)
            self.editor_gui.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                f"파일 로드 중 오류가 발생했습니다:\n\n{str(e)}"
            )


class AssignmentThread(QThread):
    """학급 편성을 백그라운드에서 실행하는 스레드"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)  # success, message

    def __init__(self, student_file, rules_file, output_file, target_class_count):
        super().__init__()
        self.student_file = student_file
        self.rules_file = rules_file
        self.output_file = output_file
        self.target_class_count = target_class_count

    def run(self):
        """학급 편성 실행"""
        try:
            self.log_signal.emit("=" * 70)
            self.log_signal.emit("🎓 자동 학급 편성 시작")
            self.log_signal.emit(f"➡️ 목표 학급 수: {self.target_class_count}개 반")
            self.log_signal.emit("=" * 70)
            self.log_signal.emit("")

            # 표준 출력 캡처
            import io
            import contextlib

            output_buffer = io.StringIO()

            with contextlib.redirect_stdout(output_buffer):
                assigner = ClassAssigner(
                    student_file=self.student_file,
                    rules_file=self.rules_file,
                    target_class_count=self.target_class_count
                )
                assigner.run(output_file=self.output_file)

            # 캡처된 출력을 GUI에 표시
            captured_output = output_buffer.getvalue()
            for line in captured_output.split('\n'):
                if line.strip():
                    self.log_signal.emit(line)

            self.log_signal.emit("")
            self.log_signal.emit("=" * 70)
            self.log_signal.emit(f"✅ 완료! 결과 파일이 생성되었습니다:")
            self.log_signal.emit(f"📁 {self.output_file}")
            self.log_signal.emit("=" * 70)

            self.finished_signal.emit(
                True,
                f"학급 편성이 완료되었습니다!\n\n결과 파일:\n{self.output_file}"
            )

        except Exception as e:
            self.log_signal.emit("")
            self.log_signal.emit("=" * 70)
            self.log_signal.emit(f"❌ 오류 발생: {str(e)}")
            self.log_signal.emit("=" * 70)

            import traceback
            error_detail = traceback.format_exc()
            self.log_signal.emit("")
            self.log_signal.emit("상세 오류 정보:")
            self.log_signal.emit(error_detail)

            self.finished_signal.emit(
                False,
                f"학급 편성 중 오류가 발생했습니다:\n\n{str(e)}\n\n자세한 내용은 진행 상황 창을 확인하세요."
            )


class ClassAssignerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # 파일 경로 저장
        self.student_file_path = None
        self.rules_file_path = None
        self.assignment_thread = None

        # UI 구성
        self.init_ui()

        # 기본 파일 경로 설정
        self.load_default_files()

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("🎓 자동 학급 편성 프로그램")
        self.setGeometry(100, 100, 700, 600)

        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)

        # 제목
        title_label = QLabel("🎓 자동 학급 편성 프로그램")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # 구분선
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line1)

        # 파일 선택 영역
        main_layout.addWidget(self.create_file_section())

        # 실행 버튼
        self.execute_btn = QPushButton("🚀 학급 편성 시작")
        self.execute_btn.setMinimumHeight(60)
        exec_font = QFont()
        exec_font.setPointSize(14)
        exec_font.setBold(True)
        self.execute_btn.setFont(exec_font)
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.execute_btn.clicked.connect(self.execute_assignment)
        main_layout.addWidget(self.execute_btn)

        # 구분선
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line2)

        # 진행 상황 표시
        progress_label = QLabel("📊 진행 상황:")
        progress_font = QFont()
        progress_font.setPointSize(12)
        progress_font.setBold(True)
        progress_label.setFont(progress_font)
        main_layout.addWidget(progress_label)

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setFont(QFont("Courier", 10))
        self.progress_text.setMinimumHeight(200)
        main_layout.addWidget(self.progress_text)

        # 초기 메시지
        self.log_message("대기 중... 파일을 선택하고 '학급 편성 시작' 버튼을 눌러주세요.")

    def create_file_section(self):
        """파일 선택 섹션 생성"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        widget.setLayout(layout)

        # 학생 명단 파일
        student_label = QLabel("📚 학생 명단 파일:")
        student_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(student_label)

        student_layout = QHBoxLayout()
        self.student_file_label = QLabel("파일을 선택해주세요")
        self.student_file_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 8px;
                color: #666666;
            }
        """)
        self.student_file_label.setMinimumHeight(35)
        student_layout.addWidget(self.student_file_label, stretch=1)

        student_btn = QPushButton("📁 파일 선택")
        student_btn.setMinimumWidth(120)
        student_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 3px;
                border: none;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        student_btn.clicked.connect(self.select_student_file)
        student_layout.addWidget(student_btn)

        layout.addLayout(student_layout)

        # 간격
        layout.addSpacing(15)

        # 분반/합반 규칙 파일
        rules_label = QLabel("📋 분반/합반 규칙 파일:")
        rules_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(rules_label)

        rules_layout = QHBoxLayout()
        self.rules_file_label = QLabel("파일을 선택해주세요")
        self.rules_file_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 8px;
                color: #666666;
            }
        """)
        self.rules_file_label.setMinimumHeight(35)
        rules_layout.addWidget(self.rules_file_label, stretch=1)

        rules_btn = QPushButton("📁 파일 선택")
        rules_btn.setMinimumWidth(120)
        rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 3px;
                border: none;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        rules_btn.clicked.connect(self.select_rules_file)
        rules_layout.addWidget(rules_btn)

        layout.addLayout(rules_layout)

        # 간격
        layout.addSpacing(15)

        # 진급 학급 수 입력
        count_label = QLabel("진급 학급 수 (내년 반 개수):")
        count_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(count_label)

        count_layout = QHBoxLayout()
        self.class_count_spin = QSpinBox()
        self.class_count_spin.setRange(1, 20)  # 1반부터 20반까지 허용
        self.class_count_spin.setValue(7)      # 기본값 7
        self.class_count_spin.setMinimumHeight(35)
        self.class_count_spin.setFont(QFont("", 11))
        self.class_count_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
            }
        """)
        
        # 설명 라벨
        desc_label = QLabel(" 개 반으로 편성")
        desc_label.setFont(QFont("", 11))
        
        count_layout.addWidget(self.class_count_spin)
        count_layout.addWidget(desc_label)
        count_layout.addStretch(1)  # 왼쪽 정렬
        
        layout.addLayout(count_layout)

        return widget

    def load_default_files(self):
        """기본 파일 경로 로드"""
        base_dir = os.getcwd()
        default_student = os.path.join(base_dir, "01 가상 명단.xlsx")
        default_rules = os.path.join(base_dir, "02 분반 합반할 학생 규칙.xlsx")

        if os.path.exists(default_student):
            self.student_file_path = default_student
            self.update_file_label(self.student_file_label, default_student)

        if os.path.exists(default_rules):
            self.rules_file_path = default_rules
            self.update_file_label(self.rules_file_label, default_rules)

    def update_file_label(self, label, filepath):
        """파일 라벨 업데이트"""
        filename = os.path.basename(filepath)
        label.setText(f"✅ {filename}")
        label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #4CAF50;
                border-radius: 3px;
                padding: 8px;
                color: #2E7D32;
                font-weight: bold;
            }
        """)

    def select_student_file(self):
        """5학년 명단 파일 선택"""
        initialdir = (os.path.dirname(self.student_file_path)
                     if self.student_file_path else get_base_path())

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "5학년 명단 파일을 선택하세요",
            initialdir,
            "Excel files (*.xlsx);;All files (*.*)"
        )

        if filename:
            self.student_file_path = filename
            self.update_file_label(self.student_file_label, filename)
            self.log_message(f"✅ 명단 파일 선택됨: {os.path.basename(filename)}")

    def select_rules_file(self):
        """분반/합반 규칙 파일 선택"""
        initialdir = (os.path.dirname(self.rules_file_path)
                     if self.rules_file_path else get_base_path())

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "분반/합반 규칙 파일을 선택하세요",
            initialdir,
            "Excel files (*.xlsx);;All files (*.*)"
        )

        if filename:
            self.rules_file_path = filename
            self.update_file_label(self.rules_file_label, filename)
            self.log_message(f"✅ 규칙 파일 선택됨: {os.path.basename(filename)}")

    def log_message(self, message):
        """진행 상황 로그 추가"""
        self.progress_text.append(message)

    def clear_log(self):
        """로그 초기화"""
        self.progress_text.clear()

    def execute_assignment(self):
        """학급 편성 실행"""
        # 파일 경로 확인
        if not self.student_file_path or not os.path.exists(self.student_file_path):
            QMessageBox.critical(self, "오류", "학생 명단 파일을 선택해주세요.")
            return

        if not self.rules_file_path or not os.path.exists(self.rules_file_path):
            QMessageBox.critical(self, "오류", "분반/합반 규칙 파일을 선택해주세요.")
            return

        # 출력 파일 경로
        output_dir = os.path.dirname(self.student_file_path)
        output_file = os.path.join(output_dir, '03 배정 결과.xlsx')

        # UI 비활성화
        self.execute_btn.setEnabled(False)
        self.clear_log()

        # 백그라운드 스레드 생성 및 실행
        target_count = self.class_count_spin.value()
        self.assignment_thread = AssignmentThread(
            self.student_file_path,
            self.rules_file_path,
            output_file,
            target_count
        )
        self.assignment_thread.log_signal.connect(self.log_message)
        self.assignment_thread.finished_signal.connect(self.on_assignment_finished)
        self.assignment_thread.start()

    def on_assignment_finished(self, success, message):
        """학급 편성 완료 처리"""
        # UI 다시 활성화
        self.execute_btn.setEnabled(True)

        # 결과 메시지 표시
        if success:
            # 완료 후 수동 조정 화면으로 이동할지 물어보기
            reply = QMessageBox.question(
                self,
                "완료",
                f"{message}\n\n수동 조정 화면으로 이동하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # InteractiveEditorGUI로 전환
                output_file = os.path.join(
                    os.path.dirname(self.student_file_path),
                    '03 배정 결과.xlsx'
                )
                self.editor_gui = InteractiveEditorGUI(output_file)
                self.editor_gui.show()
                self.close()
        else:
            QMessageBox.critical(self, "오류", message)


class InteractiveEditorGUI(QMainWindow):
    """수동 조정 화면"""

    def __init__(self, result_file: str):
        super().__init__()

        # Assigner 로드
        self.assigner = ClassAssigner(
            student_file="",  # 사용 안 함
            rules_file="",    # 불필요 (결과 파일에 포함됨)
            target_class_count=7  # 임시값, load_from_result에서 업데이트
        )

        # 결과 파일 로드 (규칙 포함)
        self.assigner.load_from_result(result_file)

        self.current_class = 1
        self.init_ui()

        # 첫 번째 반 자동 선택
        if self.class_list.count() > 0:
            self.class_list.setCurrentRow(0)

    def init_ui(self):
        """Master-Detail 레이아웃"""
        self.setWindowTitle("🎓 학급 편성 수동 조정")
        self.setGeometry(100, 100, 1000, 700)

        # 메인 레이아웃
        main_widget = QWidget()
        layout = QHBoxLayout()

        # 왼쪽: 반 목록
        left_panel = self.create_class_list_panel()
        layout.addWidget(left_panel, stretch=1)

        # 중앙: 학생 목록
        center_panel = self.create_student_list_panel()
        layout.addWidget(center_panel, stretch=3)

        # 오른쪽: 컨트롤 패널
        right_panel = self.create_control_panel()
        layout.addWidget(right_panel, stretch=1)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def create_class_list_panel(self):
        """반 선택 패널"""
        widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel("반 목록")
        label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(label)

        self.class_list = QListWidget()
        for i in range(1, self.assigner.target_class_count + 1):
            count = len(self.assigner.classes[i])
            item = QListWidgetItem(f"6-{i}반 ({count}명)")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.class_list.addItem(item)

        self.class_list.currentRowChanged.connect(self.on_class_selected)
        layout.addWidget(self.class_list)

        # Export 버튼
        export_btn = QPushButton("📥 Export to Excel")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 5px;
                border: none;
                padding: 10px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        export_btn.clicked.connect(self.export_to_excel)
        layout.addWidget(export_btn)

        widget.setLayout(layout)
        return widget

    def create_student_list_panel(self):
        """학생 목록 패널"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 검색 바
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 검색:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("학생 이름 입력...")
        self.search_box.textChanged.connect(self.filter_students)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # 학생 리스트
        self.student_list = QListWidget()
        self.student_list.setFont(QFont("", 11))
        layout.addWidget(self.student_list)

        widget.setLayout(layout)
        return widget

    def create_control_panel(self):
        """컨트롤 패널"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 이동 버튼
        move_btn = QPushButton("→ 다른 반으로 이동")
        move_btn.setMinimumHeight(50)
        move_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                border: none;
                padding: 10px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        move_btn.clicked.connect(self.move_student)
        layout.addWidget(move_btn)

        # 통계
        stats_group = QGroupBox("📊 반 통계")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel()
        self.stats_label.setFont(QFont("", 10))
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # 범례
        legend_group = QGroupBox("🎨 색상 범례")
        legend_layout = QVBoxLayout()
        legend_layout.addWidget(QLabel("🔴 특수반 학생"))
        legend_layout.addWidget(QLabel("🟡 분반 규칙 있음"))
        legend_layout.addWidget(QLabel("🔵 합반 규칙 있음"))
        legend_layout.addWidget(QLabel("⚪ 일반 학생"))
        legend_group.setLayout(legend_layout)
        layout.addWidget(legend_group)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def on_class_selected(self, row):
        """반 선택 시 학생 목록 업데이트"""
        if row < 0:
            return

        item = self.class_list.item(row)
        class_num = item.data(Qt.ItemDataRole.UserRole)
        self.current_class = class_num

        self.update_student_list()
        self.update_statistics()

    def update_student_list(self):
        """학생 목록 업데이트"""
        self.student_list.clear()

        students = self.assigner.classes[self.current_class]
        students.sort(key=lambda s: s.이름)

        for student in students:
            # 색상 코딩
            if student.특수반:
                icon = "🔴"
            elif student.이름 in self.assigner.separation_rules:
                icon = "🟡"
            elif self._is_in_together_group(student):
                icon = "🔵"
            else:
                icon = "⚪"

            # 제약사항 정보 추가
            constraint_info = self.get_constraint_info(student)
            item_text = f"{icon} {student.이름} ({student.성별}){constraint_info}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, student)
            self.student_list.addItem(item)

    def _is_in_together_group(self, student):
        """합반 그룹 학생 확인"""
        for group in self.assigner.together_groups:
            if student.이름 in group:
                return True
        return False

    def _find_student_by_name(self, name):
        """이름으로 학생 찾기"""
        for student in self.assigner.students:
            if student.이름 == name:
                return student
        return None

    def _get_together_group(self, student):
        """학생이 속한 합반 그룹 반환"""
        for group in self.assigner.together_groups:
            if student.이름 in group:
                return group
        return None

    def get_constraint_info(self, student):
        """
        학생의 제약사항 정보를 문자열로 반환

        Returns:
            "분반: 김철수(3반), 이민준(5반)" 또는
            "합반: 박영희, 정지우" 또는
            "" (제약사항 없음)
        """
        parts = []

        # 1. 분반 규칙 정보
        if student.이름 in self.assigner.separation_rules:
            targets = self.assigner.separation_rules[student.이름]

            # 각 분반 대상의 현재 반 찾기
            target_info = []
            for target_name in targets:
                target_student = self._find_student_by_name(target_name)
                if target_student and target_student.assigned_class:
                    target_info.append(f"{target_name}({target_student.assigned_class}반)")
                else:
                    target_info.append(target_name)

            if target_info:
                parts.append(f"분반: {', '.join(target_info)}")

        # 2. 합반 규칙 정보
        together_group = self._get_together_group(student)
        if together_group:
            # 자기 자신 제외
            others = [name for name in together_group if name != student.이름]
            if others:
                parts.append(f"합반: {', '.join(others)}")

        return " - " + " | ".join(parts) if parts else ""

    def get_valid_target_classes(self, student):
        """
        학생이 이동 가능한 반 목록 반환

        Args:
            student: 이동할 학생

        Returns:
            이동 가능한 반 번호 리스트 (예: [1, 2, 4, 6, 7])
        """
        valid_classes = []

        for class_num in range(1, self.assigner.target_class_count + 1):
            # 현재 반은 제외
            if class_num == self.current_class:
                continue

            # 제약사항 검증
            can_move = True

            # 1. 분반 규칙 검증
            if not self.assigner._can_assign(student, class_num):
                can_move = False

            # 2. 동명이인 검증
            same_names = [s for s in self.assigner.classes[class_num]
                         if s.이름 == student.이름]
            if same_names:
                can_move = False

            if can_move:
                valid_classes.append(class_num)

        return valid_classes

    def update_statistics(self):
        """통계 업데이트"""
        students = self.assigner.classes[self.current_class]

        male_count = sum(1 for s in students if s.성별 == '남')
        female_count = sum(1 for s in students if s.성별 == '여')
        effective_count = self.assigner._get_effective_count(self.current_class)
        special_count = sum(1 for s in students if s.특수반)
        difficulty_sum = sum(s.난이도 for s in students)

        stats_text = f"""
학생 수: {len(students)}명
유효 인원: {effective_count}명

남학생: {male_count}명
여학생: {female_count}명

특수반: {special_count}명
난이도 합: {difficulty_sum:.1f}
        """

        self.stats_label.setText(stats_text.strip())

    def filter_students(self, text):
        """학생 검색 필터"""
        for i in range(self.student_list.count()):
            item = self.student_list.item(i)
            student = item.data(Qt.ItemDataRole.UserRole)

            if text.lower() in student.이름.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def move_student(self):
        """학생 이동"""
        current_item = self.student_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "경고", "이동할 학생을 선택하세요.")
            return

        student = current_item.data(Qt.ItemDataRole.UserRole)

        # 이동 가능한 반만 필터링
        valid_classes = self.get_valid_target_classes(student)

        if not valid_classes:
            QMessageBox.warning(
                self,
                "이동 불가",
                f"{student.이름} 학생은 제약사항 때문에\n어느 반으로도 이동할 수 없습니다."
            )
            return

        # 대상 반 선택 다이얼로그 (이동 가능한 반만 표시)
        items = [f"{i}반" for i in valid_classes]
        target_str, ok = QInputDialog.getItem(
            self,
            "반 선택",
            f"{student.이름} 학생을 이동할 반을 선택하세요:",
            items,
            0,
            False
        )

        if not ok:
            return

        # 선택된 반 번호 추출
        target_class = int(target_str.split('반')[0])

        # 합반 규칙 경고
        together_group = None
        for group in self.assigner.together_groups:
            if student.이름 in group:
                together_group = group
                break

        if together_group:
            group_names = list(together_group)
            reply = QMessageBox.question(
                self,
                "합반 규칙 경고",
                f"⚠️ {student.이름} 학생은 합반 그룹입니다.\n\n"
                f"그룹 구성원: {', '.join(group_names)}\n\n"
                f"그룹에서 분리하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

        # 이동 실행
        self.assigner.classes[self.current_class].remove(student)
        student.assigned_class = target_class
        self.assigner.classes[target_class].append(student)

        # UI 업데이트
        self.update_student_list()
        self.update_statistics()
        self.update_class_list_counts()

        QMessageBox.information(
            self,
            "완료",
            f"✅ {student.이름} 학생을 {target_class}반으로 이동했습니다."
        )

    def update_class_list_counts(self):
        """반 목록의 인원수 업데이트"""
        for i in range(self.class_list.count()):
            item = self.class_list.item(i)
            class_num = item.data(Qt.ItemDataRole.UserRole)
            count = len(self.assigner.classes[class_num])
            item.setText(f"6-{class_num}반 ({count}명)")

    def export_to_excel(self):
        """Excel 파일로 내보내기 (Save As)"""
        # Save As 다이얼로그
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "결과 파일 저장",
            os.path.join(get_base_path(), "03 배정 결과.xlsx"),
            "Excel files (*.xlsx)"
        )

        if not file_path:
            return

        # 파일 생성
        try:
            self.assigner.generate_output(file_path)
            QMessageBox.information(
                self,
                "완료",
                f"✅ 파일이 저장되었습니다:\n\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                f"❌ 파일 저장 중 오류:\n\n{str(e)}"
            )


def main():
    """PyQt6 애플리케이션 실행"""
    app = QApplication(sys.argv)

    # 애플리케이션 스타일 설정
    app.setStyle('Fusion')

    # 시작 화면부터 시작
    window = ClassAssignerStartGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
