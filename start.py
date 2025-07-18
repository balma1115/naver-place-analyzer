#!/usr/bin/env python3
"""
Railway 배포용 시작 스크립트
"""
import os
import uvicorn
from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port: {port}")
    print(f"Environment: PORT={os.environ.get('PORT', 'not set')}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 