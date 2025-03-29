"""
동영상을 GIF로 변환하는 서비스 모듈입니다.

FFmpeg를 사용하여 동영상을 GIF로 변환하고, 임시 파일을 관리합니다.
"""

import logging
import os
import subprocess
import threading
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_video_to_gif(
    input_path, output_path, width=320, fps=10, quality=80, cleanup_delay=60
):
    """
    FFmpeg를 사용하여 동영상을 GIF로 변환합니다.

    Args:
        input_path: 입력 동영상 경로
        output_path: 출력 GIF 경로
        width: GIF의 가로 크기 (높이는 비율에 맞게 자동 조정)
        fps: GIF의 초당 프레임 수
        quality: GIF 품질 (1-100, 높을수록 좋은 품질)
        cleanup_delay: 변환 완료 후 파일 삭제까지 대기 시간(초)

    Returns:
        bool: 변환 성공 여부
    """
    try:
        logger.info(f"변환 시작: {input_path} -> {output_path}")

        # 한 번의 FFmpeg 명령으로 GIF 변환 수행 (단일 프로세스)
        # split 필터를 사용하여 한 번의 스케일링 작업 후 두 개의 스트림으로 분할
        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            input_path,
            "-filter_complex",
            f"fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];"
            f"[s0]palettegen[palette];"
            f"[s1][palette]paletteuse=dither=bayer:bayer_scale=5",
            "-y",
            output_path,
        ]

        # FFmpeg 실행
        process = subprocess.Popen(
            ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            logger.error(f"FFmpeg 오류: {stderr.decode()}")
            return False

        logger.info(f"변환 완료: {output_path}")

        # 파일 크기 로깅
        if os.path.exists(output_path):
            size_kb = os.path.getsize(output_path) / 1024
            logger.info(f"GIF 크기: {size_kb:.2f} KB")

        # 입력 파일 삭제
        if os.path.exists(input_path):
            os.remove(input_path)
            logger.info(f"입력 파일 삭제: {input_path}")

        # 출력 파일 삭제 예약 (별도 스레드에서 실행)
        if cleanup_delay > 0:

            def delayed_cleanup():
                time.sleep(cleanup_delay)
                if os.path.exists(output_path):
                    os.remove(output_path)
                    logger.info(
                        f"출력 파일 삭제: {output_path} (딜레이: {cleanup_delay}초)"
                    )

            cleanup_thread = threading.Thread(target=delayed_cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()

        return True
    except Exception as e:
        logger.error(f"변환 오류: {str(e)}")

        # 오류 발생 시 입력 파일 삭제
        if os.path.exists(input_path):
            os.remove(input_path)

        return False
