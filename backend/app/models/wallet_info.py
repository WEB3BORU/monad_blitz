from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


# SQLAlchemy ORM Model
class WalletInfoModel(Base):
    """지갑 정보 테이블 모델"""
    __tablename__ = "wallet_info"
    
    # 기본 식별자
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # 사용자 관계 (단순화)
    user_id = Column(Integer, nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # 지갑 정보
    wallet_address = Column(String(42), nullable=False, index=True)
    
    # 손실 정보
    loss_rate = Column(Float, nullable=False)  # 손실률 (퍼센트)
    loss_amount = Column(Float, nullable=False)  # 손실 금액 (MON 기준)
    ticker = Column(String(10), nullable=False)  # 자산 티커
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계 설정 (주석 처리 - 현재는 단순한 구조로)
    # user = relationship("UserModel", back_populates="wallet_info")


# Pydantic Models
class WalletInfoBase(BaseModel):
    """지갑 정보 기본 모델"""
    wallet_address: str = Field(..., description="지갑 주소")
    loss_rate: float = Field(..., description="손실률 (퍼센트)")
    loss_amount: float = Field(..., description="손실 금액 (MON 기준)")
    ticker: str = Field(..., description="자산 티커")


class WalletInfoCreate(WalletInfoBase):
    """지갑 정보 생성 요청 모델"""
    user_id: int = Field(..., description="사용자 ID")
    user_uuid: str = Field(..., description="사용자 UUID")


class WalletInfoUpdate(BaseModel):
    """지갑 정보 업데이트 요청 모델"""
    loss_rate: Optional[float] = None
    ticker: Optional[str] = None


class WalletInfo(WalletInfoBase):
    """지갑 정보 응답 모델"""
    id: int
    uuid: str
    user_id: int
    user_uuid: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WalletInfoInDB(WalletInfo):
    """데이터베이스 내 지갑 정보 (내부 처리용)"""
    pass 