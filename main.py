# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import uvicorn
import asyncio

# 우리가 만든 스크레이퍼 함수들을 가져옵니다.
from scraper import run_place_analysis, run_keyword_ranking_check

app = FastAPI()

# CORS 설정: Netlify의 프론트엔드 주소에서 오는 요청을 허용합니다.
# 일단 모든 주소를 허용하도록 '*'로 설정합니다.
origins = [
    "https://naverplaceranking.netlify.app", # 내 Netlify 앱 주소
    "http://localhost:5173", # 로컬에서 테스트할 때 사용하는 주소 (Vite 기본 포트)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/test-cors")
def test_cors_endpoint():
    return {"message": "CORS test successful!"}


# --- 요청 본문 모델 정의 (프론트엔드에서 보낼 데이터 형식) ---
class PlaceAnalysisRequest(BaseModel):
    url: str = Field(..., example="https://map.naver.com/p/entry/place/1616011574")

class KeywordRankRequest(BaseModel):
    business_name: str = Field(..., example="미래엔영어 벌원학원")
    keywords: List[str] = Field(..., example=["벌원동 영어학원", "탄벌동 수학학원"])

# --- API 엔드포인트 정의 ---
@app.get("/")
def read_root():
    return {"message": "네이버 플레이스 분석기 백엔드 서버입니다."}

# 1. 플레이스 정보 분석 API
@app.post("/analyze-place")
async def analyze_place_endpoint(request: PlaceAnalysisRequest):
    try:
        result = await run_place_analysis(request.url)
        return {"status": "success", "data": result}
    except Exception as e:
        # ◀ 2. 에러를 잡아서 500 상태 코드와 함께 JSON으로 응답합니다.
        print(f"!!! CRITICAL ERROR in /analyze-place: {e}") # Railway 로그에 에러 기록
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
# 2. 키워드 순위 확인 API
@app.post("/check-rankings")
async def check_rankings_endpoint(request: KeywordRankRequest):
    try:
        result = await run_keyword_ranking_check(request.business_name, request.keywords)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 이 파일이 직접 실행될 때 uvicorn 서버를 실행 (로컬 테스트용)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)