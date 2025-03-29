"""
애플리케이션 설정 모듈입니다.

환경 변수와 기본값을 기반으로 설정을 관리합니다.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 클래스."""

    APP_NAME: str = "동영상 GIF 변환기"
    APP_VERSION: str = "0.1.0"

    # 파일 크기 제한 (MB)
    MAX_UPLOAD_SIZE_MB: int = 50

    # 변환 설정 기본값
    DEFAULT_GIF_WIDTH: int = 320
    DEFAULT_GIF_FPS: int = 10

    # 파일 저장 위치
    UPLOAD_DIR: str = "static/uploads"
    OUTPUT_DIR: str = "static/outputs"

    # 도메인 설정
    APP_DOMAIN: str = "video-to-fig.memez.party"

    class Config:
        """설정 클래스의 메타 설정."""

        env_file = ".env"


settings = Settings()
