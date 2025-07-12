from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.user import UserModel
from app.models.wallet_info import WalletInfoModel
import uuid
from datetime import datetime

router = APIRouter()


class WalletInfoCreateRequest(BaseModel):
    """지갑 정보 생성 요청 모델"""
    wallet_address: str
    loss_rate: float
    loss_amount: float
    ticker: str


class WalletInfoCreateResponse(BaseModel):
    """지갑 정보 생성 응답 모델"""
    wallet_address: str
    loss_rate: float
    loss_amount: float
    ticker: str
    user_id: int
    user_uuid: str
    message: str


class WalletInfoResponse(BaseModel):
    """지갑 정보 응답 모델"""
    wallet_address: str
    loss_rate: float
    loss_amount: float
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
    손실률, 손실 금액, 티커 저장
    
    - **wallet_address**: 지갑 주소
    - **loss_rate**: 손실률 (퍼센트, 예: 15.5 = 15.5%)
    - **loss_amount**: 손실 금액 (MON 기준)
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
        
        # 손실률 검증 (0-100 사이, 퍼센트)
        if not 0 <= wallet_info.loss_rate <= 100:
            raise HTTPException(
                status_code=400, 
                detail="Loss rate must be between 0 and 100 (percentage)"
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
        
        # 기존 wallet_info 확인 (같은 지갑 주소와 티커 조합이 있는지)
        existing_wallet_info = db.query(WalletInfoModel).filter(
            WalletInfoModel.wallet_address == wallet_info.wallet_address,
            WalletInfoModel.ticker == wallet_info.ticker
        ).first()
        
        if existing_wallet_info:
            # 기존 데이터 업데이트
            existing_wallet_info.__dict__["loss_rate"] = wallet_info.loss_rate
            existing_wallet_info.__dict__["loss_amount"] = wallet_info.loss_amount
            existing_wallet_info.__dict__["updated_at"] = datetime.utcnow()
            db.commit()
            db.refresh(existing_wallet_info)
            
            return WalletInfoCreateResponse(
                wallet_address=existing_wallet_info.__dict__["wallet_address"],
                loss_rate=existing_wallet_info.__dict__["loss_rate"],
                loss_amount=existing_wallet_info.__dict__["loss_amount"],
                ticker=existing_wallet_info.__dict__["ticker"],
                user_id=existing_wallet_info.__dict__["user_id"],
                user_uuid=str(existing_wallet_info.user_uuid),
                message="Wallet info updated successfully"
            )
        else:
            # 새 wallet_info 생성
            new_wallet_info = WalletInfoModel(
                uuid=uuid.uuid4(),
                user_id=user.__dict__["id"],
                user_uuid=user.uuid,
                wallet_address=wallet_info.wallet_address,
                loss_rate=wallet_info.loss_rate,
                loss_amount=wallet_info.loss_amount,
                ticker=wallet_info.ticker
            )
            db.add(new_wallet_info)
            db.commit()
            db.refresh(new_wallet_info)
            
            return WalletInfoCreateResponse(
                wallet_address=new_wallet_info.__dict__["wallet_address"],
                loss_rate=new_wallet_info.__dict__["loss_rate"],
                loss_amount=new_wallet_info.__dict__["loss_amount"],
                ticker=new_wallet_info.__dict__["ticker"],
                user_id=new_wallet_info.__dict__["user_id"],
                user_uuid=str(new_wallet_info.user_uuid),
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
        query = db.query(WalletInfoModel)
        
        if wallet_address:
            query = query.filter(WalletInfoModel.wallet_address == wallet_address)
        
        wallet_info_records = query.offset(offset).limit(limit).all()
        
        wallet_info_list = []
        for record in wallet_info_records:
            wallet_info_list.append(WalletInfoResponse(
                wallet_address=record.__dict__["wallet_address"],
                loss_rate=record.__dict__["loss_rate"],
                loss_amount=record.__dict__["loss_amount"],
                ticker=record.__dict__["ticker"],
                user_id=record.__dict__["user_id"],
                user_uuid=str(record.user_uuid),
                created_at=record.__dict__["created_at"].isoformat() if record.__dict__["created_at"] else ""
            ))
        
        return wallet_info_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching wallet info: {str(e)}"
        ) 