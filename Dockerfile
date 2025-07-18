FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 업데이트
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 포트 노출 (Railway가 자동으로 설정)
EXPOSE 8000

# 헬스체크 (더 관대한 설정)
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# 서버 실행
CMD ["python", "main.py"]