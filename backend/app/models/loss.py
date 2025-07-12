from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class LossStatus(str, Enum):
    """손실 데이터 상태 Enum"""
    PENDING = "pending"       # 검증 대기 중
    VERIFIED = "verified"     # 검증 완료
    REJECTED = "rejected"     # 검증 거부


# SQLAlchemy ORM Model (데이터베이스 테이블과 매핑되는 모델)
class LossModel(Base):
    """손실 데이터 테이블 모델"""
    __tablename__ = "losses"
    
    # 기본 식별자
    id = Column(Integer, primary_key=True, index=True)                    # 손실 데이터 고유 ID (자동 증가)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)  # 보안용 UUID
    
    # 사용자 연결 (외래키)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)      # 사용자 ID (외래키)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False, index=True)   # 사용자 UUID (외래키)
    
    # 자산 정보
    asset_name = Column(String(100), nullable=False)                      # 자산명 (예: Bitcoin, Ethereum)
    asset_ticker = Column(String(20), nullable=False)                     # 자산 티커 (예: BTC, ETH)
    
    # 손실 정보
    loss_amount = Column(Numeric(20, 8), nullable=False)                 # 손실 금액 (원본 자산 기준, 소수점 8자리)
    loss_amount_mon = Column(Numeric(20, 8), nullable=False)             # 손실 금액 (MON 기준, 소수점 8자리)
    
    # 블록체인 정보
    transaction_hash = Column(String(66), nullable=False)                 # 트랜잭션 해시 (이더리움 해시)
    transaction_data = Column(JSONB, nullable=False)                      # 트랜잭션 상세 데이터 (JSON 형태)
    signature = Column(Text, nullable=False)                              # 사용자 서명 (검증용)
    
    # 검증 정보
    status = Column(String(20), default=LossStatus.PENDING.value)        # 검증 상태 (pending/verified/rejected)
    verified_at = Column(DateTime(timezone=True), nullable=True)          # 검증 완료 시간
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 검증자 ID
    verified_by_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=True)  # 검증자 UUID
    
    # NFT 정보
    nft_token_id = Column(Integer, nullable=True)                         # 발행된 NFT 토큰 ID
    nft_contract_address = Column(String(42), nullable=True)              # NFT 컨트랙트 주소
    
    # 기타 정보
    notes = Column(Text, nullable=True)                                   # 관리자 메모
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())      # 생성 시간
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # 수정 시간


# Pydantic Models (API 요청/응답 데이터 검증용)
class LossBase(BaseModel):
    """손실 데이터 기본 정보 (API 요청용)"""
    user_id: int = Field(..., description="사용자 ID (손실을 등록하는 사용자)")
    user_uuid: str = Field(..., description="사용자 UUID (보안용)")
    asset_name: str = Field(..., description="자산명 (예: Bitcoin, Ethereum)")
    asset_ticker: str = Field(..., description="자산 티커 (예: BTC, ETH)")
    loss_amount: float = Field(..., description="손실 금액 (원본 자산 기준)")
    loss_amount_mon: float = Field(..., description="손실 금액 (MON 기준)")
    transaction_hash: str = Field(..., description="트랜잭션 해시 (이더리움 해시)")
    transaction_data: dict = Field(..., description="트랜잭션 상세 데이터 (JSON)")
    signature: str = Field(..., description="사용자 서명 (검증용)")


class LossCreate(LossBase):
    """새 손실 데이터 생성 요청 모델"""
    pass


class LossUpdate(BaseModel):
    """손실 데이터 업데이트 요청 모델 (주로 관리자용)"""
    status: Optional[LossStatus] = None              # 검증 상태 변경
    verified_at: Optional[datetime] = None           # 검증 완료 시간 설정
    verified_by: Optional[int] = None                # 검증자 ID 설정
    verified_by_uuid: Optional[str] = None           # 검증자 UUID 설정
    notes: Optional[str] = None                      # 관리자 메모
    nft_token_id: Optional[int] = None               # NFT 토큰 ID 설정
    nft_contract_address: Optional[str] = None       # NFT 컨트랙트 주소 설정


class Loss(LossBase):
    """손실 데이터 응답 모델 (API 응답용)"""
    id: int                                          # 손실 데이터 고유 ID
    uuid: str                                        # 손실 데이터 UUID
    status: LossStatus                               # 검증 상태
    created_at: datetime                             # 생성 시간
    updated_at: datetime                             # 수정 시간
    verified_at: Optional[datetime] = None           # 검증 완료 시간
    verified_by: Optional[int] = None                # 검증자 ID
    verified_by_uuid: Optional[str] = None           # 검증자 UUID
    nft_token_id: Optional[int] = Field(None, description="발행된 NFT 토큰 ID")  # NFT 토큰 ID
    nft_contract_address: Optional[str] = None       # NFT 컨트랙트 주소
    notes: Optional[str] = None                      # 관리자 메모
    
    class Config:
        from_attributes = True                       # SQLAlchemy 모델에서 속성 자동 매핑


class LossInDB(Loss):
    """데이터베이스 내 손실 데이터 (내부 처리용)"""
    pass 