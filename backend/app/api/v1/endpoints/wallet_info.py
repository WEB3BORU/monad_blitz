# type: ignore
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.user import UserModel
from app.models.wallet_info import WalletInfoModel
import uuid
from datetime import datetime
from decimal import Decimal

router = APIRouter()


class WalletInfoCreateRequest(BaseModel):
    """지갑 정보 생성 요청 모델 (프론트엔드에서 모든 값을 string으로 전송)"""
    wallet_address: str
    ticker: str
    avg_buyprice: str = "0.0"
    avg_sellprice: str = "0.0"
    current_price: str = "0.0"
    total_buyprice: str = "0.0"
    total_sellprice: str = "0.0"


class WalletInfoCreateResponse(BaseModel):
    """지갑 정보 생성 응답 모델"""
    wallet_address: str
    ticker: str
    avg_buyprice: float
    avg_sellprice: float
    current_price: float
    total_buyprice: float
    total_sellprice: float
    loss_rate: float
    loss_amount: float
    user_id: int
    user_uuid: str
    message: str


class WalletInfoResponse(BaseModel):
    """지갑 정보 응답 모델"""
    wallet_address: str
    ticker: str
    avg_buyprice: float
    avg_sellprice: float
    current_price: float
    total_buyprice: float
    total_sellprice: float
    loss_rate: float
    loss_amount: float
    user_id: int
    user_uuid: str
    created_at: str


@router.post(
    "/", 
    response_model=WalletInfoCreateResponse,
    summary="거래 정보 저장",
    description="지갑 주소의 거래 정보를 저장합니다",
    tags=["wallet_info"]
)
async def create_wallet_info(
    wallet_info: WalletInfoCreateRequest, 
    db: Session = Depends(get_db)
):
    """
    거래 정보 저장 (프론트엔드에서 모든 값을 string으로 전송)
    
    - **wallet_address**: 지갑 주소
    - **ticker**: 자산 티커 (예: BTC, ETH)
    - **avg_buyprice**: 평균 매수가 (string)
    - **avg_sellprice**: 평균 매도가 (string)
    - **current_price**: 현재가 (string)
    - **total_buyprice**: 총 매수금액 (string)
    - **total_sellprice**: 총 매도금액 (string)
    
    해당 지갑 주소의 사용자가 없으면 자동으로 생성합니다.
    손실률과 손실금액은 자동으로 계산됩니다.
    """
    try:
        # 지갑 주소 형식 검증
        if not wallet_info.wallet_address.startswith('0x') or len(wallet_info.wallet_address) != 42:
            raise HTTPException(
                status_code=400, 
                detail="Invalid wallet address format"
            )
        
        # String 값을 float로 변환하고 검증
        try:
            avg_buyprice = float(wallet_info.avg_buyprice)
            avg_sellprice = float(wallet_info.avg_sellprice)
            current_price = float(wallet_info.current_price)
            total_buyprice = float(wallet_info.total_buyprice)
            total_sellprice = float(wallet_info.total_sellprice)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid numeric values provided"
            )
        
        # 거래 정보 검증
        if avg_buyprice < 0 or avg_sellprice < 0 or current_price < 0:
            raise HTTPException(
                status_code=400, 
                detail="Prices must be non-negative"
            )
        
        if total_buyprice < 0 or total_sellprice < 0:
            raise HTTPException(
                status_code=400, 
                detail="Total amounts must be non-negative"
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
            # 기존 데이터 업데이트 (직접 속성 접근)
            existing_wallet_info.avg_buyprice = Decimal(str(avg_buyprice))  # type: ignore
            existing_wallet_info.avg_sellprice = Decimal(str(avg_sellprice))  # type: ignore
            existing_wallet_info.current_price = Decimal(str(current_price))  # type: ignore
            existing_wallet_info.total_buyprice = Decimal(str(total_buyprice))  # type: ignore
            existing_wallet_info.total_sellprice = Decimal(str(total_sellprice))  # type: ignore
            db.commit()
            db.refresh(existing_wallet_info)
            
            return WalletInfoCreateResponse(
                wallet_address=existing_wallet_info.wallet_address,
                ticker=existing_wallet_info.ticker,
                avg_buyprice=float(existing_wallet_info.avg_buyprice),
                avg_sellprice=float(existing_wallet_info.avg_sellprice),
                current_price=float(existing_wallet_info.current_price),
                total_buyprice=float(existing_wallet_info.total_buyprice),
                total_sellprice=float(existing_wallet_info.total_sellprice),
                loss_rate=float(existing_wallet_info.loss_rate),
                loss_amount=float(existing_wallet_info.loss_amount),
                user_id=existing_wallet_info.user_id,
                user_uuid=str(existing_wallet_info.user_uuid),
                message="Wallet info updated successfully"
            )
        else:
            # 새 wallet_info 생성 (kwargs 사용)
            new_wallet_info = WalletInfoModel(
                uuid=uuid.uuid4(),
                user_id=user.id,
                user_uuid=user.uuid,
                wallet_address=wallet_info.wallet_address,  # type: ignore
                ticker=wallet_info.ticker,  # type: ignore
                avg_buyprice=Decimal(str(avg_buyprice)),  # type: ignore
                avg_sellprice=Decimal(str(avg_sellprice)),  # type: ignore
                current_price=Decimal(str(current_price)),  # type: ignore
                total_buyprice=Decimal(str(total_buyprice)),  # type: ignore
                total_sellprice=Decimal(str(total_sellprice))  # type: ignore
            )
            db.add(new_wallet_info)
            db.commit()
            db.refresh(new_wallet_info)
            
            return WalletInfoCreateResponse(
                wallet_address=new_wallet_info.wallet_address,
                ticker=new_wallet_info.ticker,
                avg_buyprice=float(new_wallet_info.avg_buyprice),
                avg_sellprice=float(new_wallet_info.avg_sellprice),
                current_price=float(new_wallet_info.current_price),
                total_buyprice=float(new_wallet_info.total_buyprice),
                total_sellprice=float(new_wallet_info.total_sellprice),
                loss_rate=float(new_wallet_info.loss_rate),
                loss_amount=float(new_wallet_info.loss_amount),
                user_id=new_wallet_info.user_id,
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
    summary="거래 정보 리스트 조회",
    description="저장된 거래 정보 목록을 조회합니다",
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
    거래 정보 리스트 조회
    
    - **wallet_address**: 특정 지갑 주소로 필터링 (선택사항)
    - **limit**: 조회할 개수 (기본값: 50)
    - **offset**: 건너뛸 개수 (기본값: 0)
    """
    try:
        query = db.query(WalletInfoModel)
        
        if wallet_address:
            query = query.filter(WalletInfoModel.wallet_address == wallet_address)
        
        wallet_info_records = query.offset(offset).limit(limit).all()
        
        wallet_info_list = []
        for record in wallet_info_records:
            wallet_info_list.append(WalletInfoResponse(
                wallet_address=record.wallet_address,
                ticker=record.ticker,
                avg_buyprice=float(record.avg_buyprice),
                avg_sellprice=float(record.avg_sellprice),
                current_price=float(record.current_price),
                total_buyprice=float(record.total_buyprice),
                total_sellprice=float(record.total_sellprice),
                loss_rate=float(record.loss_rate),
                loss_amount=float(record.loss_amount),
                user_id=record.user_id,
                user_uuid=str(record.user_uuid),
                created_at=record.created_at.isoformat() if record.created_at else ""
            ))
        
        return wallet_info_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching wallet info: {str(e)}"
        ) 