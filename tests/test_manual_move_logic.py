
import unittest
from unittest.mock import MagicMock, patch, ANY
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from collections import defaultdict

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock custom modules before importing GUI to avoid dependency issues during import if any
# (assuming class_assigner_gui_qt imports simple things, but let's be safe)
from class_assigner import Student

# Use a global app instance to avoid creating multiple QApplications
app = QApplication.instance() or QApplication(sys.argv)

from class_assigner_gui_qt import InteractiveEditorGUI

class TestManualMoveLogic(unittest.TestCase):
    def setUp(self):
        # Mock ClassAssigner to be returned when GUI creates one
        self.class_assigner_patcher = patch('class_assigner_gui_qt.ClassAssigner')
        self.MockClassAssigner = self.class_assigner_patcher.start()
        
        # Setup the mock assigner instance
        self.mock_assigner = self.MockClassAssigner.return_value
        self.mock_assigner.classes = {i: [] for i in range(1, 8)}
        self.mock_assigner.separation_rules = defaultdict(set)
        self.mock_assigner.together_groups = []
        self.mock_assigner.target_class_count = 7
        self.mock_assigner._can_assign.return_value = True # Default to allowing assignment
        
        # Initialize GUI with a dummy file path
        # prevent load_from_result from actually doing checking file existence if patched
        self.mock_assigner.load_from_result.return_value = None
        
        self.gui = InteractiveEditorGUI("dummy_result.xlsx")
        
        # Replace the GUI's assigner with our configured mock (just to be sure it's the same ref)
        self.gui.assigner = self.mock_assigner

        # Create a dummy student
        self.student = Student(
            학년=5, 원반=1, 원번호=1, 이름='테스트학생', 성별='남', 
            점수=90, 특수반=False, 전출=False, 난이도=0.0, 비고=""
        )
        self.student.assigned_class = 1
        
        # Place student in class 1
        self.mock_assigner.classes[1] = [self.student]
        
    def tearDown(self):
        self.class_assigner_patcher.stop()
        self.gui.close()

    def test_move_success(self):
        """Test successful move from Class 1 to Class 2"""
        # Execute move
        success, msg = self.gui._execute_move(self.student, 1, 2)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(msg, "성공")
        self.assertEqual(self.student.assigned_class, 2)
        self.assertNotIn(self.student, self.mock_assigner.classes[1])
        self.assertIn(self.student, self.mock_assigner.classes[2])

    def test_move_failed_validation(self):
        """Test move blocked by _can_assign (Separation Rules)"""
        # Setup: _can_assign returns False
        self.mock_assigner._can_assign.return_value = False
        
        # Execute move
        with patch.object(QMessageBox, 'warning') as mock_warning:
            success, msg = self.gui._execute_move(self.student, 1, 2)
            
            self.assertFalse(success)
            self.assertIn("분반 규칙", msg)
            self.assertEqual(self.student.assigned_class, 1) # Should remain in class 1
            mock_warning.assert_called_once()

    def test_move_failed_duplicate_name(self):
        """Test move blocked by duplicate name in target class"""
        # Setup: Class 2 has a student with same name
        duplicate_student = Student(
            학년=5, 원반=2, 원번호=2, 이름='테스트학생', 성별='여', 
            점수=80, 특수반=False, 전출=False, 난이도=0.0, 비고=""
        )
        self.mock_assigner.classes[2] = [duplicate_student]
        
        # Execute move
        with patch.object(QMessageBox, 'warning') as mock_warning:
            success, msg = self.gui._execute_move(self.student, 1, 2)
            
            self.assertFalse(success)
            self.assertIn("동명이인", msg)
            self.assertEqual(self.student.assigned_class, 1)
            mock_warning.assert_called_once()

    def test_move_together_group_confirmed(self):
        """Test move with together group warning -> User clicks Yes"""
        # Setup: Student is in a together group
        self.mock_assigner.together_groups = [{'테스트학생', '친구'}]
        
        # Mock QMessageBox to return Yes
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes):
            success, msg = self.gui._execute_move(self.student, 1, 2)
            
            self.assertTrue(success)
            self.assertEqual(self.student.assigned_class, 2)

    def test_move_together_group_cancelled(self):
        """Test move with together group warning -> User clicks No"""
        # Setup: Student is in a together group
        self.mock_assigner.together_groups = [{'테스트학생', '친구'}]
        
        # Mock QMessageBox to return No
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.No):
            success, msg = self.gui._execute_move(self.student, 1, 2)
            
            self.assertFalse(success)
            self.assertIn("사용자 취소", msg)
            self.assertEqual(self.student.assigned_class, 1)

    def test_move_student_not_found(self):
        """Test failure when student is not in the source class list"""
        # Remove student from class 1 (simulate sync error)
        self.mock_assigner.classes[1] = []
        
        success, msg = self.gui._execute_move(self.student, 1, 2)
        
        self.assertFalse(success)
        self.assertIn("데이터 불일치", msg)

if __name__ == '__main__':
    unittest.main()
