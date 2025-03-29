"""
동영상 변환 API 엔드포인트 모듈입니다.

이 모듈은 API 라우터를 정의하고 동영상 변환 서비스를 호출합니다.
"""

import os
import uuid

from core.config import settings
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from services.video_conversion import convert_video_to_gif

router = APIRouter()


@router.post("/", summary="동영상을 GIF로 변환")
async def convert_video_endpoint(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    width: int = settings.DEFAULT_GIF_WIDTH,
    fps: int = settings.DEFAULT_GIF_FPS,
):
    """
    동영상 파일을 업로드하여 GIF로 변환합니다.

    Args:
        background_tasks: 백그라운드 작업을 위한 객체
        video: 변환할 동영상 파일
        width: 출력 GIF의 너비 (픽셀)
        fps: 출력 GIF의 초당 프레임 수

    Returns:
        변환된 GIF 파일의 URL

    Raises:
        HTTPException: 파일 형식이나 크기가 잘못된 경우
    """
    # 파일 확장자 확인
    if not video.filename.lower().endswith((".mp4", ".avi", ".mov", ".wmv", ".mkv")):
        raise HTTPException(
            status_code=400,
            detail="지원되지 않는 파일 형식입니다. MP4, AVI, MOV, WMV, MKV 형식만 지원합니다.",
        )

    # 파일 저장
    file_id = str(uuid.uuid4())
    safe_filename = video.filename.replace(" ", "_")
    input_path = f"{settings.UPLOAD_DIR}/{file_id}_{safe_filename}"
    output_path = f"{settings.OUTPUT_DIR}/{file_id}.gif"

    content = await video.read()
    file_size = len(content)

    # 파일 크기 검사
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 {settings.MAX_UPLOAD_SIZE_MB}MB를 초과합니다.",
        )

    # 디렉토리 확인
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

    # 파일 저장
    with open(input_path, "wb") as buffer:
        buffer.write(content)

    # 변환 작업 백그라운드로 실행
    background_tasks.add_task(
        convert_video_to_gif,
        input_path,
        output_path,
        width,
        fps,
    )

    return {
        "message": "변환 작업이 시작되었습니다.",
        "gif_url": f"/static/outputs/{file_id}.gif",
        "status": "processing",
    }
