# Dockerfile
# 1. 베이스 이미지 선택 (Playwright가 필요한 라이브러리 포함)
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. requirements.txt 복사 및 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Playwright 브라우저 설치
RUN playwright install --with-deps

# 5. 프로젝트 소스 코드 복사
COPY . .

# 6. 서버 실행 명령어 (Railway가 이 명령어를 사용)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]