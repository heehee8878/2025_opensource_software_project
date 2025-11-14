from typing import Dict, List, Tuple
import os

"""파일 기반 에이전트 프롬프트 구성 및 응답 파싱"""
class AgentManager:
    CODE_BEGIN = "<<BEGIN_FILE>>"
    CODE_END = "<<END_FILE>>"
    DESC_BEGIN = "<<BEGIN_DESC>>"
    DESC_END = "<<END_DESC>>"

    def __init__(self, model_manager):
        self.model_manager = model_manager

    def run(self, user_prompt: str, file_path: str, file_content: str) -> Tuple[bool, str, str, str]:
        messages = self._build_messages(user_prompt, file_path, file_content)
        ok, result = self.model_manager.chat(messages)
        if not ok:
            return False, result, "", ""
        # 코드와 설명 각각 추출
        extracted_code = self._extract_code(result)
        extracted_desc = self._extract_desc(result)
        print("Extracted Description:", extracted_desc)
        return True, result, extracted_code, extracted_desc

    def _build_messages(self, user_prompt: str, file_path: str, file_content: str) -> List[Dict[str, str]]:
        filename = os.path.basename(file_path)
        language = self._guess_language(filename)

        system = (
            "당신은 정확한 리팩토링과 버그 수정을 수행하는 전문 소프트웨어 엔지니어입니다. "
            "사용자로부터 파일의 전체 내용과 지시사항을 받게 됩니다. "
            "관련 없는 코드는 보존하면서 파일의 완전한 업데이트된 내용을 생성하는 것이 목표입니다. "
            "반드시 두 개의 블록을 반환하세요: 설명과 전체 업데이트된 파일 내용. "
            f"설명은 반드시 {self.DESC_BEGIN}와 {self.DESC_END} 사이에 마크다운 형식으로 작성하세요. "
            f"최종 파일 내용은 반드시 {self.CODE_BEGIN}와 {self.CODE_END} 사이에 작성하세요. "
            "마커 안에는 추가 설명이나 백틱(```)을 포함하지 마세요. "
            "모든 설명은 한글로 작성하세요."
        )

        user = (
            f"작업: {user_prompt}\n\n"
            f"파일 경로: {file_path}\n"
            f"언어: {language}\n\n"
            "원본 파일 내용:\n" \
            "```" + language + "\n" + file_content + "\n```\n\n" \
            "제약 사항:\n" \
            "- 필요하지 않은 경우 파일 포맷과 import는 유지하세요.\n" \
            "- 지시사항을 완전히 구현하세요.\n" \
            "- 작업을 적용할 수 없는 경우에도 수정되지 않은 전체 파일을 마커 안에 반환하세요.\n\n" \
            "반환 형식 (필수):\n" \
            f"{self.DESC_BEGIN}\n" \
            "<무엇이 변경되었고 왜 변경되었는지 한글로 설명. 마크다운 형식 사용 가능 (**, *, -, > 등)>\n" \
            f"{self.DESC_END}\n\n" \
            f"{self.CODE_BEGIN}\n" \
            "<업데이트된 전체 파일 내용>\n" \
            f"{self.CODE_END}"
        )

        return [
            { 'role': 'system', 'content': system },
            { 'role': 'user', 'content': user },
        ]

    def _extract_code(self, text: str) -> str:
        # 우선 지정 마커로 추출
        start = text.find(self.CODE_BEGIN)
        end = text.find(self.CODE_END)
        if start != -1 and end != -1 and end > start:
            return text[start + len(self.CODE_BEGIN):end].strip('\n')

        import re
        fence = re.search(r"```[a-zA-Z0-9_+-]*\n([\s\S]*?)```", text)
        if fence:
            return fence.group(1).strip('\n')

        return ""

    def _extract_desc(self, text: str) -> str:
        # 지정 마커로 설명 추출
        start = text.find(self.DESC_BEGIN)
        end = text.find(self.DESC_END)
        if start != -1 and end != -1 and end > start:
            # 앞뒤 공백만 제거하고 중간 줄바꿈은 보존
            extracted = text[start + len(self.DESC_BEGIN):end]
            return extracted.strip()
        return ""

    @staticmethod
    def _guess_language(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        return {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.json': 'json',
            '.md': 'markdown',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.java': 'java',
            '.html': 'html',
            '.css': 'css',
        }.get(ext, '')
