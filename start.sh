#!/bin/sh

# === 디버깅을 위한 코드 추가 ===
echo "=================================="
echo "Attempting to start server on PORT: $PORT"
echo "=================================="
# ===============================

uvicorn main:app --host 0.0.0.0 --port $PORT