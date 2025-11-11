import os
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTreeWidgetItem, QMessageBox

# UI파일 연결
form_class = uic.loadUiType("./ui/editor.ui")[0]

# 프로그램 메인을 담당하는 Class 선언
class MainClass(QMainWindow, form_class):
    def __init__(self) :
        QMainWindow.__init__(self)
        # 연결한 Ui를 준비한다.
        self.setupUi(self)

        # QAction 위젯에 기능을 연결한다.
        self.actionOpen.triggered.connect(self.folderOpen)
        self.actionSave.triggered.connect(self.saveFile)

        # fileViewer라는 QTreeWidget 위젯의 아이템 클릭 시, 부모가 있을 시 file open하기
        self.fileViewer.itemClicked.connect(self.fileOpen)

    def saveFile(self):
        # 현재 열려있는 파일 경로 가져오기
        file_path = self.filenameLabel.text()
        if not file_path or not os.path.isfile(file_path):
            print("No file to save")
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                content = self.codeEdit.toPlainText()
                f.write(content)
            # 저장 완료 박스
            QMessageBox.information(self, "저장 완료", f"파일이 저장되었습니다:\n{file_path}")
            print(f"File saved: {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")

    def fileOpen(self, item, column):
        # 파일이면 내용 가져와서 codeEdit라는 QTextEdit에 넣기
        if item.parent() is None and not hasattr(self, 'opened_file_path'):
            return
        
        # 파일 경로 재구성
        path_parts = []
        current = item
        while current is not None:
            path_parts.insert(0, current.text(0))
            current = current.parent()
        
        file_path = os.path.join(self.opened_file_path, *path_parts)
        
        # 파일인지 확인
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.codeEdit.setPlainText(content)
                self.filenameLabel.setText(file_path)
                print(f"Opened file: {file_path}")
            except Exception as e:
                print(f"Error opening file: {e}")
                self.codeEdit.setPlainText(f"Error: Unable to open file\n{str(e)}")
        else:
            print(f"Not a file: {file_path}")

    def folderOpen(self):
        # 폴더 선택 다이얼로그 열기
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.opened_file_path = folder_path
            print("Opened Folder:", self.opened_file_path)

            self.fileViewer.clear()
            self.item_map = {} # 맵 구조: 경로 -> QTreeWidgetItem
            for root, dirs, files in os.walk(folder_path):
                rel = os.path.relpath(root, folder_path)
                if rel == '.':
                    parent = None
                else:
                    parent = self.item_map.get(rel)
                    if parent is None:
                        parent = QTreeWidgetItem(self.fileViewer)
                        parent.setText(0, os.path.basename(rel))
                        self.item_map[rel] = parent

                for d in dirs:
                    key = os.path.normpath(os.path.join(rel if rel != '.' else '', d))
                    if parent is None:
                        dir_item = QTreeWidgetItem(self.fileViewer)
                        dir_item.setText(0, d)
                    else:
                        dir_item = QTreeWidgetItem(parent)
                        dir_item.setText(0, d)
                    self.item_map[key] = dir_item

                for file in files:
                    if parent is None:
                        file_item = QTreeWidgetItem(self.fileViewer)
                        file_item.setText(0, file)
                    else:
                        file_item = QTreeWidgetItem(parent)
                        file_item.setText(0, file)
        else:
            print("No folder selected")

if __name__ == "__main__" :
    app = QApplication(sys.argv) 
    window = MainClass() 
    window.show()
    app.exec_()