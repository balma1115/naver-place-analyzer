# Dockerfile

# 1. 베이스 이미지 선택
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. requirements.txt 복사 및 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Playwright 브라우저 설치
RUN playwright install --with-deps chromium

# 5. 프로젝트 소스 코드 복사
COPY . .

# 6. 시작 스크립트 실행 권한 부여
RUN chmod +x /app/start.sh

# 7. 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 8. 포트 노출
EXPOSE 8080

# 9. 스크립트를 통해 서버 실행
CMD ["/app/start.sh"]