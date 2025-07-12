# Data models for Crypto Graves
# 이 패키지는 Crypto Graves 프로젝트의 모든 데이터 모델을 포함합니다.

from .user import UserModel, User, UserCreate, UserUpdate, UserRole
from .loss import LossModel, Loss, LossCreate, LossUpdate, LossStatus

# 외부에서 import할 수 있는 모델들
__all__ = [
    # User 관련 모델들
    "UserModel",      # SQLAlchemy 사용자 모델 (데이터베이스 테이블과 매핑)
    "User",           # Pydantic 사용자 응답 모델 (API 응답용)
    "UserCreate",     # Pydantic 사용자 생성 모델 (API 요청용)
    "UserUpdate",     # Pydantic 사용자 업데이트 모델 (API 요청용)
    "UserRole",       # 사용자 역할 Enum
    
    # Loss 관련 모델들
    "LossModel",      # SQLAlchemy 손실 데이터 모델 (데이터베이스 테이블과 매핑)
    "Loss",           # Pydantic 손실 데이터 응답 모델 (API 응답용)
    "LossCreate",     # Pydantic 손실 데이터 생성 모델 (API 요청용)
    "LossUpdate",     # Pydantic 손실 데이터 업데이트 모델 (API 요청용)
    "LossStatus",     # 손실 데이터 상태 Enum
] 