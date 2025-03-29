# Poetry 설정 가이드

이 프로젝트는 의존성 관리를 위해 Poetry를 사용합니다. 다음은 Poetry를 설치하고 프로젝트를 설정하는 방법입니다.

## Poetry 설치

### macOS / Linux / WSL:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Windows PowerShell:
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

## PATH에 Poetry 추가
설치 후, Poetry를 PATH에 추가해야 합니다:

### macOS / Linux / WSL:
```bash
export PATH="$HOME/.local/bin:$PATH"
```
`.bashrc` 또는 `.zshrc` 파일에 위 라인을 추가하는 것이 좋습니다.

### Windows:
Poetry는 자동으로 PATH에 추가됩니다. 만약 작동하지 않는다면, `%APPDATA%\Python\Scripts`를 환경 변수 PATH에 추가하세요.

## 의존성 설치

```bash
# 프로젝트 디렉토리로 이동
cd /Users/koa/projects/video-to-gif

# 의존성 설치
poetry install
```

## 가상 환경 활성화

```bash
# Poetry가 생성한 가상 환경 활성화
poetry shell

# 또는 명령 실행시에만 가상 환경 사용
poetry run python app/main.py
```

## Poetry 기본 명령어

```bash
# 패키지 추가
poetry add fastapi

# 개발용 패키지 추가
poetry add --dev pytest

# 패키지 업데이트
poetry update

# 현재 설치된 패키지 목록 확인
poetry show

# 의존성 잠금 파일 생성/업데이트
poetry lock
```

## 자세한 정보

자세한 내용은 [Poetry 공식 문서](https://python-poetry.org/docs/)를 참조하세요.
