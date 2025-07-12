from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from app.config import settings
from app.database import get_db
from app.models.user import UserModel
import uuid
from datetime import datetime, timedelta
from eth_account import Account
from eth_account.messages import encode_defunct
import hashlib

router = APIRouter()


class WalletAuthRequest(BaseModel):
    """지갑 인증 요청 모델"""
    wallet_address: str
    message: str
    signature: str


class WalletAuthResponse(BaseModel):
    """지갑 인증 응답 모델"""
    wallet_address: str
    user_id: int
    user_uuid: str
    message: str = "Authentication successful"


class UserInfoResponse(BaseModel):
    """사용자 정보 응답 모델"""
    wallet_address: str
    message: str


# JWT 관련 함수들 (주석처리 - POC에서는 사용하지 않음)
"""
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # JWT 액세스 토큰 생성
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt
"""


def verify_signature(wallet_address: str, message: str, signature: str) -> bool:
    """이더리움 서명 검증"""
    try:
        # 메시지 해시 생성
        message_hash = encode_defunct(text=message)
        
        # 서명에서 주소 복구
        recovered_address = Account.recover_message(message_hash, signature=signature)
        
        # 주소 비교 (대소문자 구분 없이)
        return recovered_address.lower() == wallet_address.lower()
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False


@router.post(
    "/wallet-auth", 
    response_model=WalletAuthResponse,
    summary="지갑 서명 인증",
    description="이더리움 지갑 서명을 통한 사용자 인증 (POC용 - JWT 없이)",
    tags=["인증"]
)
async def authenticate_wallet(
    auth_request: WalletAuthRequest, 
    db: Session = Depends(get_db)
):
    """
    지갑 서명을 통한 인증
    
    - **wallet_address**: 이더리움 지갑 주소
    - **message**: 서명할 메시지 (보통 타임스탬프 포함)
    - **signature**: 지갑으로 서명한 해시
    
    인증 성공 시 사용자 정보를 반환합니다.
    """
    
    # 서명 검증
    if not verify_signature(
        auth_request.wallet_address,
        auth_request.message,
        auth_request.signature
    ):
        raise HTTPException(
            status_code=401, 
            detail="Invalid signature - 서명이 유효하지 않습니다"
        )
    
    try:
        # 기존 사용자 확인
        user = db.query(UserModel).filter(
            UserModel.wallet_address == auth_request.wallet_address
        ).first()
        
        if not user:
            # 새 사용자 생성
            user = UserModel(
                wallet_address=auth_request.wallet_address,
                uuid=uuid.uuid4()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # JWT 토큰 대신 간단한 응답
        return WalletAuthResponse(
            wallet_address=auth_request.wallet_address,
            user_id=user.__dict__["id"],
            user_uuid=str(user.uuid)
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Authentication error: {str(e)}"
        )


@router.get(
    "/me", 
    response_model=UserInfoResponse,
    summary="사용자 정보 조회",
    description="지갑 주소로 사용자 정보 조회 (POC용)",
    tags=["인증"]
)
async def get_current_user(
    wallet_address: str = Query(
        ..., 
        description="조회할 지갑 주소",
        example="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
    )
):
    """
    지갑 주소로 사용자 정보 조회
    
    - **wallet_address**: 조회할 지갑 주소
    
    현재는 간단한 응답만 반환합니다.
    """
    try:
        # 지갑 주소로 사용자 조회
        if not wallet_address:
            raise HTTPException(
                status_code=400, 
                detail="Wallet address is required - 지갑 주소가 필요합니다"
            )
        
        return UserInfoResponse(
            wallet_address=wallet_address,
            message="User info retrieved by wallet address"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving user: {str(e)}"
        )


# JWT 기반 인증 (주석처리 - POC에서는 사용하지 않음)
"""
@router.get("/me-jwt")
async def get_current_user_jwt(token: str = Depends(lambda x: x)):
    # JWT 토큰으로 현재 인증된 사용자 정보 조회
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        wallet_address: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        user_uuid: str = payload.get("user_uuid")
        
        if wallet_address is None or user_id is None or user_uuid is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "wallet_address": wallet_address, 
            "user_id": user_id,
            "user_uuid": user_uuid
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
""" 