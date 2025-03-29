#!/bin/bash
# build-docker.sh

set -e

# 기본 이미지 정보 설정
REPOSITORY="memezparty/video-to-gif"
GIT_HASH=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d%H%M%S)
TAG="${GIT_HASH}-${TIMESTAMP}"

# 환경변수 기반 태그 설정 (CI 환경 지원)
if [ ! -z "$INPUT_TAG" ]; then
  TAG="$INPUT_TAG"
elif [ ! -z "$GITHUB_REF" ]; then
  if [[ $GITHUB_REF == refs/tags/* ]]; then
    TAG=${GITHUB_REF#refs/tags/}
  elif [[ $GITHUB_REF == refs/heads/main ]]; then
    TAG="latest"
  fi
fi

# 이미지 태그 생성
IMAGE_NAME="${REPOSITORY}:${TAG}"
LATEST_IMAGE="${REPOSITORY}:latest"

echo "Building Docker image: ${IMAGE_NAME}"
docker build -t ${IMAGE_NAME} -t ${LATEST_IMAGE} .

# 이미지 푸시 여부 확인
if [ "$1" = "--push" ]; then
  echo "Pushing Docker image to DockerHub: ${IMAGE_NAME}"
  docker push ${IMAGE_NAME}

  if [ "$TAG" != "latest" ]; then
    echo "Pushing Docker image to DockerHub: ${LATEST_IMAGE}"
    docker push ${LATEST_IMAGE}
  fi
fi

echo "Docker build process completed successfully!"
