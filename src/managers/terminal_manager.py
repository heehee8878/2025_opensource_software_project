import os
import shutil
import re
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal, QProcess

"""터미널 프로세스 관리 클래스"""
class TerminalManager(QObject):
    output_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.process: QProcess | None = None
        self.working_directory: str | None = None
        self.is_running: bool = False

    """터미널 시작 (지속형 셸 프로세스)"""
    def start_terminal(self, working_directory: str):
        self.stop_terminal()
        self.working_directory = working_directory

        self.process = QProcess()
        self.process.setWorkingDirectory(working_directory)

        if os.name == 'nt':
            # Windows: PowerShell
            program = 'powershell'
            args = ['-NoLogo']
            self.process.setProgram(program)
            self.process.setArguments(args)
        else:
            # macOS/Linux: zsh 또는 bash, 가능하면 PTY를 위해 'script' 래핑
            program = '/bin/zsh' if os.path.exists('/bin/zsh') else '/bin/bash'
            args = ['-i']  # interactive

            script_path = shutil.which('script')
            if script_path:
                # macOS/BSD 'script': file 뒤에 command 인자 배치
                # 'script -q /dev/null /bin/zsh -i'
                self.process.setProgram(script_path)
                self.process.setArguments(['-q', '/dev/null', program] + args)
            else:
                self.process.setProgram(program)
                self.process.setArguments(args)

            # 표준 출력/에러 수신
            self.process.readyReadStandardOutput.connect(self._on_stdout)
            self.process.readyReadStandardError.connect(self._on_stderr)
            self.process.finished.connect(self._on_finished)
            self.process.errorOccurred.connect(self._on_error)

            self.process.start()
            started = self.process.waitForStarted(3000)
            self.is_running = started

        if started:
            # 초기 PWD 동기화
            self.execute_command(f'cd "{working_directory}"')
        else:
            self.output_received.emit('터미널 시작 실패\n')

    def _on_stdout(self):
        if not self.process:
            return
        text = bytes(self.process.readAllStandardOutput()).decode('utf-8', errors='ignore')
        if text:
            self.output_received.emit(self._sanitize_output(text))

    def _on_stderr(self):
        if not self.process:
            return
        text = bytes(self.process.readAllStandardError()).decode('utf-8', errors='ignore')
        if text:
            self.output_received.emit(self._sanitize_output(text))

    def _on_finished(self, exitCode: int, exitStatus):
        self.is_running = False
        # 세션 종료 알림
        self.output_received.emit("\n[세션 종료]\n")

    def _on_error(self, error):
        # 상태만 false로
        self.is_running = False

    """명령/입력 전송: 실행 중 프로세스의 stdin으로 전달"""
    def execute_command(self, command: str):
        if not self.process or not self.is_running:
            # 자동 재시작 시도
            if not self.ensure_running():
                return False, "터미널이 실행 중이 아닙니다. 폴더를 다시 열거나 명령을 다시 시도하세요."
        try:
            data = (command + '\n').encode('utf-8')
            self.process.write(data)
            # flush 대신 전송 완료 대기 (QProcess에는 flush가 없음)
            self.process.waitForBytesWritten(1000)
            return True, ""
        except Exception as e:
            return False, f"입력 실패: {str(e)}"

    """작업 디렉토리 변경(셸 세션과 내부 상태 모두)"""
    def change_directory(self, path: str):
        if os.path.isdir(path):
            self.working_directory = path
            # 세션이 죽어있다면 자동 재시작
            self.execute_command(f'cd "{path}"')
            return True, f"디렉토리 변경: {path}"
        else:
            return False, f"디렉토리를 찾을 수 없습니다: {path}"

    """현재 작업 디렉토리 반환(내부 상태)"""
    def get_current_directory(self):
        return self.working_directory if self.working_directory else ""

    """터미널 종료"""
    def stop_terminal(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.waitForFinished(1000)
            except Exception:
                pass
            self.process = None
        self.is_running = False

    # --------- helpers ----------
    def _sanitize_output(self, text: str) -> str:
        """
        ANSI/OSC 이스케이프 시퀀스를 제거하고, 캐리지 리턴(\r)를 개행으로 정규화.
        색상/스타일 제어 코드가 QTextEdit에 그대로 노출되는 것을 방지.
        """
        # Normalize carriage returns
        text = text.replace('\r', '\n')

        # Remove OSC sequences: ESC ] ... BEL or ESC ] ... ESC \
        text = re.sub(r"\x1B\][^\x07]*(\x07|\x1b\\)", "", text)

        # Remove CSI sequences: ESC [ ... letters
        text = re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text)

        # Remove other ESC sequences like ESC ( B, etc.
        text = re.sub(r"\x1B[()][0-2AB]", "", text)

        return text

    def ensure_running(self) -> bool:
        """셸이 종료된 경우 working_directory 기준으로 자동 재시작."""
        if self.process and self.is_running:
            return True
        if not self.working_directory:
            return False
        self.start_terminal(self.working_directory)
        return bool(self.process and self.is_running)
