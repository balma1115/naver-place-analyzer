from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import os
import signal
import sys

# FastAPI 앱 생성
app = FastAPI(
    title="네이버 플레이스 분석기",
    description="간단하고 안정적인 네이버 플레이스 분석 API",
    version="1.0.0"
)

# CORS 미들웨어 설정 - 모든 origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 요청 모델
class PlaceRequest(BaseModel):
    url: str

class KeywordRequest(BaseModel):
    business_name: str
    keywords: List[str]

# 기본 엔드포인트
@app.get("/")
async def root():
    return {"message": "네이버 플레이스 분석기 API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "서버 정상 작동"}

@app.get("/test")
async def test():
    return {"message": "테스트 성공", "data": "서버가 정상적으로 응답합니다"}

# 플레이스 분석 엔드포인트
@app.post("/analyze-place")
async def analyze_place(request: PlaceRequest):
    try:
        # 간단한 응답 (실제 스크래핑은 나중에 구현)
        return {
            "status": "success",
            "data": {
                "name": "테스트 업체명",
                "category": "교육",
                "address": "서울시 강남구",
                "phone": "02-1234-5678",
                "message": "기본 정보 추출 완료"
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 키워드 순위 확인 엔드포인트
@app.post("/check-rankings")
async def check_rankings(request: KeywordRequest):
    try:
        results = []
        for keyword in request.keywords:
            results.append({
                "keyword": keyword,
                "business_name": request.business_name,
                "rank": "테스트 모드",
                "status": "demo"
            })
        
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 시그널 핸들러 추가
def signal_handler(sig, frame):
    print("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 서버 시작 - Railway 환경에 맞게 수정
if __name__ == "__main__":
    # Railway는 PORT 환경변수를 자동으로 설정합니다 (보통 8080)
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port: {port}")
    print(f"Environment: PORT={os.environ.get('PORT', 'not set')}")
    
    # Railway에서 안정적으로 작동하도록 설정
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port,
        log_level="info",
        access_log=True
    )