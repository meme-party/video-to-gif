"""
동영상을 GIF로 변환하는 웹 애플리케이션의 메인 모듈입니다.

FastAPI를 사용하여 웹 인터페이스를 제공하고, FFmpeg로 동영상을 GIF로 변환합니다.
"""

import os
import tempfile
import time
import uuid

from fastapi import BackgroundTasks, FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# 서비스 임포트
from services.video_conversion import convert_video_to_gif

app = FastAPI(
    title="Video to GIF Converter",
    description="동영상을 GIF로 변환하는 서비스",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정 (도메인 관련)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 오리진 허용 (프로덕션에서는 제한 필요)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 임시 디렉토리 설정
TEMP_DIR = tempfile.gettempdir()

# 정적 파일 서빙을 위한 설정 - HTML만 서빙하도록 변경
app.mount("/static", StaticFiles(directory="static"), name="static")

# GIF 캐시 저장소 (메모리 내 임시 저장)
gif_cache = {}


@app.post(
    "/convert/",
    summary="동영상을 GIF로 변환",
    description="동영상 파일을 업로드하여 GIF로 변환합니다. 생성된 GIF는 5분 후 자동으로 삭제됩니다.",
)
async def convert_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    width: int = 320,
    fps: int = 10,
    max_size_mb: int = 50,
):
    """
    동영상 파일을 업로드하여 GIF로 변환합니다.

    Args:
        background_tasks: 백그라운드 작업을 위한 객체
        video: 업로드된 동영상 파일
        width: GIF의 가로 너비 (픽셀)
        fps: GIF의 초당 프레임 수
        max_size_mb: 최대 허용 파일 크기 (MB)

    Returns:
        변환 작업 상태 및 GIF ID 정보
    """
    # 파일 크기 검사
    content = await video.read()
    file_size = len(content)

    if file_size > max_size_mb * 1024 * 1024:
        return {"error": f"파일 크기가 {max_size_mb}MB를 초과합니다."}

    # 임시 파일 생성
    file_id = str(uuid.uuid4())
    input_filename = f"{file_id}_{video.filename.replace(' ', '_')}"
    output_filename = f"{file_id}.gif"

    input_path = os.path.join(TEMP_DIR, input_filename)
    output_path = os.path.join(TEMP_DIR, output_filename)

    # 임시 파일에 업로드된 콘텐츠 저장
    with open(input_path, "wb") as buffer:
        buffer.write(content)

    # 변환 작업 백그라운드로 실행
    background_tasks.add_task(
        convert_video_to_gif,
        input_path,
        output_path,
        width,
        fps,
        cleanup_delay=300,  # 5분 후 자동 삭제
    )

    # GIF 캐시에 메타데이터 저장
    gif_cache[file_id] = {
        "path": output_path,
        "created_at": time.time(),
        "expires_at": time.time() + 300,  # 5분 후 만료
    }

    return {
        "message": "변환 작업이 시작되었습니다.",
        "gif_id": file_id,
        "status": "processing",
    }


@app.get(
    "/gif/{file_id}",
    summary="변환된 GIF 조회",
    description="변환된 GIF를 브라우저에서 볼 수 있습니다.",
)
async def get_gif(file_id: str):
    """
    변환된 GIF를 브라우저에서 볼 수 있습니다.

    Args:
        file_id: GIF 파일의 고유 ID

    Returns:
        GIF 파일 스트림 또는 오류 메시지
    """
    # 캐시에서 GIF 정보 확인
    if file_id not in gif_cache:
        return {"error": "요청한 GIF를 찾을 수 없습니다."}

    gif_info = gif_cache[file_id]
    file_path = gif_info["path"]

    # 파일 존재 확인
    if not os.path.exists(file_path):
        return {"error": "GIF 파일이 아직 생성되지 않았거나 만료되었습니다."}

    # 파일 스트리밍으로 반환 (다운로드 후 삭제되지 않도록)
    def iterfile():
        with open(file_path, mode="rb") as file_like:
            yield from file_like

    # 파일 반환 (Content-Disposition 헤더 추가하지 않음 - 다운로드 안됨)
    return StreamingResponse(iterfile(), media_type="image/gif")


@app.get(
    "/download/{file_id}",
    summary="변환된 GIF 다운로드",
    description="변환된 GIF를 다운로드할 수 있습니다.",
)
async def download_gif(file_id: str):
    """
    변환된 GIF를 다운로드할 수 있습니다.

    Args:
        file_id: GIF 파일의 고유 ID

    Returns:
        다운로드 가능한 GIF 파일 또는 오류 메시지
    """
    # 캐시에서 GIF 정보 확인
    if file_id not in gif_cache:
        return {"error": "요청한 GIF를 찾을 수 없습니다."}

    gif_info = gif_cache[file_id]
    file_path = gif_info["path"]

    # 파일 존재 확인
    if not os.path.exists(file_path):
        return {"error": "GIF 파일이 아직 생성되지 않았거나 만료되었습니다."}

    # 다운로드를 위한 응답 생성
    return FileResponse(
        file_path, media_type="image/gif", filename=f"converted_{file_id}.gif"
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    """메인 페이지를 반환합니다."""
    with open("static/index.html", "r") as f:
        return f.read()


@app.get(
    "/health",
    summary="헬스체크",
    description="서비스 상태 확인을 위한 헬스체크 엔드포인트",
)
def health_check():
    """서비스 상태를 확인합니다."""
    return {"status": "ok", "timestamp": time.time()}


# 주기적으로 만료된 캐시 항목 정리 (실제 환경에서는 백그라운드 태스크로 구현)
@app.middleware("http")
async def cleanup_expired_cache(request: Request, call_next):
    """만료된 GIF 캐시 항목을 정리합니다."""
    # 현재 시간
    current_time = time.time()

    # 만료된 캐시 항목 찾기
    expired_keys = []
    for key, info in gif_cache.items():
        if current_time > info["expires_at"]:
            expired_keys.append(key)

    # 만료된 항목 삭제
    for key in expired_keys:
        if key in gif_cache:
            del gif_cache[key]

    response = await call_next(request)
    return response
