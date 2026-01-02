"""
자동 학급 편성 프로그램 - PyQt6 GUI 버전
PyQt6 기반 크로스플랫폼 사용자 인터페이스
"""

# Version Information
VERSION = "v2.8"  # Update this for each release

import sys
import os
import threading
import webbrowser
import subprocess
import platform
from logger_config import logger, get_log_dir  # Import logger and log dir function
import traceback
import logging
import unicodedata
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QListWidget, QPushButton,
                             QMessageBox, QFileDialog, QListWidgetItem, QFrame,
                             QGraphicsDropShadowEffect, QComboBox, QStyledItemDelegate,
                             QStyle, QTreeWidget, QTreeWidgetItem, QAbstractItemView,
                             QHeaderView, QSplitter, QSpinBox, QTextEdit, QLineEdit,
                             QGroupBox, QInputDialog, QStyleOptionViewItem, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QRect, QPoint, QMimeData
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QPainter, QLinearGradient, QPalette, QDrag

def create_circle_icon(color_code, size=16):
    """Creates a colored circle icon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color_code))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(0, 0, size, size)
    painter.end()
    return QIcon(pixmap)

def create_composite_icon(colors, size=16):
    """Creates an icon with multiple colored circles"""
    if not colors:
        return QIcon()
    
    width = size * len(colors) + (2 * (len(colors) - 1)) # Add spacing
    pixmap = QPixmap(width, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    
    for i, color_code in enumerate(colors):
        painter.setBrush(QColor(color_code))
        x = i * (size + 2) # 2px spacing default
        painter.drawEllipse(x, 0, size, size)
        
    painter.end()
    return QIcon(pixmap)
from class_assigner import ClassAssigner, get_base_path

# 피드백 폼 URL (전역 상수)
FEEDBACK_FORM_URL = "https://forms.gle/qzkLKsSCeAAZ2HFP7"


def setup_help_menu(window):
    """공통 도움말 메뉴 설정 (모든 QMainWindow에서 사용)"""
    menubar = window.menuBar()

    # 도움말 메뉴
    help_menu = menubar.addMenu("도움말")

    # 피드백 보내기
    feedback_action = help_menu.addAction("💬 피드백 보내기")
    feedback_action.triggered.connect(lambda: open_feedback_form())

    # 로그 파일 위치 열기
    log_action = help_menu.addAction("📁 로그 파일 위치 열기")
    log_action.triggered.connect(lambda: open_log_folder(window))

    help_menu.addSeparator()

    # 프로그램 정보
    about_action = help_menu.addAction("ℹ️ 프로그램 정보")
    about_action.triggered.connect(lambda: show_about(window))


def open_feedback_form():
    """Google Form 피드백 페이지 열기"""
    logger.info("Opening feedback form...")
    webbrowser.open(FEEDBACK_FORM_URL)


def open_log_folder(parent_window=None):
    """로그 파일 폴더를 OS 파일 탐색기로 열기"""
    log_dir = get_log_dir()
    logger.info(f"Opening log folder: {log_dir}")

    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(log_dir)
        elif system == "Darwin":  # Mac
            subprocess.run(["open", log_dir])
        else:  # Linux
            subprocess.run(["xdg-open", log_dir])
    except Exception as e:
        logger.error(f"Failed to open log folder: {e}")
        if parent_window:
            QMessageBox.warning(
                parent_window,
                "알림",
                f"로그 폴더를 열 수 없습니다.\n\n경로: {log_dir}"
            )


def show_about(parent_window):
    """프로그램 정보 다이얼로그"""
    log_dir = get_log_dir()
    QMessageBox.about(
        parent_window,
        "프로그램 정보",
        f"🎓 자동 학급 편성 프로그램\n\n"
        f"버전: {VERSION}\n\n"
        f"문의: angoansu@gmail.com\n\n"
        f"로그 위치:\n{log_dir}"
    )


class ClassAssignerStartGUI(QMainWindow):
    """시작 화면: 새로 시작 vs 결과 불러오기"""

    def __init__(self):
        super().__init__()
        logger.info("ClassAssignerStartGUI Initialized")
        self.init_ui()
        setup_help_menu(self)  # 공통 도움말 메뉴

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(f"🎓 자동 학급 편성 프로그램 - {VERSION}")
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
        
        # Version footer
        version_label = QLabel(f"Version: {VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666666; font-size: 10px;")
        layout.addWidget(version_label)

    def start_new_assignment(self):
        """기존 ClassAssignerGUI 실행"""
        logger.info("Start New Assignment Button Clicked")
        self.assignment_gui = ClassAssignerGUI()
        self.assignment_gui.show()
        self.close()

    def load_result_file(self):
        """결과 파일 선택 → InteractiveEditorGUI 실행"""
        logger.info("Load Result File Button Clicked")
        logger.info("=" * 70)
        logger.info("결과 파일 불러오기 시작")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "배정 결과 파일 선택",
            get_base_path(),
            "Excel files (*.xlsx)"
        )

        if not file_path:
            logger.info("파일 선택 취소됨")
            return

        logger.info(f"Selected result file: {file_path}")
        logger.info(f"파일 존재 여부: {os.path.exists(file_path)}")
        if os.path.exists(file_path):
            logger.info(f"파일 크기: {os.path.getsize(file_path)} bytes")

        # 파일 타입 검증
        logger.info("파일 타입 검증 중...")
        try:
            is_result = ClassAssigner.is_result_file(file_path)
            logger.info(f"배정 결과 파일 여부: {is_result}")
            
            if not is_result:
                logger.warning("배정 결과 파일이 아님")
                QMessageBox.warning(
                    self,
                    "오류",
                    "배정 결과 파일이 아닙니다.\n'새로 시작'을 선택하세요."
                )
                return
        except Exception as e:
            logger.error("파일 타입 검증 중 오류 발생", exc_info=True)
            QMessageBox.critical(
                self,
                "오류",
                f"파일 검증 중 오류가 발생했습니다:\n\n{str(e)}"
            )
            return

        # OverviewGUI 실행 (전체 학생 보기 → 반 선택 → 수동 조정)
        try:
            logger.info("Initializing OverviewGUI...")
            self.overview_gui = OverviewGUI(file_path)
            self.overview_gui.show()
            self.close()
            logger.info("OverviewGUI 생성 및 표시 완료")
        except Exception as e:
            logger.error(f"Failed to load OverviewGUI: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "오류",
                f"파일 로드 중 오류가 발생했습니다:\n\n{str(e)}"
            )
            return


class AssignmentThread(QThread):
    """학급 편성을 백그라운드에서 실행하는 스레드"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)  # success, message

    def __init__(self, student_file, rules_file, output_file, target_class_count, special_student_weight=3.0):
        super().__init__()
        self.student_file = student_file
        self.rules_file = rules_file
        self.output_file = output_file
        self.target_class_count = target_class_count
        self.special_student_weight = special_student_weight

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
                    target_class_count=self.target_class_count,
                    special_student_weight=self.special_student_weight
                )
                success, message = assigner.run(output_file=self.output_file)

            # 캡처된 출력을 GUI에 표시
            captured_output = output_buffer.getvalue()
            for line in captured_output.split('\n'):
                if line.strip():
                    self.log_signal.emit(line)

            self.log_signal.emit("")
            self.log_signal.emit("=" * 70)
            
            if success:
                self.log_signal.emit(f"✅ 완료! 결과 파일이 생성되었습니다:")
                self.log_signal.emit(f"📁 {self.output_file}")
                self.log_signal.emit("=" * 70)

                self.finished_signal.emit(
                    True,
                    f"학급 편성이 완료되었습니다!\n\n결과 파일:\n{self.output_file}"
                )
            else:
                self.log_signal.emit(f"❌ 실패! 오류가 발생했습니다:")
                self.log_signal.emit(f"메시지: {message}")
                self.log_signal.emit("=" * 70)
                
                self.finished_signal.emit(
                    False,
                    f"학급 편성 중 오류가 발생했습니다:\n\n{message}"
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



class StatusDelegate(QStyledItemDelegate):
    """Delegate to render status circles and text in the same column"""
    def paint(self, painter, option, index):
        # 1. Setup
        painter.save()
        
        # Draw background (handling selection)
        style = option.widget.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)
        
        # Get data
        colors = index.data(Qt.ItemDataRole.UserRole)
        text = index.data(Qt.ItemDataRole.DisplayRole)
        
        # Layout metrics
        rect = option.rect
        icon_size = 14
        spacing = 4
        x = rect.left() + spacing
        y = rect.top() + (rect.height() - icon_size) // 2

        # 2. Draw Circles
        if colors and isinstance(colors, list):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            for color_code in colors:
                painter.setBrush(QColor(color_code))
                painter.drawEllipse(x, y, icon_size, icon_size)
                x += icon_size + 2 # 2px gap between circles
            
            x += spacing # Gap before text

        # 3. Draw Text
        if text:
            # Handle Text Color (White if selected)
            if option.state & QStyle.StateFlag.State_Selected:
                painter.setPen(option.palette.highlightedText().color())
            else:
                painter.setPen(option.palette.text().color())
                
            text_rect = rect.adjusted(x - rect.left(), 0, 0, 0)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
            
        painter.restore()

