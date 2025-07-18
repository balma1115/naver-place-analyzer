# main.py - 간단한 버전으로 새로 작성
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os
import uvicorn
import requests
from bs4 import BeautifulSoup
import re
import json

app = FastAPI(title="네이버 플레이스 분석기", version="2.0.0")

# CORS 설정 - 모든 origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 요청 모델
class PlaceAnalysisRequest(BaseModel):
    url: str = Field(..., example="https://map.naver.com/p/entry/place/1616011574")

class KeywordRankRequest(BaseModel):
    business_name: str = Field(..., example="미래엔영어 벌원학원")
    keywords: List[str] = Field(..., example=["벌원동 영어학원", "탄벌동 수학학원"])

# 기본 엔드포인트들
@app.get("/")
def read_root():
    return {"message": "네이버 플레이스 분석기 백엔드 서버 v2.0", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "서버가 정상적으로 작동 중입니다."}

@app.get("/test")
def test_endpoint():
    return {"message": "테스트 엔드포인트가 정상적으로 작동합니다!", "timestamp": "2024-01-01"}

@app.get("/test-cors")
def test_cors_endpoint():
    return {"message": "CORS test successful!"}

# 간단한 플레이스 정보 추출 (requests + BeautifulSoup 사용)
def extract_place_info(url: str) -> Dict[str, Any]:
    """네이버 플레이스 URL에서 기본 정보를 추출합니다."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 기본 정보 추출
        place_info = {
            "name": "정보 추출 중...",
            "category": "정보 추출 중...",
            "address": "정보 추출 중...",
            "phone": "정보 추출 중...",
            "status": "success",
            "message": "기본 정보 추출 완료"
        }
        
        # 제목 추출 시도
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            place_info["name"] = title_elem.get_text().strip()
        
        # 메타 태그에서 정보 추출
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            place_info["name"] = meta_title.get('content', place_info["name"])
        
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc:
            place_info["description"] = meta_desc.get('content', '설명 없음')
        
        return place_info
        
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"네트워크 오류: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"정보 추출 오류: {str(e)}"
        }

# 키워드 순위 확인 (간단한 버전)
def check_keyword_ranking_simple(business_name: str, keywords: List[str]) -> List[Dict[str, Any]]:
    """키워드 순위를 간단하게 확인합니다."""
    results = []
    
    for keyword in keywords:
        # 실제 검색 대신 시뮬레이션된 결과 반환
        result = {
            "keyword": keyword,
            "business_name": business_name,
            "rank": "시뮬레이션 모드",
            "status": "demo",
            "message": "실제 검색 기능은 개발 중입니다."
        }
        results.append(result)
    
    return results

# API 엔드포인트들
@app.post("/analyze-place")
async def analyze_place_endpoint(request: PlaceAnalysisRequest):
    try:
        print(f"분석 요청 받음: {request.url}")
        result = extract_place_info(request.url)
        return {"status": "success", "data": result}
    except Exception as e:
        print(f"!!! CRITICAL ERROR in /analyze-place: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.post("/check-rankings")
async def check_rankings_endpoint(request: KeywordRankRequest):
    try:
        print(f"키워드 순위 확인 요청 받음: {request.business_name}, {request.keywords}")
        result = check_keyword_ranking_simple(request.business_name, request.keywords)
        return {"status": "success", "data": result}
    except Exception as e:
        print(f"!!! CRITICAL ERROR in /check-rankings: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# 서버 시작
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port: {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, workers=1)