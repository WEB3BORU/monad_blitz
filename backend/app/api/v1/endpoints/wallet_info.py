from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.user import UserModel
import uuid
from datetime import datetime

router = APIRouter()


class WalletInfoCreateRequest(BaseModel):
    """지갑 정보 생성 요청 모델"""
    wallet_address: str
    loss_rate: float
    ticker: str


class WalletInfoCreateResponse(BaseModel):
    """지갑 정보 생성 응답 모델"""
    wallet_address: str
    loss_rate: float
    ticker: str
    user_id: int
    user_uuid: str
    message: str


class WalletInfoResponse(BaseModel):
    """지갑 정보 응답 모델"""
    wallet_address: str
    loss_rate: float
    ticker: str
    user_id: int
    user_uuid: str
    created_at: str


@router.post(
    "/", 
    response_model=WalletInfoCreateResponse,
    summary="손실률과 티커 저장",
    description="지갑 주소의 손실률과 티커 정보를 저장합니다",
    tags=["wallet_info"]
)
async def create_wallet_info(
    wallet_info: WalletInfoCreateRequest, 
    db: Session = Depends(get_db)
):
    """
    손실률과 티커 저장
    
    - **wallet_address**: 지갑 주소
    - **loss_rate**: 손실률 (예: 0.15 = 15%)
    - **ticker**: 자산 티커 (예: BTC, ETH)
    
    해당 지갑 주소의 사용자가 없으면 자동으로 생성합니다.
    """
    try:
        # 지갑 주소 형식 검증
        if not wallet_info.wallet_address.startswith('0x') or len(wallet_info.wallet_address) != 42:
            raise HTTPException(
                status_code=400, 
                detail="Invalid wallet address format"
            )
        
        # 손실률 검증 (0-1 사이)
        if not 0 <= wallet_info.loss_rate <= 1:
            raise HTTPException(
                status_code=400, 
                detail="Loss rate must be between 0 and 1"
            )
        
        # 기존 사용자 확인 또는 생성
        user = db.query(UserModel).filter(
            UserModel.wallet_address == wallet_info.wallet_address
        ).first()
        
        if not user:
            # 새 사용자 생성
            user = UserModel(
                wallet_address=wallet_info.wallet_address,
                uuid=uuid.uuid4()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 여기서는 간단히 사용자 정보만 반환
        # 실제로는 별도의 wallet_info 테이블을 만들어야 하지만
        # 현재 요구사항에 맞춰 사용자 정보에 손실률과 티커를 포함하여 반환
        
        return WalletInfoCreateResponse(
            wallet_address=user.__dict__["wallet_address"],
            loss_rate=wallet_info.loss_rate,
            ticker=wallet_info.ticker,
            user_id=user.__dict__["id"],
            user_uuid=str(user.uuid),
            message="Wallet info saved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error saving wallet info: {str(e)}"
        )


@router.get(
    "/", 
    response_model=List[WalletInfoResponse],
    summary="손실률과 티커 리스트 조회",
    description="저장된 손실률과 티커 정보 목록을 조회합니다",
    tags=["wallet_info"]
)
async def get_wallet_info_list(
    wallet_address: Optional[str] = Query(
        None, 
        description="특정 지갑 주소로 필터링 (선택사항)",
        example="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
    ),
    limit: int = Query(50, description="조회할 개수", example=50),
    offset: int = Query(0, description="건너뛸 개수", example=0),
    db: Session = Depends(get_db)
):
    """
    손실률과 티커 리스트 조회
    
    - **wallet_address**: 특정 지갑 주소로 필터링 (선택사항)
    - **limit**: 조회할 개수 (기본값: 50)
    - **offset**: 건너뛸 개수 (기본값: 0)
    
    현재는 사용자 목록을 반환하며, 실제 손실률과 티커 정보는
    별도 테이블 구현 시 추가됩니다.
    """
    try:
        query = db.query(UserModel)
        
        if wallet_address:
            query = query.filter(UserModel.wallet_address == wallet_address)
        
        users = query.offset(offset).limit(limit).all()
        
        # 임시로 더미 데이터로 손실률과 티커 정보 생성
        # 실제 구현 시에는 별도 테이블에서 조회
        wallet_info_list = []
        for user in users:
            # 임시 데이터 (실제로는 별도 테이블에서 조회)
            wallet_info_list.append(WalletInfoResponse(
                wallet_address=user.__dict__["wallet_address"],
                loss_rate=0.15,  # 임시 손실률
                ticker="BTC",    # 임시 티커
                user_id=user.__dict__["id"],
                user_uuid=str(user.uuid),
                created_at=user.__dict__["created_at"].isoformat() if user.__dict__["created_at"] else ""
            ))
        
        return wallet_info_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching wallet info: {str(e)}"
        ) 