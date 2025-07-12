from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class UserRole(str, Enum):
    """사용자 역할 Enum"""
    USER = "user"           # 일반 사용자
    ADMIN = "admin"         # 관리자
    MODERATOR = "moderator" # 중재자


# SQLAlchemy ORM Model (데이터베이스 테이블과 매핑되는 모델)
class UserModel(Base):
    """사용자 정보 테이블 모델"""
    __tablename__ = "users"
    
    # 기본 식별자
    id = Column(Integer, primary_key=True, index=True)                    # 사용자 고유 ID (자동 증가)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)  # 보안용 UUID
    
    # 지갑 정보
    wallet_address = Column(String(42), unique=True, nullable=False, index=True)  # 이더리움 지갑 주소
    
    # 사용자 정보
    username = Column(String(100), nullable=True)                        # 사용자명 (선택사항)
    email = Column(String(255), nullable=True)                          # 이메일 (선택사항)
    role = Column(String(20), default=UserRole.USER.value)              # 사용자 역할 (user/admin/moderator)
    
    # 손익 정보
    total_loss = Column(Numeric(20, 8), default=0.0)                    # 총 손실 금액 (MON 기준, 소수점 8자리)
    total_gain = Column(Numeric(20, 8), default=0.0)                    # 총 수익 금액 (MON 기준, 소수점 8자리)
    
    # 프로필 정보
    profile_image_url = Column(Text, nullable=True)                      # 프로필 이미지 URL
    bio = Column(Text, nullable=True)                                   # 사용자 소개글
    
    # 계정 상태
    is_active = Column(Boolean, default=True)                           # 계정 활성화 상태
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())      # 계정 생성 시간
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # 정보 수정 시간


# Pydantic Models (API 요청/응답 데이터 검증용)
class UserBase(BaseModel):
    """사용자 기본 정보 (API 요청용)"""
    wallet_address: str = Field(..., description="사용자 지갑 주소 (이더리움 주소)")
    username: Optional[str] = Field(None, description="사용자명 (선택사항)")
    email: Optional[str] = Field(None, description="이메일 (선택사항)")


class UserCreate(UserBase):
    """새 사용자 생성 요청 모델"""
    pass


class UserUpdate(BaseModel):
    """사용자 정보 업데이트 요청 모델"""
    username: Optional[str] = None              # 사용자명 변경
    email: Optional[str] = None                 # 이메일 변경
    profile_image_url: Optional[str] = None     # 프로필 이미지 URL 변경
    bio: Optional[str] = None                   # 소개글 변경


class User(UserBase):
    """사용자 정보 응답 모델 (API 응답용)"""
    id: int                                    # 사용자 고유 ID
    uuid: str                                  # 사용자 UUID
    role: UserRole                             # 사용자 역할
    total_loss: float = Field(default=0.0, description="총 손실 금액 (MON)")      # 총 손실
    total_gain: float = Field(default=0.0, description="총 수익 금액 (MON)")      # 총 수익
    profile_image_url: Optional[str] = None    # 프로필 이미지 URL
    bio: Optional[str] = None                  # 사용자 소개
    is_active: bool = True                     # 계정 활성화 상태
    created_at: datetime                       # 계정 생성 시간
    updated_at: datetime                       # 정보 수정 시간
    
    class Config:
        from_attributes = True                 # SQLAlchemy 모델에서 속성 자동 매핑


class UserInDB(User):
    """데이터베이스 내 사용자 정보 (내부 처리용)"""
    pass 