"""
동영상을 GIF로 변환하는 서비스 모듈입니다.

FFmpeg를 사용하여 동영상을 GIF로 변환하고, 임시 파일을 관리합니다.
"""

import logging
import os
import threading
import time

import ffmpeg

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_video_to_gif(input_path, output_path, width=320, fps=10, cleanup_delay=60):
    """
    FFmpeg를 사용하여 동영상을 GIF로 변환합니다.

    Args:
        input_path: 입력 동영상 경로
        output_path: 출력 GIF 경로
        width: GIF의 가로 크기 (높이는 비율에 맞게 자동 조정)
        fps: GIF의 초당 프레임 수
        cleanup_delay: 변환 완료 후 파일 삭제까지 대기 시간(초)

    Returns:
        bool: 변환 성공 여부
    """
    try:
        logger.info(f"변환 시작: {input_path} -> {output_path}")

        # FFmpeg 변환 명령
        (
            ffmpeg.input(input_path)
            .filter("fps", fps=fps)
            .filter("scale", width=width, height=-1)
            .output(output_path)
            .run(capture_stdout=True, capture_stderr=True)
        )

        logger.info(f"변환 완료: {output_path}")

        # 입력 파일 즉시 삭제
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
    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if hasattr(e, "stderr") else str(e)
        logger.error(f"FFmpeg 오류: {error_message}")

        # 오류 발생 시 입력 파일 삭제
        if os.path.exists(input_path):
            os.remove(input_path)

        return False
    except Exception as e:
        logger.error(f"변환 오류: {str(e)}")

        # 오류 발생 시 입력 파일 삭제
        if os.path.exists(input_path):
            os.remove(input_path)

        return False
