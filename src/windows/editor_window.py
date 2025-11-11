import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from src.managers.file_manager import FileManager

# Load UI file
form_class = uic.loadUiType("./ui/editor.ui")[0]

class EditorWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 파일 관리자 초기화
        self.file_manager = FileManager()
        
        # 상태 변수
        self.opened_folder_path = ""
        self.opened_file_path = ""
        self.opened_file_name = ""
        
        # UI 초기 설정
        self.filename_label.setText("Untitled")
        self.file_list.clear()
        
        # 이벤트 연결
        self._connect_events()
    
    def _connect_events(self):
        self.actionOpen.triggered.connect(self.open_folder)
        self.actionSave.triggered.connect(self.save_file)
        self.actionExit.triggered.connect(self.close)
        self.file_list.itemClicked.connect(self.open_file)
    
    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder_path:
            self.opened_folder_path = folder_path
            print("Opened Folder:", self.opened_folder_path)
            
            # 파일 트리 로드
            self.file_manager.load_folder_tree(self.file_list, folder_path)
        else:
            print("No folder selected")
    
    def open_file(self, item, column):
        if item.parent() is None and not hasattr(self, 'opened_folder_path'):
            return
        
        # 파일 경로 구성
        file_path = self.file_manager.get_file_path_from_item(item, self.opened_folder_path)
        
        # 파일인지 확인
        if os.path.isfile(file_path):
            content, error = self.file_manager.read_file(file_path)
            
            if error:
                print(f"Error opening file: {error}")
                self.code_input.setPlainText("")
            else:
                self.code_input.setPlainText(content)
                self.opened_file_path = file_path
                self.opened_file_name = os.path.basename(file_path)
                self.filename_label.setText(self.opened_file_name)
                print(f"Opened file: {file_path}")
        else:
            print(f"Not a file: {file_path}")
    
    def save_file(self):
        if not self.opened_file_path or not os.path.isfile(self.opened_file_path):
            print("No file to save")
            return
        
        content = self.code_input.toPlainText()
        success, error = self.file_manager.save_file(self.opened_file_path, content)
        
        if success:
            QMessageBox.information(self, "저장 완료", f"파일이 저장되었습니다:\n{self.opened_file_path}")
            print(f"File saved: {self.opened_file_path}")
        else:
            print(f"Error saving file: {error}")
