# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List
import os
import uvicorn
import asyncio

# 우리가 만든 스크레이퍼 함수들을 가져옵니다.
from scraper import run_place_analysis, run_keyword_ranking_check

app = FastAPI(title="네이버 플레이스 분석기", version="1.0.0")

# CORS 설정: 모든 origin 허용 (개발 중에는 이렇게 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=False,  # credentials가 false여야 allow_origins=["*"]와 함께 사용 가능
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/test-cors")
def test_cors_endpoint():
    return {"message": "CORS test successful!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "서버가 정상적으로 작동 중입니다."}

@app.get("/")
def read_root():
    return {"message": "네이버 플레이스 분석기 백엔드 서버입니다."}

@app.get("/test")
def test_endpoint():
    return {"message": "테스트 엔드포인트가 정상적으로 작동합니다!", "timestamp": "2024-01-01"}

# --- 요청 본문 모델 정의 (프론트엔드에서 보낼 데이터 형식) ---
class PlaceAnalysisRequest(BaseModel):
    url: str = Field(..., example="https://map.naver.com/p/entry/place/1616011574")

class KeywordRankRequest(BaseModel):
    business_name: str = Field(..., example="미래엔영어 벌원학원")
    keywords: List[str] = Field(..., example=["벌원동 영어학원", "탄벌동 수학학원"])

# 1. 플레이스 정보 분석 API
@app.post("/analyze-place")
async def analyze_place_endpoint(request: PlaceAnalysisRequest):
    try:
        print(f"분석 요청 받음: {request.url}")  # 로깅 추가
        result = await run_place_analysis(request.url)
        return {"status": "success", "data": result}
    except Exception as e:
        # 에러를 잡아서 500 상태 코드와 함께 JSON으로 응답합니다.
        print(f"!!! CRITICAL ERROR in /analyze-place: {e}") # Railway 로그에 에러 기록
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# 2. 키워드 순위 확인 API
@app.post("/check-rankings")
async def check_rankings_endpoint(request: KeywordRankRequest):
    try:
        print(f"키워드 순위 확인 요청 받음: {request.business_name}, {request.keywords}")  # 로깅 추가
        result = await run_keyword_ranking_check(request.business_name, request.keywords)
        return {"status": "success", "data": result}
    except Exception as e:
        print(f"!!! CRITICAL ERROR in /check-rankings: {e}") # Railway 로그에 에러 기록
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# 이 파일이 직접 실행될 때 uvicorn 서버를 실행 (로컬 테스트용)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port: {port}")  # 디버깅용
    uvicorn.run("main:app", host="0.0.0.0", port=port, workers=1)