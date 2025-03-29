# 동영상 GIF 변환기

동영상 파일을 GIF 애니메이션으로 변환하는 웹 애플리케이션입니다. 이 프로젝트는 FastAPI와 FFmpeg를 사용하여 개발되었습니다.

## 특징

- 동영상 파일 업로드 및 GIF로 변환
- 출력 GIF의 너비 및 FPS 설정
- 모바일 친화적인 반응형 UI
- 쿠버네티스 배포 지원
- **서버에 파일이 영구 저장되지 않음** (임시 파일 사용 및 자동 삭제)

## 기술 스택

- **백엔드**: FastAPI (Python)
- **동영상 처리**: FFmpeg
- **프론트엔드**: HTML, CSS, JavaScript
- **패키지 관리**: Poetry
- **컨테이너화**: Docker
- **오케스트레이션**: Kubernetes

## 로컬 개발 환경 설정

### 필수 요구 사항

- Python 3.13
- Poetry
- FFmpeg

### 설치 및 실행 방법

1. 저장소 클론:
```bash
git clone https://github.com/yourusername/video-to-gif.git
cd video-to-gif
```

2. Poetry로 의존성 설치:
```bash
poetry install
```

3. FFmpeg 설치:
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: [FFmpeg 공식 사이트](https://ffmpeg.org/download.html)에서 다운로드

4. 애플리케이션 실행:
```bash
# 직접 실행
cd app
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8083

# 또는 스크립트 사용
./scripts/run-dev.sh
```

5. 브라우저에서 `http://localhost:8083` 접속

### Docker를 사용한 실행

```bash
docker-compose up --build
```

## 파일 처리 방식

이 애플리케이션은 서버에 파일을 영구적으로 저장하지 않습니다:

1. **업로드된 동영상**: 임시 디렉토리에 저장되며, GIF 변환 완료 즉시 삭제됩니다.
2. **변환된 GIF**: 임시 디렉토리에 저장되며, 5분 후 자동으로 삭제됩니다.
3. **메모리 기반 캐시**: 변환된 GIF의 메타데이터는 메모리 내 캐시에 저장되고 주기적으로 정리됩니다.

이 방식은 서버 디스크 공간을 효율적으로 사용하며, 더 이상 필요하지 않은 파일이 서버에 남지 않도록 합니다.

## 쿠버네티스 배포

1. 환경에 맞게 k8s 디렉토리의 매니페스트 파일 수정

2. cert-manager 설정 (HTTPS 인증서 자동 발급)
```bash
# cert-manager가 설치되지 않은 경우
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# 이메일 주소 수정 필요
kubectl apply -f k8s/cert-manager-issuer.yaml
```

3. 매니페스트 적용:
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

4. 또는 Skaffold를 사용한 배포:
```bash
skaffold run -p prod
```

## 도메인 설정

애플리케이션은 다음 도메인으로 접속할 수 있습니다:
- 프로덕션: https://video-to-gif.memez.party

## API 문서

FastAPI에서 자동 생성된 API 문서는 다음 URL에서 확인할 수 있습니다:
- Swagger UI: `https://video-to-gif.memez.party/docs`
- ReDoc: `https://video-to-gif.memez.party/redoc`

## 주요 API 엔드포인트

- `POST /convert/`: 동영상 업로드 및 GIF 변환
- `GET /gif/{file_id}`: 변환된 GIF 조회
- `GET /download/{file_id}`: 변환된 GIF 다운로드
- `GET /health`: 헬스체크 엔드포인트

## 라이센스

MIT

## 기여 방법

1. 이 저장소를 포크합니다.
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경 사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.
