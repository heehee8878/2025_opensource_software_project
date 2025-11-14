import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QMenu, QInputDialog, QTreeWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from src.managers.file_manager import FileManager
from src.managers.terminal_manager import TerminalManager
from src.managers.model_manager import ModelManager
from src.managers.agent_manager import AgentManager

# Load UI file
form_class = uic.loadUiType("./ui/editor.ui")[0]

"""에디터 메인 윈도우 클래스"""
class EditorWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Manager 초기화
        self.file_manager = FileManager()
        self.terminal_manager = TerminalManager()
        self.model_manager = ModelManager()
        self.agent_manager = AgentManager(self.model_manager)
        
        # global 상태 변수
        self.opened_folder_path = ""
        self.opened_file_path = ""
        self.opened_file_name = ""
        
        # Initialize UI
        self.filename_label.setText("Untitled")
        self.file_list.clear()
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)

        # Hotkeys
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionSave.setShortcut("Ctrl+S")
        self.actionExit.setShortcut("Ctrl+Q")
        
        # 터미널 초기 메시지
        self.terminal_output.setPlainText("터미널이 준비되었습니다. 폴더를 열면 해당 디렉토리에서 시작됩니다.\n")
        
        # 초기 상태: 폴더 열기 버튼 표시
        self.file_list_stack.setCurrentIndex(0)
        
        # Connect events
        self._connect_events()
        # 터미널 출력 스트림 연결
        self.terminal_manager.output_received.connect(self.append_terminal_output)
    
    """이벤트 연결"""
    def _connect_events(self):
        self.actionOpen.triggered.connect(self.open_folder)
        self.actionSave.triggered.connect(self.save_file)
        self.actionExit.triggered.connect(self.close)
        self.file_list.itemClicked.connect(self.open_file)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.terminal_input.returnPressed.connect(self.execute_terminal_command)
        self.open_folder_button.clicked.connect(self.open_folder)
        self.agent_enterButton.clicked.connect(self.on_agent_generate)
    

    """폴더 열기"""
    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder_path:
            self.opened_folder_path = folder_path
            print("Opened Folder:", self.opened_folder_path)
            
            self.file_list_stack.setCurrentIndex(1)
            
            self.file_manager.load_folder_tree(self.file_list, folder_path)
            
            # 터미널 디렉토리 설정
            self.terminal_manager.start_terminal(folder_path)
            self.append_terminal_output(f"\n작업 디렉토리: {folder_path}\n")
        else:
            print("No folder selected")
    
    """파일 열기"""
    def open_file(self, item, column):
        if item.parent() is None and not hasattr(self, 'opened_folder_path'):
            return
        
        file_path = self.file_manager.get_file_path_from_item(item, self.opened_folder_path)
        
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
    
    """파일 저장"""
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
    
    """파일 리스트 우클릭 컨텍스트 메뉴 표시"""
    def show_context_menu(self, position):
        item = self.file_list.itemAt(position)
        if not item:
            return
        
        file_path = self.file_manager.get_file_path_from_item(item, self.opened_folder_path)
        is_directory = os.path.isdir(file_path)
        
        menu = QMenu(self)
        
        if is_directory:
            add_file_action = menu.addAction("파일 추가")
            add_file_action.triggered.connect(lambda: self.add_file_to_folder(item, file_path))
            menu.addSeparator()
        
        delete_action = menu.addAction("삭제")
        delete_action.triggered.connect(lambda: self.delete_item(item, file_path, is_directory))
        
        menu.exec_(self.file_list.viewport().mapToGlobal(position))
    
    """폴더에 새 파일 추가"""
    def add_file_to_folder(self, folder_item, folder_path):
        file_name, ok = QInputDialog.getText(self, "파일 추가", "새 파일 이름을 입력하세요:")
        
        if ok and file_name:
            new_file_path = os.path.join(folder_path, file_name)
            
            if os.path.exists(new_file_path):
                QMessageBox.warning(self, "오류", "같은 이름의 파일이 이미 존재합니다.")
                return
            
            success, error = self.file_manager.create_file(new_file_path)
            
            if success:
                new_item = QTreeWidgetItem(folder_item)
                new_item.setText(0, file_name)
                new_item.setData(0, 1, file_name)
                folder_item.setExpanded(True)
                
                QMessageBox.information(self, "성공", f"파일이 생성되었습니다:\n{new_file_path}")
                print(f"File created: {new_file_path}")
            else:
                QMessageBox.critical(self, "오류", f"파일 생성 실패:\n{error}")
    
    """파일 또는 폴더 삭제"""
    def delete_item(self, item, item_path, is_directory):
        item_type = "폴더" if is_directory else "파일"
        reply = QMessageBox.question(
            self, 
            "삭제 확인", 
            f"정말 이 {item_type}를 삭제하시겠습니까?\n{item_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = self.file_manager.delete_item(item_path, is_directory)
            
            if success:
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                else:
                    index = self.file_list.indexOfTopLevelItem(item)
                    self.file_list.takeTopLevelItem(index)
                
                # 현재 열린 파일이 삭제된 경우 에디터 초기화
                if self.opened_file_path == item_path:
                    self.code_input.setPlainText("")
                    self.filename_label.setText("Untitled")
                    self.opened_file_path = ""
                    self.opened_file_name = ""
                
                QMessageBox.information(self, "성공", f"{item_type}가 삭제되었습니다.")
                print(f"Deleted: {item_path}")
            else:
                QMessageBox.critical(self, "오류", f"{item_type} 삭제 실패:\n{error}")
    
    """터미널 명령어 실행"""
    def execute_terminal_command(self):
        command = self.terminal_input.text().strip()
        if not command:
            return
        
        # 현재 디렉토리 표시
        current_dir = self.terminal_manager.get_current_directory()
        prompt = f"PS {current_dir}> " if current_dir else "> "
        
        # 명령어 표시
        self.append_terminal_output(f"{prompt}{command}\n")
        self.terminal_input.clear()
        
        # cd
        if command.startswith("cd "):
            new_path = command[3:].strip().strip('"').strip("'")
            
            # 상대 경로
            if not os.path.isabs(new_path):
                new_path = os.path.join(current_dir, new_path)
            
            new_path = os.path.normpath(new_path)
            success, message = self.terminal_manager.change_directory(new_path)
            self.append_terminal_output(f"{message}\n")
        
        # clear
        elif command.lower() in ["clear", "cls"]:
            self.terminal_output.clear()
            self.append_terminal_output("터미널이 초기화되었습니다.\n")
        
        # else
        else:
            # 지속형 셸에 명령/입력을 전달
            success, msg = self.terminal_manager.execute_command(command)
            if not success and msg:
                self.append_terminal_output(msg + "\n")
    
    """터미널 출력에 텍스트 추가"""
    def append_terminal_output(self, text):
        self.terminal_output.moveCursor(QTextCursor.End)
        self.terminal_output.insertPlainText(text)
        self.terminal_output.moveCursor(QTextCursor.End)

    """에이전트 생성 실행"""
    def on_agent_generate(self):
        # 파일이 열려 있어야 함
        if not self.opened_file_path:
            QMessageBox.warning(self, "에이전트", "먼저 파일을 열어주세요.")
            return

        # 사용자 프롬프트와 현재 코드(수정 전/중)를 가져옴
        user_prompt = self.agent_promptEdit.toPlainText().strip()
        if not user_prompt:
            QMessageBox.information(self, "에이전트", "프롬프트를 입력해주세요.")
            return
        
        self.agent_promptEdit.clear()

        current_code = self.code_input.toPlainText()

        # 실행 중 표시
        self.agent_enterButton.setEnabled(False)
        self.agent_enterButton.setText("…")
        self.agent_resultEdit.setPlainText("LLM 호출 중입니다…")
        try:
            ok, raw, extracted_code, extracted_desc = self.agent_manager.run(user_prompt, self.opened_file_path, current_code)
        finally:
            self.agent_enterButton.setEnabled(True)
            self.agent_enterButton.setText("✦")

        if not ok:
            self.agent_resultEdit.setHtml(self._format_as_html(raw))
            QMessageBox.critical(self, "에이전트 오류", raw)
            return

        # 설명 블록이 있으면 그걸 표시, 없으면 전체 응답 표시
        if extracted_desc:
            self.agent_resultEdit.setHtml(self._format_as_html(extracted_desc))
        else:
            self.agent_resultEdit.setHtml(self._format_as_html(raw))

        # 포맷에 맞는 코드 추출 성공 시 코드 입력창에 반영
        if extracted_code:
            self.code_input.setPlainText(extracted_code)
        else:
            # 추출 실패 시 안내 유지
            QMessageBox.information(self, "안내", "응답에서 수정된 코드를 추출하지 못했습니다. 우측 응답을 확인해주세요.")

    def _format_as_html(self, text: str) -> str:
        """마크다운 텍스트를 HTML로 변환"""
        try:
            import markdown
            # 마크다운 확장 기능 포함 (테이블, 코드 하이라이트 등)
            html_content = markdown.markdown(
                text,
                extensions=['extra', 'nl2br', 'sane_lists']
            )
            # 기본 스타일 적용
            styled_html = f'''
            <div style="color: #d4d4d4; font-family: 'Noto Sans KR', sans-serif; font-size: 11pt; line-height: 1.6;">
                {html_content}
            </div>
            <style>
                strong {{ color: #4ec9b0; font-weight: bold; }}
                em {{ color: #ce9178; font-style: italic; }}
                code {{ background-color: #1e1e1e; color: #d7ba7d; padding: 2px 4px; border-radius: 3px; font-family: 'Consolas', monospace; }}
                h1, h2, h3 {{ color: #569cd6; }}
                ul, ol {{ padding-left: 20px; }}
                blockquote {{ border-left: 3px solid #569cd6; padding-left: 10px; margin-left: 0; color: #9cdcfe; }}
            </style>
            '''
            return styled_html
        except ImportError:
            # markdown 라이브러리가 없으면 기본 HTML 처리
            import html
            escaped = html.escape(text)
            formatted = escaped.replace('\n', '<br>')
            return f'<div style="color: #d4d4d4; font-family: \'Noto Sans KR\', sans-serif; font-size: 11pt; line-height: 1.6;">{formatted}</div>'
