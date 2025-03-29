#!/bin/bash

# 코드 포맷팅 실행
poetry run black app
poetry run isort app
