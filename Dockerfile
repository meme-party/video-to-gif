FROM python:3.13-slim

# 기본 환경 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1

# 필수 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ffmpeg \
    gifsicle \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install "poetry==${POETRY_VERSION}"

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설정: 가상 환경 생성하지 않음
RUN poetry config virtualenvs.create false

# 의존성 파일 복사 및 설치
COPY pyproject.toml ./
RUN poetry install --without dev

# 기본 정적 파일만 복사
COPY ./app/static/index.html /app/static/

# 애플리케이션 코드 복사
COPY ./app/*.py /app/
COPY ./app/api /app/api/
COPY ./app/core /app/core/
COPY ./app/services /app/services/

# 포트 설정
EXPOSE 8083

# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8083"]
