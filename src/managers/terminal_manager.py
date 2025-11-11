import subprocess
import os
from PyQt5.QtCore import QObject, pyqtSignal

"""터미널 프로세스 관리 클래스"""
class TerminalManager(QObject):
    output_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.working_directory = None
        self.is_running = False
        
    """터미널 시작"""
    def start_terminal(self, working_directory):
        self.working_directory = working_directory
        self.is_running = True
        
    """명령어 실행"""
    def execute_command(self, command):
        if not self.working_directory:
            return False, "작업 디렉토리가 설정되지 않았습니다."
        
        try:
            # Windows
            if os.name == 'nt':
                # PowerShell
                process = subprocess.Popen(
                    ['powershell', '-Command', command],
                    cwd=self.working_directory,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    shell=True
                )
            else:
                # Linux/Mac
                process = subprocess.Popen(
                    command,
                    cwd=self.working_directory,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    shell=True
                )
            
            # 출력 읽기
            stdout, stderr = process.communicate(timeout=10)
            
            output = ""
            if stdout:
                output += stdout
            if stderr:
                output += stderr
            
            return True, output
        except subprocess.TimeoutExpired:
            process.kill()
            return True, "명령어 실행 시간이 초과되었습니다."
        except Exception as e:
            return False, f"오류: {str(e)}"
    
    """작업 디렉토리 변경"""
    def change_directory(self, path):
        if os.path.isdir(path):
            self.working_directory = path
            return True, f"디렉토리 변경: {path}"
        else:
            return False, f"디렉토리를 찾을 수 없습니다: {path}"
    
    """현재 작업 디렉토리 반환"""
    def get_current_directory(self):
        return self.working_directory if self.working_directory else ""
    
    """터미널 종료"""
    def stop_terminal(self):
        if self.process:
            self.process.terminate()
        self.is_running = False
