import os
from PyQt5.QtWidgets import QTreeWidgetItem

class FileManager:
    def __init__(self):
        self.item_map = {}  # { path: QTreeWidgetItem }
    
    def load_folder_tree(self, file_list_widget, folder_path):
        file_list_widget.clear()
        self.item_map.clear()
        
        for root, dirs, files in os.walk(folder_path):
            rel = os.path.relpath(root, folder_path)
            if rel == '.':
                parent = None
            else:
                parent = self.item_map.get(rel)
                if parent is None:
                    parent = QTreeWidgetItem(file_list_widget)
                    parent.setText(0, os.path.basename(rel))
                    self.item_map[rel] = parent

            for dir in dirs:
                key = os.path.normpath(os.path.join(rel if rel != '.' else '', dir))
                if parent is None:
                    dir_item = QTreeWidgetItem(file_list_widget)
                    dir_item.setText(0, f"📁 {dir}")
                    dir_item.setData(0, 1, dir)
                else:
                    dir_item = QTreeWidgetItem(parent)
                    dir_item.setText(0, f"📁 {dir}")
                    dir_item.setData(0, 1, dir)
                self.item_map[key] = dir_item

            for file in files:
                if parent is None:
                    file_item = QTreeWidgetItem(file_list_widget)
                    file_item.setText(0, file)
                    file_item.setData(0, 1, file)
                else:
                    file_item = QTreeWidgetItem(parent)
                    file_item.setText(0, file)
                    file_item.setData(0, 1, file)
    
    def read_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), None
        except Exception as e:
            return None, str(e)
    
    def save_file(self, file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_file_path_from_item(self, item, folder_path):
        path_parts = []
        current = item
        while current is not None:
            # 저장된 실제 이름 가져오기
            actual_name = current.data(0, 1)
            if actual_name:
                path_parts.insert(0, actual_name)
            current = current.parent()
        
        return os.path.join(folder_path, *path_parts)
    
    def create_file(self, file_path):
        """새 파일 생성"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")
            return True, None
        except Exception as e:
            return False, str(e)
    
    def create_folder(self, folder_path):
        """새 폴더 생성"""
        try:
            os.makedirs(folder_path, exist_ok=True)
            return True, None
        except Exception as e:
            return False, str(e)

    def delete_item(self, item_path, is_directory):
        """파일 또는 폴더 삭제"""
        try:
            if is_directory:
                import shutil
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
            return True, None
        except Exception as e:
            return False, str(e)
