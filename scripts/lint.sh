#!/bin/bash

# 코드 린팅 실행
poetry run flake8 app
poetry run mypy app
