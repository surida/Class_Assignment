
import sys
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QListWidgetItem
from PyQt6.QtCore import Qt

# Add project root to sys.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from class_assigner_gui_qt import InteractiveEditorGUI

# Mock Student class
class MockStudent:
    def __init__(self, name, gender='남', special=False):
        self.이름 = name
        self.성별 = gender
        self.특수반 = special
        self.난이도 = 3.0
        self.assigned_class = None
        self.전출 = False  # Added

# Mock ClassAssigner
class MockClassAssigner:
    def __init__(self):
        self.students = []
        self.classes = {i: [] for i in range(1, 8)} # 7 classes
        self.target_class_count = 7
        self.separation_rules = {}
        self.together_groups = []
        self.rules_file = "mock_rules.xlsx"

    def load_from_result(self, filepath):
        # Mock behavior: if file implies special weight, set it
        if "weight_5" in filepath:
             self.special_student_weight = 5.0
        else:
             self.special_student_weight = 3.0

    def _get_effective_count(self, class_num):
        return len(self.classes[class_num])
    
    def _can_assign(self, student, class_num):
        return True

class TestInteractiveEditorGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        with patch('class_assigner_gui_qt.ClassAssigner') as mock_assigner_cls:
            self.mock_assigner = MockClassAssigner()
            mock_assigner_cls.return_value = self.mock_assigner
            
            # Setup data
            s1 = MockStudent("학생1", "남") # Class 1
            s1.assigned_class = 1
            self.mock_assigner.classes[1].append(s1)
            
            s2 = MockStudent("학생2", "여") # Class 1
            s2.assigned_class = 1
            self.mock_assigner.classes[1].append(s2)
            
            s3 = MockStudent("학생3", "남") # Class 2
            s3.assigned_class = 2
            self.mock_assigner.classes[2].append(s3)

            self.mock_assigner.students = [s1, s2, s3]

            self.gui = InteractiveEditorGUI("dummy.xlsx")
            
    def test_ui_structure(self):
        """Test if panels are initialized"""
        self.assertIsNotNone(self.gui.left_panel)
        self.assertIsNotNone(self.gui.right_panel)
        self.assertEqual(self.gui.left_panel.class_list.count(), 7)

    def test_move_right_via_button(self):
        """Test moving Left -> Right via Button"""
        # Select Class 1 on Left
        self.gui.left_panel.set_current_class(1)
        # Select Class 2 on Right
        self.gui.right_panel.set_current_class(2)
        
        # Select Student1 on Left
        item = self.gui.left_panel.student_list.item(0) # 학생1
        item.setSelected(True)
        # Mock selection behavior since simple setSelected might not trigger everything if needed
        # But QListWidget.selectedItems() relies on it.
        
        # Execute Move
        with patch('PyQt6.QtWidgets.QMessageBox.information'): # Suppress info if any
            self.gui.on_btn_move_to_right()
            
        # Verify
        self.assertEqual(len(self.mock_assigner.classes[1]), 1) # One left
        self.assertEqual(len(self.mock_assigner.classes[2]), 2) # Two now

    def test_move_left_via_button(self):
        """Test moving Right -> Left via Button"""
        # Select Class 1 on Left
        self.gui.left_panel.set_current_class(1)
        # Select Class 2 on Right
        self.gui.right_panel.set_current_class(2)
        
        # Select Student3 on Right (initially in class 2)
        item = self.gui.right_panel.student_list.item(0) # 학생3
        item.setSelected(True)
        
        # Execute Move
        self.gui.on_btn_move_to_left()
        
        # Verify
        self.assertEqual(len(self.mock_assigner.classes[2]), 0) # Empty
        self.assertEqual(len(self.mock_assigner.classes[1]), 3) # All 3 here

    def test_drag_drop_move(self):
        """Test Drag & Drop (Left -> Right)"""
        self.gui.left_panel.set_current_class(1)
        self.gui.right_panel.set_current_class(2)
        
        # "학생1" Item
        item = QListWidgetItem("학생1")
        student_data = self.mock_assigner.students[0] # 학생1
        item.setData(Qt.ItemDataRole.UserRole, student_data)
        
        # Trigger on_student_dropped(source=Left, target=Right)
        with patch.object(self.gui.left_panel.student_list, 'selectedItems', return_value=[item]):
             self.gui.on_student_dropped(self.gui.left_panel.student_list, self.gui.right_panel.student_list)
        
        # Verify
        self.assertEqual(len(self.mock_assigner.classes[1]), 1)
        self.assertEqual(len(self.mock_assigner.classes[2]), 2)

if __name__ == '__main__':
    unittest.main()
