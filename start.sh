#!/bin/sh

# === 디버깅을 위한 코드 추가 ===
echo "=================================="
echo "Starting Naver Place Analyzer Backend"
echo "PORT: $PORT"
echo "PYTHONPATH: $PYTHONPATH"
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la
echo "=================================="

# Playwright 브라우저 상태 확인
echo "Checking Playwright installation..."
playwright --version || echo "Playwright not found, installing..."
playwright install --with-deps chromium || echo "Playwright installation failed"

# 서버 시작 (더 안정적인 설정)
echo "Starting uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 75 --log-level info