class ModernTableDelegate(QStyledItemDelegate):
    """
    시스템 테마를 따르는 테이블 Delegate
    Handles badges in Column 5 and general styling
    """
    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 32)  # Height 32px

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Background (Selection / Hover) - 시스템 팔레트 사용
        rect = option.rect

        if option.state & QStyle.StateFlag.State_Selected:
            bg_color = option.palette.highlight().color()
            text_color = option.palette.highlightedText().color()
        elif option.state & QStyle.StateFlag.State_MouseOver:
            # 호버: Base 색상을 약간 조정
            base = option.palette.base().color()
            if base.lightness() > 128:
                bg_color = base.darker(110)
            else:
                bg_color = base.lighter(120)
            text_color = option.palette.text().color()
        else:
            bg_color = option.palette.base().color()
            text_color = option.palette.text().color()

        # Draw Background
        painter.fillRect(rect, bg_color)

        # Draw Border (Bottom Line) - Use Mid/MidLight color
        painter.setPen(option.palette.midlight().color())
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        # 2. Content Drawing by Column
        col = index.column()
        # Data
        text = index.data(Qt.ItemDataRole.DisplayRole)
        
        # Text Rect
        text_rect = rect.adjusted(5, 0, -5, 0)
        
        painter.setPen(text_color)
        
        # Column Specific Rendering
        if col == 5: # Info Column (Badges)
            badges = index.data(Qt.ItemDataRole.UserRole + 1)
            if badges:
                badge_x = rect.left() + 5
                badge_y = rect.center().y()
                
                font = painter.font()
                font.setPointSize(11) # Increased from 9
                painter.setFont(font)

                for b_text, bg_c, txt_c in badges:
                    fm = painter.fontMetrics()
                    b_w = fm.horizontalAdvance(b_text) + 16 # Slightly more padding
                    b_h = 24 # Increased from 18
                    
                    b_rect = QRect(badge_x, badge_y - b_h//2, b_w, b_h)
                    
                    # Draw Badge
                    painter.setBrush(QColor(bg_c))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRoundedRect(b_rect, 4, 4)
                    
                    painter.setPen(QColor(txt_c))
                    painter.drawText(b_rect, Qt.AlignmentFlag.AlignCenter, b_text)
                    
                    badge_x += b_w + 5
            else:
                # Fallback text if no badges but text exists (shouldn't happen with new logic)
                pass 
                
        elif col == 2: # Gender
             # Center Align
             painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(text))
        elif col == 3 or col == 4: # Score, Difficulty
             # Center Align
             painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(text))
        else: # Name, Number
             painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, str(text))

        painter.restore()

class StudentTreeWidget(QTreeWidget):
    """Drag & Drop을 지원하는 현대적인 테이블 리스트 위젯"""
    item_dropped = pyqtSignal(object, object, int)  # source, target, index
    order_changed = pyqtSignal(int, list) # class_id, new_student_list

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Multi-Column Mode
        self.setColumnCount(6)
        self.setHeaderLabels(["번호", "이름", "성별", "점수", "난이도", "정보"])
        self.setHeaderHidden(False) 
        self.setIndentation(0)     
        self.setRootIsDecorated(False)
        self.setSortingEnabled(False) # Disable Auto-Sorting for Manual Ordering
        
        # Modern Table Delegate 적용
        self.setItemDelegate(ModernTableDelegate(self))

        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        
        self.setMouseTracking(True)

        # 시스템 테마를 따르는 최소한의 스타일 (배경/텍스트 색상은 시스템 팔레트 사용)
        self.setStyleSheet("""
            QTreeWidget {
                border: 1px solid palette(mid);
            }
            QHeaderView::section {
                padding: 4px;
                border: none;
                border-bottom: 1px solid palette(mid);
                font-weight: bold;
            }
        """)
        
        # Column Widths
        self.setColumnWidth(0, 50)  # No
        self.setColumnWidth(1, 100) # Name
        self.setColumnWidth(2, 50)  # Gender
        self.setColumnWidth(3, 60)  # Score
        self.setColumnWidth(4, 60)  # Diff
        # Info takes rest
        
        self.class_id = None

    def dropEvent(self, event):
        """Handle internal reordering and external drops"""
        source = event.source()
        drop_pos = event.position().toPoint()
        target_item = self.itemAt(drop_pos)
        indicator = self.dropIndicatorPosition()

        # OnItem일 때는 드롭 무시 (명확한 위치 지정 필요)
        if target_item and indicator == QAbstractItemView.DropIndicatorPosition.OnItem:
            logger.debug("OnItem: Drop ignored - require clear position (Above/Below)")
            event.ignore()
            return

        # 1. Internal Reorder
        if source == self:
            # Use default implementation to move visual items
            super().dropEvent(event)
            self.sync_order()
            return

        # 2. External Drop (from another class)
        drop_index = -1

        logger.debug(f"Drop Event at {drop_pos}, Target Item: {target_item is not None}")

        if target_item:
            drop_index = self.indexOfTopLevelItem(target_item)

            logger.debug(f"  - Initial Index: {drop_index}")
            logger.debug(f"  - Indicator: {indicator}")

            if indicator == QAbstractItemView.DropIndicatorPosition.BelowItem:
                drop_index += 1
                logger.debug("  - Adjusted Index (+1) due to BelowItem")
            elif indicator == QAbstractItemView.DropIndicatorPosition.AboveItem:
                logger.debug("  - AboveItem: Keeping index")

        else:
             # Dropped on empty space
             logger.debug("  - Dropped on empty space")
             if self.topLevelItemCount() > 0:
                 last_item = self.topLevelItem(self.topLevelItemCount() - 1)
                 last_rect = self.visualItemRect(last_item)
                 logger.debug(f"  - Last Item Rect: {last_rect}, Drop Y: {drop_pos.y()}")

                 if drop_pos.y() > last_rect.y() + last_rect.height():
                     drop_index = self.topLevelItemCount()
                     logger.debug("  - Appending to end (below last item)")
                 else:
                     drop_index = self.topLevelItemCount()
                     logger.debug("  - Defaulting to end")
             else:
                 drop_index = 0
                 logger.debug("  - Empty list, inserting at 0")

        logger.debug(f"Final Drop Index emitted: {drop_index}")
        self.item_dropped.emit(source, self, drop_index)
        event.ignore() 
        
    def sync_order(self):
        """Syncs the internal Student list order with the current TreeWidget order"""
        if self.class_id is None: return
        
        new_order = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            
            # Update the displayed Number (Column 0) to match new index (i + 1)
            # This ensures the "No." column reflects the new visual order immediately
            item.setData(0, Qt.ItemDataRole.DisplayRole, i + 1)
            
            student = item.data(0, Qt.ItemDataRole.UserRole)
            if student:
                new_order.append(student)
        
        self.order_changed.emit(self.class_id, new_order)


