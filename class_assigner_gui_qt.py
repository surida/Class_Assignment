"""
자동 학급 편성 프로그램 - PyQt6 GUI 버전
PyQt6 기반 크로스플랫폼 사용자 인터페이스
"""

import sys
import os
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from class_assigner import ClassAssigner, get_base_path


class AssignmentThread(QThread):
    """학급 편성을 백그라운드에서 실행하는 스레드"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)  # success, message

    def __init__(self, student_file, rules_file, output_file):
        super().__init__()
        self.student_file = student_file
        self.rules_file = rules_file
        self.output_file = output_file

    def run(self):
        """학급 편성 실행"""
        try:
            self.log_signal.emit("=" * 70)
            self.log_signal.emit("🎓 자동 학급 편성 시작")
            self.log_signal.emit("=" * 70)
            self.log_signal.emit("")

            # 표준 출력 캡처
            import io
            import contextlib

            output_buffer = io.StringIO()

            with contextlib.redirect_stdout(output_buffer):
                assigner = ClassAssigner(
                    student_file=self.student_file,
                    rules_file=self.rules_file
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

        # 5학년 명단 파일
        student_label = QLabel("📚 5학년 명단 파일:")
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

        return widget

    def load_default_files(self):
        """기본 파일 경로 로드"""
        base_path = get_base_path()
        default_student = os.path.join(base_path, '01 5학년_가상 명단.xlsx')
        default_rules = os.path.join(base_path, '02 분반 합반할 학생 규칙.xlsx')

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
            QMessageBox.critical(self, "오류", "5학년 명단 파일을 선택해주세요.")
            return

        if not self.rules_file_path or not os.path.exists(self.rules_file_path):
            QMessageBox.critical(self, "오류", "분반/합반 규칙 파일을 선택해주세요.")
            return

        # 출력 파일 경로
        output_dir = os.path.dirname(self.student_file_path)
        output_file = os.path.join(output_dir, '03 6학년 배정 결과.xlsx')

        # UI 비활성화
        self.execute_btn.setEnabled(False)
        self.clear_log()

        # 백그라운드 스레드 생성 및 실행
        self.assignment_thread = AssignmentThread(
            self.student_file_path,
            self.rules_file_path,
            output_file
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
            QMessageBox.information(self, "완료", message)
        else:
            QMessageBox.critical(self, "오류", message)


def main():
    """PyQt6 애플리케이션 실행"""
    app = QApplication(sys.argv)

    # 애플리케이션 스타일 설정
    app.setStyle('Fusion')

    window = ClassAssignerGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
