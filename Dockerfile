# Dockerfile

# 1. 베이스 이미지 선택
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 시스템 패키지 업데이트
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. requirements.txt 복사 및 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Playwright 브라우저 설치
RUN playwright install --with-deps chromium

# 6. 프로젝트 소스 코드 복사
COPY . .

# 7. 시작 스크립트 실행 권한 부여
RUN chmod +x /app/start.sh

# 8. 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# 9. 포트 노출
EXPOSE 8080

# 10. 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# 11. 스크립트를 통해 서버 실행
CMD ["/app/start.sh"]