class ClassPanel(QWidget):
    """
    개별 반 관리를 위한 패널 (Card Style)
    Enhanced Modern Dark Mode: Shadow + ComboBox
    """
    class_selected = pyqtSignal(int)
    student_dropped = pyqtSignal(object, object, int) # source, target, index
    order_changed = pyqtSignal(int, list)

    def __init__(self, title, assigner, parent=None):
        super().__init__(parent)
        self.assigner = assigner
        self.current_class_id = None
        self.title = title
        self.init_ui()
        
        # Add Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80)) # 30% Black
        self.setGraphicsEffect(shadow)

    def init_ui(self):
        # Card Main Layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # 시스템 테마를 따르는 카드 스타일
        self.setObjectName("ClassPanel")
        self.setStyleSheet("""
            QWidget#ClassPanel {
                border-radius: 12px;
                border: 1px solid palette(mid);
            }
        """)

        # 1. Header Area (Class Selector + Stats)
        header_layout = QHBoxLayout()
        
        # 1.1 Class Selector (Title)
        self.class_combo = QComboBox()
        self.class_combo.setMinimumWidth(100)
        self.class_combo.setFont(QFont("", 14, QFont.Weight.Bold))
        # 시스템 테마를 따르는 콤보박스 스타일
        self.class_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 1px solid palette(highlight);
            }
        """)
        
        # Populate Combo
        self.class_combo.addItem(self.title, None) # Placeholder or "Select Class"
        for i in range(1, self.assigner.target_class_count + 1):
            self.class_combo.addItem(f"{i}반", i)
            
        self.class_combo.currentIndexChanged.connect(self.on_class_combo_changed)
        header_layout.addWidget(self.class_combo)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)

        # 2. Stats Line (Inline)
        self.stats_label = QLabel("반을 선택해주세요")
        self.stats_label.setFont(QFont("", 12)) # Increased from 10
        # 시스템 팔레트 사용 (별도 색상 지정 없음)
        layout.addWidget(self.stats_label)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setFixedHeight(1)
        layout.addWidget(line)

        # 3. Student List
        self.student_list = StudentTreeWidget()
        self.student_list.item_dropped.connect(self.student_dropped.emit) # Pass through to parent
        self.student_list.order_changed.connect(self.order_changed.emit) # Pass through to parent
        
        # 스크롤바는 시스템 기본 스타일 사용
        
        layout.addWidget(self.student_list)

        self.setLayout(layout)

    def on_class_combo_changed(self, index):
        class_id = self.class_combo.currentData()
        self.set_current_class(class_id)
        if class_id is not None:
            self.class_selected.emit(class_id)

    def set_current_class(self, class_id):
        self.current_class_id = class_id
        self.student_list.class_id = class_id
        
        # Sync Combo if set externally
        if class_id is None:
            self.class_combo.setCurrentIndex(0)
        else:
            # Find index
            idx = self.class_combo.findData(class_id)
            if idx >= 0 and self.class_combo.currentIndex() != idx:
                self.class_combo.setCurrentIndex(idx)
              
        self.refresh_data()

    def refresh_data(self):
        """데이터(학생 목록, 통계) 새로고침"""
        # 0. Always Update Combo Stats (for all classes)
        self.update_combo_stats()

        if self.current_class_id is None:
            self.student_list.clear()
            self.stats_label.setText("반을 선택해주세요")
            return

        # 1. 학생 목록 Refresh
        self.student_list.clear() # TreeWidget Clear
        if self.current_class_id in self.assigner.classes:
            students = self.assigner.classes[self.current_class_id]
            # Use the list AS IS (Trusting manual order or initial sort)
            # sorted_students = sorted(students, key=lambda s: (1 if s.전출 else 0, s.이름)) 
            
            for idx, student in enumerate(students, 1):
                item = QTreeWidgetItem(self.student_list)
                
                # Column 0: Number (Sortable)
                item.setData(0, Qt.ItemDataRole.DisplayRole, idx) 
                
                # Column 1: Name
                item.setText(1, student.이름)
                
                # Column 2: Gender
                item.setText(2, student.성별)
                
                # Column 3: Score (Display as Int, Sort as Number)
                item.setData(3, Qt.ItemDataRole.DisplayRole, int(student.점수) if student.점수 else 0)
                
                # Column 4: Difficulty
                diff = student.난이도
                item.setText(4, str(int(diff)) if diff and float(diff) != 0.0 else "")

                # Store Student Object in UserRole (Accessible from all cols ideally, but root item is enough)
                item.setData(0, Qt.ItemDataRole.UserRole, student) 
                
                # Calculate Extra Badges (Rules) for Column 5
                badges = []
                
                # 1. 분반 규칙 Check (Separation)
                if student.이름 in self.assigner.separation_rules:
                     partners = self.assigner.separation_rules[student.이름]
                     # Format: "3반 홍길동"
                     p_texts = []
                     for p in partners:
                         c_id = self._find_student_class_id(p)
                         class_str = f"{c_id}반" if c_id else "미배정"
                         p_texts.append(f"{class_str} {p}")
                     
                     partner_str = ",".join(p_texts)
                     badges.append((f"🚫 {partner_str}", "#F57F17", "#FFF9C4")) # Dark Yellow Bg
                
                # 2. 합반 규칙 Check (Together)
                is_together = False
                partners = set()
                
                # Normalize name for robust checking
                s_name_nfc = unicodedata.normalize('NFC', student.이름.strip())

                for group in self.assigner.together_groups:
                    # Check both raw and normalized name
                    if student.이름 in group or s_name_nfc in group:
                        is_together = True
                        # Remove both forms to be safe
                        partners = group - {student.이름, s_name_nfc}
                        break
                
                if is_together:
                    p_texts = []
                    for p in partners:
                         # Normalize partner name for lookup
                         p_clean = unicodedata.normalize('NFC', p.strip())
                         c_id = self._find_student_class_id(p_clean)
                         class_str = f"{c_id}반" if c_id else "미배정"
                         p_texts.append(f"{class_str} {p}")

                    partner_str = ",".join(p_texts) if p_texts else ""
                    badges.append((f"🤝 {partner_str}", "#1565C0", "#E3F2FD")) # Dark Blue Bg

                # Badges for Transfer/Special
                if student.전출:
                    badges.insert(0, ("전출", "#424242", "#BDBDBD"))
                if student.특수반:
                    badges.insert(0, ("특수", "#4A148C", "#E1BEE7"))
                    
                # Store Badges in UserRole + 1 of Column 5 (Info) (AND Column 0 just in case)
                item.setData(5, Qt.ItemDataRole.UserRole + 1, badges)
                # item.setData(5, Qt.ItemDataRole.DisplayRole, "") # No text, just badges
        
        # 2. 통계 Refresh (Current View)
        self.update_statistics()

        # 3. Default Sort: REMOVED to support manual reordering
        # self.student_list.sortItems(0, Qt.SortOrder.AscendingOrder)

    def _find_student_class_id(self, name):
        """이름으로 학생의 현재 반 번호 찾기 (Unicode Normalization 적용)"""
        if not name: return None
        target_name = unicodedata.normalize('NFC', name.strip())
        
        for c_id, students in self.assigner.classes.items():
            for s in students:
                s_name_clean = unicodedata.normalize('NFC', s.이름.strip())
                if s_name_clean == target_name:
                    return c_id
        
        return None

    def update_combo_stats(self):
        """콤보박스 아이템들의 텍스트를 최신 통계로 업데이트"""
        for i in range(self.class_combo.count()):
            class_id = self.class_combo.itemData(i)
            if class_id is None: continue # Skip placeholder
            
            if class_id in self.assigner.classes:
                students = self.assigner.classes[class_id]
                total = len(students)
                effective = self.assigner._get_effective_count(class_id)
                male = sum(1 for s in students if s.성별 == '남')
                female = sum(1 for s in students if s.성별 == '여')
                
                # Format: "1반 - 22 (유효 21) | 남 10 여 12"
                new_text = f"{class_id}반 - {total}명 (유효 {int(effective)}) | 남 {male} 여 {female}"
                self.class_combo.setItemText(i, new_text)

    def update_statistics(self):
        if self.current_class_id not in self.assigner.classes:
            return

        students = self.assigner.classes[self.current_class_id]
        
        special_count = sum(1 for s in students if s.특수반)
        transfer_count = sum(1 for s in students if s.전출)
        difficulty_sum = sum(s.난이도 for s in students)
        
        # 성적 평균 계산
        scores = [float(s.점수) for s in students if s.점수]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Update: Show Special, Transfer, Difficulty Sum, and Score Average
        stats_text = (
            f"특수 {special_count}  ·  전출 {transfer_count}  |  "
            f"난이도합 {int(difficulty_sum)}  ·  평균 {avg_score:.1f}"
        )
        self.stats_label.setText(stats_text)

    def on_drop_event(self, source, target):
        self.student_dropped.emit(source, target)

    # Helper methods copied/adapted from old InteractiveEditorGUI
    def _get_student_icon(self, student):
        if student.전출: return "🛫"
        elif student.특수반: return "🔴"
        elif student.이름 in self.assigner.separation_rules: return "🟡"
        elif self._is_in_together_group(student): return "🔵"
        else: return "⚪"

    def _is_in_together_group(self, student):
        for group in self.assigner.together_groups:
            if student.이름 in group: return True
        return False
        
    def _find_student_by_name(self, name): # Helper if needed
        for student in self.assigner.students:
            if student.이름 == name: return student
        return None
        
    def _get_together_group(self, student):
        for group in self.assigner.together_groups:
            if student.이름 in group: return group
        return None

    def get_constraint_info(self, student):
        # ... Reuse logic ...
        # Can we move this to a shared helper or keep duplicate? 
        # For now duplicate to keep it self-contained in ClassPanel or 
        # better: use Assigner if possible. But Assigner doesn't have UI string logic.
        # Let's clean copy.
        parts = []
        # 1. 분반
        if student.이름 in self.assigner.separation_rules:
            targets = self.assigner.separation_rules[student.이름]
            target_info = []
            for target_name in targets:
                # Find target's class
                 # Low performace but okay for GUI
                found = False
                for s in self.assigner.students: # Or use map if available
                    if s.이름 == target_name:
                         if s.assigned_class:
                             target_info.append(f"{target_name}({s.assigned_class}반)")
                         else:
                             target_info.append(target_name)
                         found = True
                         break
                if not found: target_info.append(target_name)

            if target_info: parts.append(f"분반: {', '.join(target_info)}")

        # 2. 합반
        together_group = self._get_together_group(student)
        if together_group:
            others = [name for name in together_group if name != student.이름]
            if others: parts.append(f"합반: {', '.join(others)}")

        return " - " + " | ".join(parts) if parts else ""


class ClassAssignerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("ClassAssignerGUI Initialized")

        # 파일 경로 저장
        self.student_file_path = None
        self.rules_file_path = None
        self.assignment_thread = None

        # UI 구성
        self.init_ui()
        setup_help_menu(self)  # 공통 도움말 메뉴

        # 기본 파일 경로 설정
        self.load_default_files()

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(f"🎓 자동 학급 편성 프로그램 - {VERSION}")
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
        
        # Version footer
        version_label = QLabel(f"Version: {VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666666; font-size: 10px; margin-top: 5px;")
        main_layout.addWidget(version_label)

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

        # 간격
        layout.addSpacing(10)

        # 특수반 학생 가중치 입력
        weight_label = QLabel("특수반 학생 가중치):")
        weight_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(weight_label)
        
        weight_layout = QHBoxLayout()
        self.weight_spin = QSpinBox()
        self.weight_spin.setRange(1, 10)
        self.weight_spin.setValue(3)      # 기본값 3
        self.weight_spin.setMinimumHeight(35)
        self.weight_spin.setFont(QFont("", 11))
        self.weight_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
            }
        """)
        
        weight_desc = QLabel(" 명")
        weight_desc.setFont(QFont("", 11))
        
        weight_layout.addWidget(self.weight_spin)
        weight_layout.addWidget(weight_desc)
        weight_layout.addStretch(1)
        
        layout.addLayout(weight_layout)

        return widget

    def load_default_files(self):
        """기본 파일 경로 로드"""
        logger.info("Loading default files...")
        base_dir = os.getcwd()
        default_student = os.path.join(base_dir, "01 가상 명단.xlsx")
        default_rules = os.path.join(base_dir, "02 분반 합반할 학생 규칙.xlsx")

        if os.path.exists(default_student):
            self.student_file_path = default_student
            self.update_file_label(self.student_file_label, default_student)
            logger.info(f"Default student file loaded: {default_student}")
        else:
            logger.warning(f"Default student file not found: {default_student}")

        if os.path.exists(default_rules):
            self.rules_file_path = default_rules
            self.update_file_label(self.rules_file_label, default_rules)
            logger.info(f"Default rules file loaded: {default_rules}")
        else:
            logger.warning(f"Default rules file not found: {default_rules}")

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
        logger.info("Selecting student file...")
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
            logger.info(f"Student file selected: {filename}")
        else:
            logger.info("Student file selection cancelled.")

    def select_rules_file(self):
        """분반/합반 규칙 파일 선택"""
        logger.info("Selecting rules file...")
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
            logger.info(f"Rules file selected: {filename}")
        else:
            logger.info("Rules file selection cancelled.")

    def log_message(self, message):
        """진행 상황 로그 추가"""
        self.progress_text.append(message)

    def clear_log(self):
        """로그 초기화"""
        self.progress_text.clear()

    def execute_assignment(self):
        """학급 편성 실행"""
        logger.info("Execute Assignment button clicked.")
        # 파일 경로 확인
        if not self.student_file_path or not os.path.exists(self.student_file_path):
            QMessageBox.critical(self, "오류", "학생 명단 파일을 선택해주세요.")
            logger.warning("Student file not selected or does not exist.")
            return

        if not self.rules_file_path or not os.path.exists(self.rules_file_path):
            QMessageBox.critical(self, "오류", "분반/합반 규칙 파일을 선택해주세요.")
            logger.warning("Rules file not selected or does not exist.")
            return

        # 출력 파일 경로
        output_dir = os.path.dirname(self.student_file_path)
        output_file = os.path.join(output_dir, '03 배정 결과.xlsx')
        logger.info(f"Output file path set to: {output_file}")

        # UI 비활성화
        self.execute_btn.setEnabled(False)
        self.clear_log()

        # 백그라운드 스레드 생성 및 실행
        target_count = self.class_count_spin.value()
        special_weight = self.weight_spin.value()
        logger.info(f"Starting assignment with target_class_count={target_count}, special_student_weight={special_weight}")
        
        self.assignment_thread = AssignmentThread(
            self.student_file_path,
            self.rules_file_path,
            output_file,
            target_count,
            special_weight
        )
        self.assignment_thread.log_signal.connect(self.log_message)
        self.assignment_thread.finished_signal.connect(self.on_assignment_finished)
        self.assignment_thread.start()
        logger.info("Assignment thread started.")

    def on_assignment_finished(self, success, message):
        """학급 편성 완료 처리"""
        logger.info(f"Assignment finished. Success: {success}, Message: {message}")
        # UI 다시 활성화
        self.execute_btn.setEnabled(True)

        # 결과 메시지 표시
        if success:
            # 완료 후 전체 보기 화면으로 이동할지 물어보기
            reply = QMessageBox.question(
                self,
                "완료",
                f"{message}\n\n전체 학생 보기 화면으로 이동하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                logger.info("User chose to move to OverviewGUI.")
                # OverviewGUI로 전환
                output_file = os.path.join(
                    os.path.dirname(self.student_file_path),
                    '03 배정 결과.xlsx'
                )
                try:
                    self.overview_gui = OverviewGUI(output_file)
                    self.overview_gui.show()
                    self.close()
                    logger.info("OverviewGUI launched successfully.")
                except Exception as e:
                    logger.error(f"Failed to launch OverviewGUI after assignment: {e}", exc_info=True)
                    QMessageBox.critical(
                        self,
                        "오류",
                        f"전체 보기 화면 로드 중 오류가 발생했습니다:\n\n{str(e)}"
                    )
            else:
                logger.info("User chose not to move to OverviewGUI.")
        else:
            logger.error(f"Assignment failed: {message}")
            QMessageBox.critical(self, "오류", message)


class CompactStudentCard(QFrame):
    """축소 학생 카드 (칸반 보드용) - 드래그 지원"""
    clicked = pyqtSignal(object)  # student object

    def __init__(self, student, assigner, class_id, parent=None):
        super().__init__(parent)
        self.student = student
        self.assigner = assigner
        self.class_id = class_id  # 현재 소속 반
        self.setFixedHeight(28)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.drag_start_pos = None
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        # 상태 아이콘 (색상 원)
        icon_label = QLabel()
        color = self._get_status_color()
        icon_label.setPixmap(create_circle_icon(color, 12).pixmap(12, 12))
        layout.addWidget(icon_label)

        # 이름
        name_label = QLabel(self.student.이름)
        name_label.setFont(QFont("", 10))
        layout.addWidget(name_label)

        # 성별
        gender_label = QLabel(self.student.성별)
        gender_label.setFont(QFont("", 9))
        layout.addWidget(gender_label)
        
        # 난이도 (0이 아닌 경우만 표시)
        if self.student.난이도 and float(self.student.난이도) != 0.0:
            diff_label = QLabel(f"난{int(self.student.난이도)}")
            diff_label.setFont(QFont("", 9))
            layout.addWidget(diff_label)

        layout.addStretch()
        self.setLayout(layout)

        # 스타일
        self.setStyleSheet("""
            CompactStudentCard {
                border: 1px solid palette(mid);
                border-radius: 4px;
                background-color: palette(base);
            }
            CompactStudentCard:hover {
                border: 1px solid palette(highlight);
                background-color: palette(alternateBase);
            }
        """)
        
        # 툴팁 설정 (합반/분반 정보)
        self._set_tooltip()

    def _get_status_color(self):
        """학생 상태에 따른 색상 반환"""
        if self.student.특수반:
            return "#9C27B0"  # 보라
        elif self.student.전출:
            return "#9E9E9E"  # 회색
        elif self.student.이름 in self.assigner.separation_rules:
            return "#FFD700"  # 노랑 (분반)
        else:
            # 합반 체크
            for group in self.assigner.together_groups:
                if self.student.이름 in group:
                    return "#2196F3"  # 파랑 (합반)
        return "#FFFFFF"  # 흰색 (일반)
    
    def _set_tooltip(self):
        """합반/분반/특수반/전출 정보를 툴팁으로 표시"""
        # 분반/합반/특수반/전출이 아닌 일반 학생은 툴팁 없음
        has_separation = self.student.이름 in self.assigner.separation_rules
        has_together = any(self.student.이름 in group for group in self.assigner.together_groups)
        
        if not (self.student.특수반 or self.student.전출 or has_separation or has_together):
            # 일반 학생은 툴팁 없음
            return
        
        tooltip_parts = []
        
        # 기본 정보
        basic_info = f"{self.student.이름} ({self.student.성별})"
        if self.student.특수반:
            basic_info += " - 특수반"
        if self.student.전출:
            basic_info += " - 전출"
        tooltip_parts.append(basic_info)
        
        # 분반 규칙 확인
        if has_separation:
            partners = self.assigner.separation_rules[self.student.이름]
            partner_infos = []
            for partner_name in partners:
                # 파트너의 반 찾기
                partner_class = self._find_student_class(partner_name)
                if partner_class:
                    partner_infos.append(f"{partner_class}반 {partner_name}")
                else:
                    partner_infos.append(f"미배정 {partner_name}")
            
            if partner_infos:
                tooltip_parts.append(f"🚫 분반 대상: {', '.join(partner_infos)}")
        
        # 합반 규칙 확인
        if has_together:
            for group in self.assigner.together_groups:
                if self.student.이름 in group:
                    partners = group - {self.student.이름}
                    partner_infos = []
                    for partner_name in partners:
                        # 파트너의 반 찾기
                        partner_class = self._find_student_class(partner_name)
                        if partner_class:
                            partner_infos.append(f"{partner_class}반 {partner_name}")
                        else:
                            partner_infos.append(f"미배정 {partner_name}")
                    
                    if partner_infos:
                        tooltip_parts.append(f"🤝 합반 대상: {', '.join(partner_infos)}")
                    break
        
        # 툴팁 설정 (항상 표시, 이미 필터링됨)
        self.setToolTip("\n".join(tooltip_parts))
    
    def _find_student_class(self, student_name):
        """학생 이름으로 반 번호 찾기"""
        import unicodedata
        target_name = unicodedata.normalize('NFC', student_name.strip())
        
        for class_id, students in self.assigner.classes.items():
            for s in students:
                s_name_clean = unicodedata.normalize('NFC', s.이름.strip())
                if s_name_clean == target_name:
                    return class_id
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        self.clicked.emit(self.student)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if self.drag_start_pos is None:
            return
        # 드래그 시작 거리 체크
        if (event.pos() - self.drag_start_pos).manhattanLength() < 10:
            return

        # 드래그 시작
        drag = QDrag(self)
        mime_data = QMimeData()
        # 학생 정보를 MIME 데이터로 전달
        mime_data.setText(f"{self.class_id}:{self.student.이름}")
        mime_data.setData("application/x-student",
                         f"{self.class_id}:{id(self.student)}".encode())
        drag.setMimeData(mime_data)

        # 드래그 시 표시할 픽스맵
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        drag.exec(Qt.DropAction.MoveAction)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.drag_start_pos = None


class ClassColumn(QFrame):
    """칸반 스타일 반 컬럼 - 드롭 수신 지원"""
    class_clicked = pyqtSignal(int)  # class_id
    student_moved = pyqtSignal(int, int, object, int)  # from_class, to_class, student, insert_index

    def __init__(self, class_id, assigner, parent=None):
        super().__init__(parent)
        self.class_id = class_id
        self.assigner = assigner
        self.is_selected = False
        self.drop_indicator_index = -1  # 드롭 위치 표시용
        self.setAcceptDrops(True)  # 드롭 수신 활성화
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # 헤더 (클릭 가능)
        self.header = QPushButton()
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.clicked.connect(lambda: self.class_clicked.emit(self.class_id))
        self.update_header()
        layout.addWidget(self.header)

        # 학생 목록 (스크롤 가능)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self.student_container = QWidget()
        self.student_layout = QVBoxLayout()
        self.student_layout.setContentsMargins(0, 0, 0, 0)
        self.student_layout.setSpacing(2)
        self.student_layout.addStretch()
        self.student_container.setLayout(self.student_layout)

        scroll.setWidget(self.student_container)
        layout.addWidget(scroll)

        self.setLayout(layout)
        self.update_style()
        self.refresh_students()

    def update_header(self):
        """헤더 텍스트 업데이트"""
        students = self.assigner.classes.get(self.class_id, [])
        total = len(students)
        male = sum(1 for s in students if s.성별 == '남')
        female = sum(1 for s in students if s.성별 == '여')
        
        # 난이도 합계 계산
        total_difficulty = sum(float(s.난이도) if s.난이도 else 0 for s in students)
        
        # 성적 평균 계산
        scores = [float(s.점수) for s in students if s.점수]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # 헤더 텍스트 구성
        header_text = f"{self.class_id}반 ({total}명)\n"
        header_text += f"남{male} 여{female}\n"
        header_text += f"난이도합:{int(total_difficulty)}\n"
        header_text += f"학업평균:{avg_score:.1f}"
        
        self.header.setText(header_text)
        self.header.setFont(QFont("", 11, QFont.Weight.Bold))

    def update_style(self):
        """선택 상태에 따른 스타일 업데이트"""
        if self.is_selected:
            self.setStyleSheet("""
                ClassColumn {
                    border: 2px solid palette(highlight);
                    border-radius: 8px;
                    background-color: palette(base);
                }
            """)
            self.header.setStyleSheet("""
                QPushButton {
                    background-color: palette(highlight);
                    color: palette(highlightedText);
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                ClassColumn {
                    border: 1px solid palette(mid);
                    border-radius: 8px;
                    background-color: palette(base);
                }
            """)
            self.header.setStyleSheet("""
                QPushButton {
                    background-color: palette(button);
                    border: 1px solid palette(mid);
                    border-radius: 4px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: palette(midlight);
                }
            """)

    def set_selected(self, selected):
        """선택 상태 설정"""
        self.is_selected = selected
        self.update_style()

    def refresh_students(self):
        """학생 카드 새로고침"""
        # 기존 카드 제거
        while self.student_layout.count() > 1:  # stretch 제외
            item = self.student_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 학생 카드 추가 (class_id 전달)
        students = self.assigner.classes.get(self.class_id, [])
        for student in students:
            card = CompactStudentCard(student, self.assigner, self.class_id)
            self.student_layout.insertWidget(self.student_layout.count() - 1, card)

        self.update_header()

    def dragEnterEvent(self, event):
        """드래그 진입 이벤트"""
        if event.mimeData().hasFormat("application/x-student"):
            data = event.mimeData().data("application/x-student").data().decode()
            from_class = int(data.split(":")[0])
            
            # 같은 반이든 다른 반이든 모두 허용
            event.acceptProposedAction()
            
            if from_class != self.class_id:
                # 다른 반에서 온 경우: 강조 표시
                self.setStyleSheet("""
                    ClassColumn {
                        border: 2px dashed palette(highlight);
                        border-radius: 8px;
                        background-color: palette(alternateBase);
                    }
                """)
            # 같은 반 내에서의 이동은 기본 스타일 유지
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """드래그 이동 이벤트 - 삽입 위치 계산 및 표시"""
        if not event.mimeData().hasFormat("application/x-student"):
            event.ignore()
            return

        # 같은 반이든 다른 반이든 모두 허용
        event.acceptProposedAction()

        # 드롭 위치 계산 (student_container 내 좌표로 변환)
        pos = self.student_container.mapFrom(self, event.position().toPoint())
        new_index = self._calc_drop_index(pos)

        # 인디케이터 업데이트
        if new_index != self.drop_indicator_index:
            self.drop_indicator_index = new_index
            self._update_drop_indicator()

    def _calc_drop_index(self, pos):
        """드롭 위치에 해당하는 인덱스 계산"""
        y = pos.y()
        # student_layout에서 학생 카드 위젯들만 순회 (마지막 stretch 제외)
        card_count = self.student_layout.count() - 1  # stretch 제외

        for i in range(card_count):
            item = self.student_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                widget_y = widget.y()
                widget_height = widget.height()
                # 카드의 중간점을 기준으로 위/아래 판단
                if y < widget_y + widget_height / 2:
                    return i
        return card_count  # 마지막 위치

    def _update_drop_indicator(self):
        """드롭 위치 인디케이터 업데이트"""
        card_count = self.student_layout.count() - 1  # stretch 제외

        for i in range(card_count):
            item = self.student_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if i == self.drop_indicator_index:
                    # 삽입 위치 위의 카드에 상단 보더 표시
                    widget.setStyleSheet(widget.styleSheet() +
                        "border-top: 3px solid palette(highlight);")
                else:
                    # 기존 스타일 복원 (border-top 제거)
                    style = widget.styleSheet()
                    if "border-top: 3px solid" in style:
                        widget.setStyleSheet(style.replace(
                            "border-top: 3px solid palette(highlight);", ""))

    def _clear_drop_indicator(self):
        """드롭 인디케이터 제거"""
        card_count = self.student_layout.count() - 1
        for i in range(card_count):
            item = self.student_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                style = widget.styleSheet()
                if "border-top: 3px solid" in style:
                    widget.setStyleSheet(style.replace(
                        "border-top: 3px solid palette(highlight);", ""))
        self.drop_indicator_index = -1

    def dragLeaveEvent(self, event):
        """드래그 이탈 이벤트"""
        self._clear_drop_indicator()
        self.update_style()  # 원래 스타일로 복원

    def dropEvent(self, event):
        """드롭 이벤트"""
        insert_index = self.drop_indicator_index if self.drop_indicator_index >= 0 else -1
        self._clear_drop_indicator()

        if event.mimeData().hasFormat("application/x-student"):
            data = event.mimeData().data("application/x-student").data().decode()
            from_class, student_id = data.split(":")
            from_class = int(from_class)
            student_id = int(student_id)

            # 학생 객체 찾기
            student = None
            for s in self.assigner.classes.get(from_class, []):
                if id(s) == student_id:
                    student = s
                    break

            if student:
                # 시그널 발송 (OverviewGUI에서 처리)
                # from_class == self.class_id인 경우 순서 변경, 다른 경우 반 이동
                self.student_moved.emit(from_class, self.class_id, student, insert_index)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

        self.update_style()  # 스타일 복원


class OverviewGUI(QMainWindow):
    """전체 학생 보기 화면 (Bird's Eye View)"""

    def __init__(self, result_file: str, assigner: ClassAssigner = None):
        super().__init__()
        logger.info("=" * 70)
        logger.info("OverviewGUI 초기화 시작")
        logger.info(f"결과 파일: {result_file}")
        logger.info(f"Assigner 객체 전달됨: {assigner is not None}")

        self.result_file = result_file
        self.selected_classes = []  # 최대 2개

        # Assigner 로드
        try:
            if assigner is not None:
                # 외부에서 assigner 객체를 전달받은 경우
                logger.info("전달받은 ClassAssigner 객체 사용")
                self.assigner = assigner
            else:
                # 파일에서 새로 로드하는 경우
                self.assigner = ClassAssigner(
                    student_file="",
                    rules_file="",
                    target_class_count=7
                )
                self.assigner.load_from_result(result_file)
                logger.info("결과 파일 로드 완료")

            self.init_ui()
            setup_help_menu(self)  # 공통 도움말 메뉴
            logger.info("OverviewGUI UI 초기화 완료")

        except Exception as e:
            logger.error("OverviewGUI 초기화 실패", exc_info=True)
            raise

    def init_ui(self):
        self.setWindowTitle(f"🎓 전체 학생 보기 - {VERSION}")
        self.setGeometry(50, 50, 1400, 800)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 상단: 안내 및 선택 상태
        header_layout = QHBoxLayout()

        title_label = QLabel("📋 전체 학생 보기")
        title_label.setFont(QFont("", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # 선택 상태 표시
        self.selection_label = QLabel("반을 2개 선택하세요")
        self.selection_label.setFont(QFont("", 12))
        header_layout.addWidget(self.selection_label)

        # 수동 조정 버튼
        self.edit_btn = QPushButton("🔧 수동 조정 화면으로")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setMinimumWidth(180)
        self.edit_btn.setMinimumHeight(40)
        self.edit_btn.setFont(QFont("", 12))
        self.edit_btn.clicked.connect(self.open_editor)
        header_layout.addWidget(self.edit_btn)

        # 저장 버튼
        save_btn = QPushButton("💾 저장")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.export_to_excel)
        header_layout.addWidget(save_btn)

        main_layout.addLayout(header_layout)

        # 범례
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("범례:"))

        def add_legend(text, color):
            icon = QLabel()
            icon.setPixmap(create_circle_icon(color, 12).pixmap(12, 12))
            legend_layout.addWidget(icon)
            legend_layout.addWidget(QLabel(text))
            legend_layout.addSpacing(10)

        add_legend("특수", "#9C27B0")
        add_legend("분반", "#FFD700")
        add_legend("합반", "#2196F3")
        add_legend("전출", "#9E9E9E")
        add_legend("일반", "#FFFFFF")
        legend_layout.addStretch()
        main_layout.addLayout(legend_layout)

        # 칸반 보드 (반별 컬럼)
        kanban_layout = QHBoxLayout()
        kanban_layout.setSpacing(8)

        self.class_columns = {}
        for class_id in range(1, self.assigner.target_class_count + 1):
            column = ClassColumn(class_id, self.assigner)
            column.class_clicked.connect(self.on_class_clicked)
            column.student_moved.connect(self.on_student_moved)  # 드래그&드롭 시그널 연결
            self.class_columns[class_id] = column
            kanban_layout.addWidget(column)

        main_layout.addLayout(kanban_layout)

        # 하단: 통계
        stats_layout = QHBoxLayout()
        total_students = sum(len(students) for students in self.assigner.classes.values())
        self.stats_label = QLabel(f"총 학생 수: {total_students}명 | {self.assigner.target_class_count}개 반")
        self.stats_label.setFont(QFont("", 11))
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()

        version_label = QLabel(f"Version: {VERSION}")
        version_label.setStyleSheet("color: gray;")
        stats_layout.addWidget(version_label)
        main_layout.addLayout(stats_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def on_class_clicked(self, class_id):
        """반 클릭 핸들러"""
        if class_id in self.selected_classes:
            # 이미 선택된 반 클릭 → 선택 해제
            self.selected_classes.remove(class_id)
            self.class_columns[class_id].set_selected(False)
        else:
            if len(self.selected_classes) >= 2:
                # 2개 초과 → 첫 번째 선택 해제
                old_class = self.selected_classes.pop(0)
                self.class_columns[old_class].set_selected(False)

            self.selected_classes.append(class_id)
            self.class_columns[class_id].set_selected(True)

        self.update_selection_ui()

    def update_selection_ui(self):
        """선택 상태 UI 업데이트"""
        if len(self.selected_classes) == 0:
            self.selection_label.setText("반을 2개 선택하세요")
            self.edit_btn.setEnabled(False)
        elif len(self.selected_classes) == 1:
            self.selection_label.setText(f"선택: {self.selected_classes[0]}반 (1개 더 선택)")
            self.edit_btn.setEnabled(False)
        else:
            self.selection_label.setText(f"선택: {self.selected_classes[0]}반 ↔ {self.selected_classes[1]}반")
            self.edit_btn.setEnabled(True)

    def on_student_moved(self, from_class: int, to_class: int, student, insert_index: int = -1):
        """학생 이동 처리 (드래그 앤 드롭)"""
        logger.info(f"학생 이동: {student.이름} ({from_class}반 → {to_class}반, 위치: {insert_index})")

        if from_class == to_class:
            # 같은 반 내에서 순서 변경
            logger.info(f"같은 반 ({from_class}반) 내에서 순서 변경")
            
            if from_class in self.assigner.classes:
                students = self.assigner.classes[from_class]
                
                # 현재 위치 찾기
                if student in students:
                    current_index = students.index(student)
                    
                    # 학생 제거
                    students.pop(current_index)
                    
                    # 새 위치에 삽입
                    if insert_index >= 0:
                        # insert_index가 current_index보다 뒤에 있었다면 조정 필요
                        if insert_index > current_index:
                            insert_index -= 1
                        
                        # 범위 체크
                        if insert_index > len(students):
                            insert_index = len(students)
                        
                        students.insert(insert_index, student)
                        logger.info(f"순서 변경: {current_index} → {insert_index}")
                    else:
                        # 맨 뒤에 추가
                        students.append(student)
                        logger.info(f"순서 변경: {current_index} → 맨 뒤")
                    
                    # UI 새로고침
                    if from_class in self.class_columns:
                        self.class_columns[from_class].refresh_students()
        else:
            # 다른 반으로 이동
            logger.info(f"다른 반으로 이동: {from_class}반 → {to_class}반")
            
            # 1. 원래 반에서 학생 제거
            if from_class in self.assigner.classes:
                if student in self.assigner.classes[from_class]:
                    self.assigner.classes[from_class].remove(student)

            # 2. 목표 반에 학생 추가 (특정 위치에 삽입)
            if to_class not in self.assigner.classes:
                self.assigner.classes[to_class] = []

            if insert_index >= 0 and insert_index < len(self.assigner.classes[to_class]):
                # 특정 위치에 삽입
                self.assigner.classes[to_class].insert(insert_index, student)
            else:
                # 맨 뒤에 추가
                self.assigner.classes[to_class].append(student)

            # 3. 두 반의 UI 새로고침
            if from_class in self.class_columns:
                self.class_columns[from_class].refresh_students()
            if to_class in self.class_columns:
                self.class_columns[to_class].refresh_students()

            # 4. 하단 통계 업데이트
            self.update_stats()

            logger.info(f"학생 이동 완료: {from_class}반({len(self.assigner.classes.get(from_class, []))}명) → {to_class}반({len(self.assigner.classes.get(to_class, []))}명))")

    def update_stats(self):
        """하단 통계 업데이트"""
        total_students = sum(len(students) for students in self.assigner.classes.values())
        self.stats_label.setText(f"총 학생 수: {total_students}명 | {self.assigner.target_class_count}개 반")

    def open_editor(self):
        """수동 조정 화면 열기"""
        if len(self.selected_classes) != 2:
            return

        logger.info(f"Opening editor with classes: {self.selected_classes}")
        self.editor = InteractiveEditorGUI(
            self.result_file,
            initial_classes=self.selected_classes,
            assigner=self.assigner  # assigner 객체 직접 전달
        )
        self.editor.show()
        self.close()

    def export_to_excel(self):
        """Excel 파일로 내보내기"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "결과 파일 저장",
            os.path.join(get_base_path(), "03 배정 결과.xlsx"),
            "Excel files (*.xlsx)"
        )

        if not file_path:
            return

        try:
            self.assigner.generate_output(file_path)
            QMessageBox.information(self, "완료", f"✅ 파일이 저장되었습니다:\n\n{file_path}")
            logger.info(f"Results exported to: {file_path}")
        except Exception as e:
            logger.error(f"Export error: {e}", exc_info=True)
            QMessageBox.critical(self, "오류", f"❌ 파일 저장 중 오류:\n\n{str(e)}")


class InteractiveEditorGUI(QMainWindow):
    """수동 조정 화면 (Symmetrical Dual-Panel)"""

    def __init__(self, result_file: str, initial_classes: list = None, assigner: ClassAssigner = None):
        super().__init__()

        self.result_file = result_file  # 결과 파일 경로 저장
        self.initial_classes = initial_classes  # 초기 선택 반 저장

        logger.info("=" * 70)
        logger.info("InteractiveEditorGUI 초기화 시작")
        logger.info(f"결과 파일: {result_file}")
        logger.info(f"초기 선택 반: {initial_classes}")
        logger.info(f"Assigner 객체 전달됨: {assigner is not None}")

        # Assigner 로드
        try:
            if assigner is not None:
                # 외부에서 assigner 객체를 전달받은 경우 (OverviewGUI에서 호출)
                logger.info("전달받은 ClassAssigner 객체 사용")
                self.assigner = assigner
            else:
                # 파일에서 새로 로드하는 경우
                logger.info("ClassAssigner 객체 생성 중...")
                self.assigner = ClassAssigner(
                    student_file="",
                    rules_file="",
                    target_class_count=7
                )
                logger.info("ClassAssigner 객체 생성 완료")

                logger.info("결과 파일 로드 시작...")
                self.assigner.load_from_result(result_file)
                logger.info("결과 파일 로드 완료")

            logger.info("UI 초기화 시작...")
            self.init_ui()
            setup_help_menu(self)  # 공통 도움말 메뉴
            logger.info("UI 초기화 완료")

        except Exception as e:
            logger.error("InteractiveEditorGUI 초기화 실패", exc_info=True)
            raise

    def init_ui(self):
        """Symmetrical Layout"""
        self.setWindowTitle(f"🎓 학급 편성 수동 조정 - {VERSION}")
        self.setGeometry(100, 100, 1200, 700) # 너비 확장

        # 메인 위젯
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 1. 왼쪽 패널
        self.left_panel = ClassPanel("왼쪽 패널", self.assigner)
        self.left_panel.class_selected.connect(self.update_buttons_state)
        self.left_panel.student_dropped.connect(self.on_student_dropped)
        self.left_panel.order_changed.connect(self.on_order_changed)
        main_layout.addWidget(self.left_panel, stretch=4)

        # 2. 중앙 버튼 (이동)
        center_layout = QVBoxLayout()
        center_layout.addStretch()
        
        self.to_right_btn = QPushButton("▶\n이\n동")
        self.to_right_btn.setFixedSize(40, 100)
        self.to_right_btn.clicked.connect(self.on_btn_move_to_right)
        center_layout.addWidget(self.to_right_btn)
        
        center_layout.addSpacing(20)
        
        self.to_left_btn = QPushButton("◀\n이\n동")
        self.to_left_btn.setFixedSize(40, 100)
        self.to_left_btn.clicked.connect(self.on_btn_move_to_left)
        center_layout.addWidget(self.to_left_btn)
        
        center_layout.addStretch()
        main_layout.addLayout(center_layout)

        # 3. 오른쪽 패널
        self.right_panel = ClassPanel("오른쪽 패널", self.assigner)
        self.right_panel.class_selected.connect(self.update_buttons_state)
        self.right_panel.student_dropped.connect(self.on_student_dropped)
        self.right_panel.order_changed.connect(self.on_order_changed)
        main_layout.addWidget(self.right_panel, stretch=4)
        
        # 4. 맨 오른쪽: 범례 및 저장
        right_sidebar = QVBoxLayout()
        
        # 범례
        legend_group = QGroupBox("범례")
        legend_layout = QVBoxLayout()
        
        # Helper to create colored legend item
        def add_legend_item(text, color_code):
            item_layout = QHBoxLayout()
            icon_label = QLabel()
            # 16x16 Circle Icon
            icon_label.setPixmap(create_circle_icon(color_code, 16).pixmap(16, 16))
            text_label = QLabel(text)
            
            item_layout.addWidget(icon_label)
            item_layout.addWidget(text_label)
            item_layout.addStretch()
            legend_layout.addLayout(item_layout)

        add_legend_item("특수학생 (보라)", "#9C27B0")
        add_legend_item("분반 (노랑)", "#FFD700")
        add_legend_item("합반 (파랑)", "#2196F3")
        add_legend_item("전출 (회색)", "#9E9E9E")
        add_legend_item("일반 (흰색)", "#FFFFFF")
        legend_group.setLayout(legend_layout)
        right_sidebar.addWidget(legend_group)
        
        right_sidebar.addStretch()

        # 전체 보기로 돌아가기 버튼
        back_btn = QPushButton("📋\n전\n체")
        back_btn.setFixedSize(50, 80)
        back_btn.setToolTip("전체 학생 보기로 돌아가기")
        back_btn.clicked.connect(self.go_to_overview)
        right_sidebar.addWidget(back_btn)

        right_sidebar.addSpacing(10)

        # Export 버튼
        export_btn = QPushButton("💾\n저\n장")
        export_btn.setFixedSize(50, 80)
        export_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        export_btn.clicked.connect(self.export_to_excel)
        right_sidebar.addWidget(export_btn)

        # Version footer
        version_label = QLabel(f"v{VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #999999; font-size: 9px; margin-top: 5px;")
        right_sidebar.addWidget(version_label)
        
        main_layout.addLayout(right_sidebar)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 초기 버튼 상태 업데이트
        self.update_buttons_state()

        # 초기 반 선택 (OverviewGUI에서 전달받은 값 또는 기본값)
        if self.initial_classes and len(self.initial_classes) >= 2:
            self.left_panel.set_current_class(self.initial_classes[0])
            self.right_panel.set_current_class(self.initial_classes[1])
        elif self.assigner.target_class_count >= 2:
            self.left_panel.set_current_class(1)
            self.right_panel.set_current_class(2)
            
    def update_buttons_state(self):
        """버튼 활성화 상태 업데이트"""
        left_class = self.left_panel.current_class_id
        right_class = self.right_panel.current_class_id
        
        valid = (left_class is not None) and (right_class is not None) and (left_class != right_class)
        
        self.to_right_btn.setEnabled(valid)
        self.to_left_btn.setEnabled(valid)

    def on_btn_move_to_right(self):
        """왼쪽 -> 오른쪽 이동"""
        logger.info(f"Move to Right button clicked. From class {self.left_panel.current_class_id} to {self.right_panel.current_class_id}")
        self._move_selected_students(self.left_panel, self.right_panel)

    def on_btn_move_to_left(self):
        """오른쪽 -> 왼쪽 이동"""
        logger.info(f"Move to Left button clicked. From class {self.right_panel.current_class_id} to {self.left_panel.current_class_id}")
        self._move_selected_students(self.right_panel, self.left_panel)

    def _move_selected_students(self, source_panel, target_panel):
        """선택된 학생들을 소스 패널에서 타겟 패널로 이동"""
        source_class = source_panel.current_class_id
        target_class = target_panel.current_class_id
        
        if source_class is None or target_class is None:
            logger.warning("Move attempted with unselected source or target class.")
            return
            
        selected_items = source_panel.student_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "경고", "이동할 학생을 선택하세요.")
            logger.warning("No students selected for move operation.")
            return

        success_count = 0
        error_messages = []
        
        for item in selected_items:
            student = item.data(0, Qt.ItemDataRole.UserRole) # QTreeWidgetItem requires column index
            logger.debug(f"Attempting to move student {student.이름} from {source_class} to {target_class}")
            success, msg = self._execute_move(student, source_class, target_class, silent=True)
            if success:
                success_count += 1
                logger.info(f"Successfully moved {student.이름} to class {target_class}")
            else:
                error_messages.append(f"{student.이름}: {msg}")
                logger.warning(f"Failed to move {student.이름}: {msg}")
        
        # UI Refresh
        self.left_panel.refresh_data()
        self.right_panel.refresh_data()
        self.update_buttons_state() 
        
        if error_messages:
             QMessageBox.warning(self, "이동 실패", "\n".join(error_messages))

    def on_student_dropped(self, source_widget, target_widget, drop_index=-1):
        """Drag & Drop 핸들러 (Index 지원)"""
        source_class = getattr(source_widget, 'class_id', None)
        target_class = getattr(target_widget, 'class_id', None)
        
        logger.info(f"Student dropped. Source class: {source_class}, Target class: {target_class}, Index: {drop_index}")

        if source_class is None or target_class is None or source_class == target_class:
            logger.warning("Invalid drag & drop operation: source/target class unselected or same class.")
            return
            
        selected_items = source_widget.selectedItems()
        success_count = 0
        error_messages = []
        
        # Calculate insert position
        current_insert_index = drop_index
        if current_insert_index == -1:
            current_insert_index = len(self.assigner.classes[target_class])
        
        for item in selected_items:
            student = item.data(0, Qt.ItemDataRole.UserRole)
            logger.debug(f"Attempting to move student {student.이름} via drag & drop from {source_class} to {target_class}")
            
            # Pass insert_index
            success, msg = self._execute_move(student, source_class, target_class, insert_index=current_insert_index, silent=True)
            
            if success:
                 success_count += 1
                 logger.info(f"Successfully moved {student.이름} to class {target_class} via drag & drop")
                 if current_insert_index != -1:
                     current_insert_index += 1
            else:
                 error_messages.append(f"{student.이름}: {msg}")
                 logger.warning(f"Failed to move {student.이름} via drag & drop: {msg}")

        # Refresh
        self.left_panel.refresh_data()
        self.right_panel.refresh_data()
        
        if error_messages:
            QMessageBox.warning(self, "이동 실패", "\n".join(error_messages))

    def _execute_move(self, student, source_class, target_class, insert_index=-1, silent=False):
        """이동 실행 및 검증 (Index 지원) -> Returns (success, message)"""
        logger.debug(f"Executing move for {student.이름} from {source_class} to {target_class}")
        # 1. Validation
        if not self.assigner._can_assign(student, target_class):
             msg = "분반 규칙(가까운 사이 금지) 위반"
             logger.warning(f"Move failed for {student.이름}: {msg}")
             if not silent: QMessageBox.warning(self, "이동 불가", msg)
             return False, msg
        
        # Check for same name
        same_names = [s for s in self.assigner.classes[target_class] if s.이름 == student.이름]
        if same_names:
            msg = "동명이인 존재"
            logger.warning(f"Move failed for {student.이름}: {msg}")
            if not silent: QMessageBox.warning(self, "이동 불가", msg)
            return False, msg
            
        # 합반 규칙 경고
        together_group = None
        for group in self.assigner.together_groups:
            if student.이름 in group:
                together_group = group
                break

        if together_group:
            group_names = list(together_group)
            logger.warning(f"Together group rule detected for {student.이름}. Group: {group_names}")
            reply = QMessageBox.question(
                self,
                "합반 규칙 경고",
                f"⚠️ {student.이름} 학생은 합반 그룹입니다.\n\n"
                f"그룹 구성원: {', '.join(group_names)}\n\n"
                f"그룹에서 분리하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                logger.info(f"Move cancelled for {student.이름} due to together group rule (user choice).")
                return False, "합반 규칙 경고(사용자 취소)"

        # 2. Execution
        if student in self.assigner.classes[source_class]:
            self.assigner.classes[source_class].remove(student)
            student.assigned_class = target_class
            
            # Insert or Append
            if insert_index != -1:
                # Boundary check
                if insert_index > len(self.assigner.classes[target_class]):
                    insert_index = len(self.assigner.classes[target_class])
                self.assigner.classes[target_class].insert(insert_index, student)
            else:
                self.assigner.classes[target_class].append(student)

            logger.info(f"Student {student.이름} successfully moved from {source_class} to {target_class}.")
            return True, "성공"
        logger.error(f"Student {student.이름} not found in source class {source_class} during move operation.")
        return False, "학생 데이터 불일치"

    def on_order_changed(self, class_id, new_list):
        """Sync reordered list from Widget to Assigner"""
        if class_id in self.assigner.classes:
            self.assigner.classes[class_id] = new_list
            logger.info(f"Class {class_id} reordered internal. Count: {len(new_list)}")
        
    def export_to_excel(self):
        """Excel 파일로 내보내기"""
        logger.info("Export to Excel button clicked.")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "결과 파일 저장",
            os.path.join(get_base_path(), "03 배정 결과.xlsx"),
            "Excel files (*.xlsx)"
        )

        if not file_path:
            logger.info("Export to Excel cancelled by user.")
            return

        try:
            self.assigner.generate_output(file_path)
            QMessageBox.information(
                self,
                "완료",
                f"✅ 파일이 저장되었습니다:\n\n{file_path}"
            )
            logger.info(f"Results successfully exported to: {file_path}")
        except Exception as e:
            logger.error(f"Error exporting results to Excel: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "오류",
                f"❌ 파일 저장 중 오류:\n\n{str(e)}"
            )

    def go_to_overview(self):
        """전체 학생 보기 화면으로 돌아가기"""
        logger.info("Go to Overview button clicked.")

        # OverviewGUI로 이동 (assigner 객체 전달하여 변경사항 유지)
        try:
            self.overview_gui = OverviewGUI(self.result_file, assigner=self.assigner)
            self.overview_gui.show()
            self.close()
            logger.info("Returned to OverviewGUI successfully.")
        except Exception as e:
            logger.error(f"Failed to return to OverviewGUI: {e}", exc_info=True)
            QMessageBox.critical(self, "오류", f"전체 보기 화면 로드 중 오류:\n{str(e)}")


def set_global_style(app: QApplication) -> None:
    """전역 팔레트를 설정해 배경과 대비되는 텍스트 색을 적용합니다.
    Fusion 스타일은 유지하고, 배경 밝기에 따라 검정·흰 텍스트를 자동 선택합니다.
    """
    # Fusion 스타일은 이미 설정돼 있음 (main에서 호출 가능)
    # 기본 팔레트 복제
    palette = app.palette()
    # 배경 색을 기준으로 밝기 계산
    bg = palette.color(QPalette.ColorRole.Window)
    brightness = (0.299 * bg.red() + 0.587 * bg.green() + 0.114 * bg.blue())
    # 밝으면 어두운 텍스트, 어두우면 밝은 텍스트
    text_color = QColor(0, 0, 0) if brightness > 128 else QColor(255, 255, 255)
    # 텍스트 색 지정
    palette.setColor(QPalette.ColorRole.WindowText, text_color)
    palette.setColor(QPalette.ColorRole.ButtonText, text_color)
    palette.setColor(QPalette.ColorRole.Text, text_color)
    palette.setColor(QPalette.ColorRole.HighlightedText, text_color)
    # 강조 색 (버튼 등) 지정 – 파란색 강조
    palette.setColor(QPalette.ColorRole.Highlight, QColor(30, 144, 255))
    app.setPalette(palette)


def main():
    """PyQt6 애플리케이션 실행"""
    logger.info("Application Starting...")
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        set_global_style(app)  # 텍스트 대비 적용
        window = ClassAssignerStartGUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical("Critical Application Error in Main Loop", exc_info=True)
        raise


if __name__ == '__main__':
    main()
