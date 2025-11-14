import os
import json
from typing import List, Dict, Optional, Tuple

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore


class ModelManager:
    """
    LLM 모델/프로바이더를 관리하고 호출하는 매니저.

    - 기본 프로바이더: Cerebras Cloud (OpenAI Chat Completions 호환)
    - 환경 변수: LLAMA_API_KEY (.env 에서 로드 시도)
    - 모델 확장 가능: register_model / set_default_model
    """

    def __init__(self):
        self._load_env_if_exists()

        # provider -> { 'endpoint': str, 'headers_fn': callable }
        self.providers: Dict[str, Dict] = {
            'cerebras': {
                'chat_completions_url': 'https://api.cerebras.ai/v1/chat/completions',
                'headers_fn': self._cerebras_headers,
            }
        }

        # 등록된 모델들: alias -> { provider, model }
        self.models: Dict[str, Dict[str, str]] = {
            'llama-3.3-70b': { 'provider': 'cerebras', 'model': 'llama-3.3-70b' },
        }

        self.default_model_alias: str = 'llama-3.3-70b'

    # ---------- public APIs ----------
    def register_model(self, alias: str, provider: str, model_name: str):
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        self.models[alias] = { 'provider': provider, 'model': model_name }

    def set_default_model(self, alias: str):
        if alias not in self.models:
            raise ValueError(f"Unknown model alias: {alias}")
        self.default_model_alias = alias

    def chat(self, messages: List[Dict[str, str]], model_alias: Optional[str] = None, temperature: float = 0.2, max_tokens: Optional[int] = None) -> Tuple[bool, str]:
        """
        Chat completion 호출.
        returns: (success, text or error)
        """
        if requests is None:
            return False, "'requests' 라이브러리가 필요합니다. pip install requests 로 설치하세요."

        alias = model_alias or self.default_model_alias
        if alias not in self.models:
            return False, f"모델 별칭을 찾을 수 없습니다: {alias}"

        model_info = self.models[alias]
        provider = model_info['provider']
        model_name = model_info['model']

        if provider == 'cerebras':
            return self._chat_cerebras(messages, model_name, temperature, max_tokens)
        else:
            return False, f"지원되지 않는 프로바이더: {provider}"

    # ---------- providers ----------
    def _chat_cerebras(self, messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: Optional[int]) -> Tuple[bool, str]:
        api_key = os.getenv('LLAMA_API_KEY')
        if not api_key:
            return False, "LLAMA_API_KEY 가 설정되지 않았습니다. 프로젝트 루트의 .env 에 설정해주세요."

        url = self.providers['cerebras']['chat_completions_url']
        headers = self.providers['cerebras']['headers_fn'](api_key)
        payload: Dict = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
        }
        if max_tokens is not None:
            payload['max_tokens'] = max_tokens

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code != 200:
                return False, f"Cerebras API 오류: {resp.status_code} {resp.text}"
            data = resp.json()
            # OpenAI 호환: choices[0].message.content
            content = data.get('choices', [{}])[0].get('message', {}).get('content')
            if not content:
                # 일부 구현은 'text'를 사용
                content = data.get('choices', [{}])[0].get('text')
            if not content:
                return False, f"응답 파싱 실패: {json.dumps(data)[:500]}"
            return True, content
        except Exception as e:
            return False, f"요청 실패: {str(e)}"

    # ---------- helpers ----------
    @staticmethod
    def _cerebras_headers(api_key: str) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }

    def _load_env_if_exists(self):
        """프로젝트 루트의 .env 파일을 간단히 로드 (python-dotenv 없이)."""
        # 현재 파일에서 프로젝트 루트 추정
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        env_path = os.path.join(root, '.env')
        if not os.path.isfile(env_path):
            return
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
        except Exception:
            pass
