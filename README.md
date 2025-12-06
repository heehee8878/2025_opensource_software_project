![header](https://capsule-render.vercel.app/api?type=waving&color=auto&height=301&section=header&text=[%20Blue%20Dot%20Code%20]&fontSize=60&desc=24101183%20김강민&descSize=15)

> Python PyQt5 라이브러리를 사용해 개발한 AI Agent기능이 탑재된 Code Editor입니다.

## 🔧 사용 언어
![](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 💼 사용 프레임워크
 - PyQt5

## ⚙️ 사용 api
- Cerebras Cloud (llama-3.3-70B, gpt-oss-120b)

## 🏗️ 구조
- **Editor Window (editor_window.py)**
    - 에디터를 위한 메인 윈도우를 구성하며, PyQt5 기반의 GUI 애플리케이션입니다.
    - UI 파일(editor.ui)을 로드하여 인터페이스를 구성하고, 모든 매니저 클래스들을 초기화 및 통합합니다.
    - 파일 트리 뷰, 코드 편집기, 터미널 출력, AI 에이전트 프롬프트 입력창 등 주요 UI 컴포넌트들의 이벤트 핸들링을 담당합니다.
    - 핫키(Ctrl+O, Ctrl+S, Ctrl+Q) 설정 및 사용자 인터랙션(파일 열기/저장, 우클릭 메뉴, 터미널 명령 실행 등)을 처리합니다.
    - 상태 관리: 현재 열린 폴더 경로(opened_folder_path), 파일 경로(opened_file_path), 파일명(opened_file_name)을 추적합니다.
    - 마크다운을 HTML로 변환하여 AI 에이전트의 응답을 스타일링된 형태로 표시합니다(markdown 라이브러리 사용).

- **File Manager (file_manager.py)**
    - 파일 시스템 작업을 캡슐화하여 파일 및 폴더 관리를 담당합니다.
    - 폴더 트리 로드: os.walk()를 사용해 디렉토리 구조를 순회하고, QTreeWidget에 계층 구조를 구축합니다. 폴더는 "📁" 아이콘과 함께 표시됩니다.
    - 파일 읽기/쓰기: UTF-8 인코딩으로 파일 내용을 읽고 저장하며, 예외 처리를 통해 오류 메시지를 반환합니다.
    - 경로 추적: QTreeWidgetItem의 부모-자식 관계를 역추적하여 전체 파일 경로를 재구성합니다(get_file_path_from_item).
    - CRUD 작업: 새 파일/폴더 생성(create_file, create_folder) 및 삭제(delete_item) 기능을 제공합니다.
    - 내부적으로 item_map 딕셔너리를 사용해 경로와 QTreeWidgetItem 간의 매핑을 유지합니다.

- **Terminal Manager (terminal_manager.py)**
    - 에디터에 내장된 터미널의 프로세스 관리 및 실행을 담당합니다.
    - 플랫폼별 셸 실행: Windows에서는 PowerShell을, macOS/Linux에서는 zsh 또는 bash를 실행합니다. PTY 에뮬레이션을 위해 Unix 계열에서는 script 명령을 활용합니다.
    - 지속형 세션: QProcess를 사용해 백그라운드에서 셸 프로세스를 유지하며, 명령 실행 간 상태(환경 변수, 작업 디렉토리)를 보존합니다.
    - 입출력 처리: readyReadStandardOutput/readyReadStandardError 시그널을 통해 실시간으로 출력을 수신하고, output_received 시그널로 UI에 전달합니다.
    - 출력 정제: ANSI 이스케이프 시퀀스(OSC, CSI, ESC)를 정규표현식으로 제거하여 깔끔한 텍스트 출력을 제공합니다(_sanitize_output).
    - 디렉토리 관리: cd 명령 처리 및 작업 디렉토리 동기화를 지원하며, 프로세스가 종료된 경우 자동 재시작 기능(ensure_running)을 제공합니다.
    - 에러 및 종료 상태를 추적하여 안정적인 터미널 환경을 유지합니다.

- **Agent Manager (agent_manager.py)**
    - AI 기반 코드 리팩토링 및 버그 수정을 위한 에이전트 로직을 담당합니다.
    - 프롬프트 엔지니어링: 파일 경로, 언어, 원본 코드를 포함한 상세한 시스템/사용자 메시지를 구성하여 LLM에 전달합니다.
    - 응답 파싱: 미리 정의된 마커(<<BEGIN_FILE>>, <<END_FILE>>, <<BEGIN_DESC>>, <<END_DESC>>)를 사용해 LLM 응답에서 코드와 설명을 정확히 추출합니다.
    - 언어 추론: 파일 확장자를 기반으로 프로그래밍 언어를 자동 감지합니다(.py → Python, .js → JavaScript 등).
    - 오류 처리: 마커가 없을 경우 백틱(```)으로 감싸진 코드 블록을 대체 추출하며, 실패 시 빈 문자열을 반환합니다.
    - Model Manager와 연동하여 chat() 메서드를 호출하고, 응답을 구조화된 형태로 반환합니다(run 메서드).

- **Model Manager (model_manager.py)**
    - LLM API 통합 및 모델 라이프사이클을 관리합니다.
    - 프로바이더 지원: Cerebras Cloud API를 기본 프로바이더로 사용하며, OpenAI Chat Completions 호환 방식으로 통신합니다.
    - 모델 등록 시스템: 여러 모델을 alias로 등록하고 관리할 수 있습니다(register_model). 기본적으로 llama-3.3-70b와 gpt-oss-120b 모델을 지원합니다.
    - 환경 변수 로딩: 프로젝트 루트의 .env 파일에서 LLAMA_API_KEY를 로드합니다(_load_env_if_exists). python-dotenv 라이브러리 없이 직접 파싱합니다.
    - Chat Completion API: requests 라이브러리를 사용해 HTTP POST 요청을 전송하며, temperature와 max_tokens 파라미터를 지원합니다.
    - 에러 핸들링: API 호출 실패 시 상세한 오류 메시지를 반환하며, 환경 변수 미설정, 네트워크 오류, 응답 파싱 실패 등을 처리합니다.
    - 확장성: 새로운 프로바이더 추가를 위한 구조화된 딕셔너리(providers)와 헤더 생성 함수(_cerebras_headers)를 제공합니다.

## 📖 "AI Code Editor" 사용법

우측 패널에서 프롬프트를 작성하고 생성 버튼(✦)을 누르면 현재 열린 파일의 전체 내용을 특정 포맷으로 LLM에 전달하여 받은 응답으로 파일을 수정합니다.


##### 1) 의존성 설치

```bash
# Windows
pip install -r requirements.txt
```
```bash
# MacOS
pip3 install -r requirements.txt
```

##### 2) 환경 변수 설정

프로젝트 루트에 `.env` 파일을 만들고 다음 값을 넣어주세요.

```
LLAMA_API_KEY={your_cerebras_api_key}
```

##### 3) 실행

```bash
# Windows
python main.py
```
```bash
# MacOS
python3 main.py
```


## ⚡ 앱 실행 시연

##### 1) 앱 실행하기
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/bccc1c37-03f6-49c5-be86-6d8d697afe5b" />

> 앱 실행 시 다음과 같은 화면이 보입니다. "폴더 열기"버튼을 통해서 로컬 작업 환경을 설정할 수 있습니다.

##### 2) 작업 환경 시작하기
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/d5f53f81-abcc-456d-a33c-d430d09ba699" />

> 폴더를 열면 해당 폴더 경로에서 터미널이 시작되는것을 확인할 수 있습니다. 해당 터미널 도구로 다양한 기능을 수행 가능합니다.

##### 3) 파일 편집 시작하기
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/3ee89f54-5f74-49e6-a1ad-16d7a5bc9312" />

> 작업 환경 설정 이후 해당 폴더 내의 파일을 선택하면 사진과 같이 파일 편집이 가능합니다.

##### 4) 코드 입력하기
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/c53c796b-c554-4a93-b4f3-4e1a059f2390" />

> test.py파일에 간단한 코드를 적어봅니다.

##### 5) 저장하기
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/7d4c9d79-4559-47d2-aa91-a3478f2fff53" />

> "File > Save" 또는 "Ctrl + S" 단축키를 통해서 파일 저장이 가능합니다.

##### 6) 파일 실행하기
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/22053b70-54d0-4224-bd8e-36ae1c0eab80" />

> 터미널에서 "python test.py"코드를 실행해 Python 코드를 실행시킨 화면입니다.

##### 7) Agent 모델 선택하기
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/94cf6407-576e-442f-856a-7a856e64a765" />

> 우측 Code Agent 패널 하단의 콤보 박스를 통해 LLM 모델을 선택할 수 있습니다.

##### 8) 프롬프트 입력하기
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/479567b5-19fc-44c3-abb8-9438d1bc22c2" />

> 프롬프트 입력 인풋에 다양한 프롬프트를 입력 가능합니다. 프롬프트의 결과물은 현재 선택된 파일에 영향을 줍니다.

##### 9) 결과 확인하기
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/31adb62d-7be8-40d1-9eba-485595ca0d89" />

> 선택된 파일에는 결과 코드가, Code Agent 패널 설명란에는 해당 코드에 대한 설명을 보여줍니다.

##### 10) 파일 실행하기
<img width="138" height="66" alt="Image" src="https://github.com/user-attachments/assets/dd743c7a-743f-4862-95bc-3d4f7774a987" />
<img width="802" height="466" alt="Image" src="https://github.com/user-attachments/assets/2fd3757c-7ab4-488a-ac31-7b7919d7a0c5" />

> 파일 저장 후 "python test.py" 명령어를 실행해주면 이와 같은 결과물을 볼 수 있습니다.

##### 11) 다양한 옵션
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/2d11a617-3cea-4cb0-8194-bdf59321e05f" />

> 작업환경 내의 폴더 및 파일을 오른쪽 마우스로 클릭하면 다양한 옵션을 활용할 수 있습니다.

<img width="202" height="121" alt="Image" src="https://github.com/user-attachments/assets/16b9d975-b524-4ee0-945d-5568202dc1b7" />

> 파일 추가

##### 13) 다양한 활용 (시)
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/472442d0-81d6-40ea-bbc8-e30732e24542" />

> python 코드 이외에도 다양한 작업을 Code Agent를 통해 효율적으로 진행할 수 있습니다. 위는 Agent를 통해 간단한 시를 생성한 예시입니다.

##### 14) 다양한 활용 (html)
<img width="1458" height="860" alt="Image" src="https://github.com/user-attachments/assets/85306a77-1dfb-4425-a9cb-f79ca856e862" />

> html코드도 위와 같이 실행 가능하며, 상당히 높은 수준의 결과를 보여줍니다.

<img width="1609" height="991" alt="Image" src="https://github.com/user-attachments/assets/5969ebc9-17fd-4edc-8165-4c5a7634168a" />


## 아이콘

<img width="176" height="176" alt="Image" src="https://github.com/user-attachments/assets/9707181d-cd08-42f7-9755-87e0595765e4" /></br>
