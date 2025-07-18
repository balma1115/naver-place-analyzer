#!/bin/sh

# === 디버깅을 위한 코드 추가 ===
echo "=================================="
echo "Starting Naver Place Analyzer Backend"
echo "PORT: $PORT"
echo "PYTHONPATH: $PYTHONPATH"
echo "=================================="

# Playwright 브라우저 상태 확인
echo "Checking Playwright installation..."
playwright --version

# 서버 시작
echo "Starting uvicorn server..."
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 75