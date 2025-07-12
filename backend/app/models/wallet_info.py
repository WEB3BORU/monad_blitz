from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric
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
    
    # 자산 정보
    ticker = Column(String(10), nullable=False, index=True)  # 자산 티커
    
    # 거래 정보
    avg_buyprice = Column(Numeric(20, 8), default=0.0, nullable=False)  # 평균 매수가
    avg_sellprice = Column(Numeric(20, 8), default=0.0, nullable=False)  # 평균 매도가
    current_price = Column(Numeric(20, 8), default=0.0, nullable=False)  # 현재가
    total_buyprice = Column(Numeric(20, 8), default=0.0, nullable=False)  # 총 매수금액
    total_sellprice = Column(Numeric(20, 8), default=0.0, nullable=False)  # 총 매도금액
    
    # 손실 정보 (자동 계산됨)
    loss_rate = Column(Float, nullable=False, default=0.0)  # 손실률 (퍼센트)
    loss_amount = Column(Numeric(20, 8), default=0.0, nullable=False)  # 손실 금액 (MON 기준)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계 설정 (주석 처리 - 현재는 단순한 구조로)
    # user = relationship("UserModel", back_populates="wallet_info")


# Pydantic Models
class WalletInfoBase(BaseModel):
    """지갑 정보 기본 모델"""
    wallet_address: str = Field(..., description="지갑 주소")
    ticker: str = Field(..., description="자산 티커")
    avg_buyprice: float = Field(default=0.0, description="평균 매수가")
    avg_sellprice: float = Field(default=0.0, description="평균 매도가")
    current_price: float = Field(default=0.0, description="현재가")
    total_buyprice: float = Field(default=0.0, description="총 매수금액")
    total_sellprice: float = Field(default=0.0, description="총 매도금액")


class WalletInfoCreate(WalletInfoBase):
    """지갑 정보 생성 요청 모델"""
    user_id: int = Field(..., description="사용자 ID")
    user_uuid: str = Field(..., description="사용자 UUID")


class WalletInfoUpdate(BaseModel):
    """지갑 정보 업데이트 요청 모델"""
    ticker: Optional[str] = None
    avg_buyprice: Optional[float] = None
    avg_sellprice: Optional[float] = None
    current_price: Optional[float] = None
    total_buyprice: Optional[float] = None
    total_sellprice: Optional[float] = None


class WalletInfo(WalletInfoBase):
    """지갑 정보 응답 모델"""
    id: int
    uuid: str
    user_id: int
    user_uuid: str
    loss_rate: float = Field(default=0.0, description="손실률 (퍼센트)")
    loss_amount: float = Field(default=0.0, description="손실 금액 (MON 기준)")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WalletInfoInDB(WalletInfo):
    """데이터베이스 내 지갑 정보 (내부 처리용)"""
    pass


class WalletInfoSummary(BaseModel):
    """지갑 정보 요약 모델 (계산된 필드 포함)"""
    id: int
    uuid: str
    user_id: int
    user_uuid: str
    wallet_address: str
    ticker: str
    loss_rate: float
    avg_buyprice: float
    avg_sellprice: float
    current_price: float
    total_buyprice: float
    total_sellprice: float
    loss_amount: float
    unrealized_pnl_percent: float = Field(description="미실현 손익률")
    unrealized_pnl_amount: float = Field(description="미실현 손익금액")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 