![header](https://capsule-render.vercel.app/api?type=waving&color=auto&height=301&section=header&text=[%20AI%20Code%20Editor%20]&fontSize=60&desc=24101183%20김강민&descSize=15)

### 🔧 사용 언어
![](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

### 💼 사용 프레임워크
 - PyQt5

### ⚙️ 사용 api
- Cerebras Cloud (Llama-3.3-70B)

### 📖 "AI Code Editor" 사용법

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