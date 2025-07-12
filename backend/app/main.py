from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.api import api_router
from app.database import init_db, check_db_connection
import logging

# 로깅 설정
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    debug=settings.debug
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(api_router, prefix=settings.api_v1_str)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    try:
        # 데이터베이스 초기화
        init_db()
        logger.info("Database initialized successfully")
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Crypto Graves API",
        "version": "1.0.0",
        "docs": f"{settings.api_v1_str}/docs"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    db_status = "connected" if check_db_connection() else "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": "2024-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.server_host, port=settings.server_port) 