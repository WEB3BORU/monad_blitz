from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from app.config import settings
from app.database import get_db
from app.models.loss import LossModel, LossStatus
from app.models.user import UserModel
from datetime import datetime
import json
import uuid

router = APIRouter()


class LossResponse(BaseModel):
    """손실 데이터 응답 모델"""
    id: int
    uuid: str
    user_id: int
    user_uuid: str
    asset_name: str
    asset_ticker: str
    loss_amount: float
    loss_amount_mon: float
    transaction_hash: str
    status: LossStatus
    created_at: datetime
    nft_token_id: Optional[int] = None


class LossCreateRequest(BaseModel):
    """손실 데이터 생성 요청 모델"""
    user_id: int
    user_uuid: str
    asset_name: str
    asset_ticker: str
    loss_amount: float
    loss_amount_mon: float
    transaction_hash: str
    transaction_data: dict
    signature: str


class LossUpdateRequest(BaseModel):
    """손실 데이터 업데이트 요청 모델"""
    status: Optional[LossStatus] = None
    notes: Optional[str] = None
    nft_token_id: Optional[int] = None
    nft_contract_address: Optional[str] = None


class LossVerificationRequest(BaseModel):
    """손실 데이터 검증 요청 모델"""
    verified_by: int


class LossVerificationResponse(BaseModel):
    """손실 데이터 검증 응답 모델"""
    message: str
    loss_id: int
    loss_uuid: str
    verified_by: int
    verified_at: datetime


class TransactionUploadResponse(BaseModel):
    """트랜잭션 업로드 응답 모델"""
    message: str
    filename: str
    transaction_data: dict
    user_id: Optional[int] = None
    user_uuid: Optional[str] = None
    asset_name: Optional[str] = None
    asset_ticker: Optional[str] = None


@router.post(
    "/losses", 
    response_model=LossResponse,
    summary="손실 데이터 등록",
    description="새로운 손실 데이터를 등록합니다",
    tags=["손실 데이터"]
)
async def create_loss(
    loss_data: LossCreateRequest, 
    db: Session = Depends(get_db)
):
    """
    새로운 손실 데이터 등록
    
    - **user_id**: 사용자 ID
    - **user_uuid**: 사용자 UUID
    - **asset_name**: 자산명 (예: Bitcoin, Ethereum)
    - **asset_ticker**: 자산 티커 (예: BTC, ETH)
    - **loss_amount**: 손실 금액 (원본 자산 기준)
    - **loss_amount_mon**: 손실 금액 (MON 기준)
    - **transaction_hash**: 트랜잭션 해시
    - **transaction_data**: 트랜잭션 상세 데이터 (JSON)
    - **signature**: 사용자 서명
    
    등록된 손실 데이터는 기본적으로 'pending' 상태로 설정됩니다.
    """
    try:
        # 사용자 존재 확인
        user = db.query(UserModel).filter(UserModel.id == loss_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, 
                detail="User not found - 사용자를 찾을 수 없습니다"
            )
        
        # 손실 데이터 생성
        loss = LossModel(
            uuid=uuid.uuid4(),
            user_id=loss_data.user_id,
            user_uuid=loss_data.user_uuid,
            asset_name=loss_data.asset_name,
            asset_ticker=loss_data.asset_ticker,
            loss_amount=loss_data.loss_amount,
            loss_amount_mon=loss_data.loss_amount_mon,
            transaction_hash=loss_data.transaction_hash,
            transaction_data=loss_data.transaction_data,
            signature=loss_data.signature,
            status=LossStatus.PENDING.value
        )
        
        db.add(loss)
        db.commit()
        db.refresh(loss)
        
        return LossResponse.model_validate(loss)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error creating loss: {str(e)}"
        )


@router.get(
    "/losses", 
    response_model=List[LossResponse],
    summary="손실 데이터 목록 조회",
    description="손실 데이터 목록을 조회합니다",
    tags=["손실 데이터"]
)
async def get_losses(
    user_id: Optional[int] = Query(None, description="사용자 ID로 필터링", example=1),
    user_uuid: Optional[str] = Query(None, description="사용자 UUID로 필터링", example="550e8400-e29b-41d4-a716-446655440001"),
    status: Optional[LossStatus] = Query(None, description="상태로 필터링", example=LossStatus.PENDING),
    limit: int = Query(50, description="조회할 개수", example=50),
    offset: int = Query(0, description="건너뛸 개수", example=0),
    db: Session = Depends(get_db)
):
    """
    손실 데이터 목록 조회
    
    - **user_id**: 사용자 ID로 필터링 (선택사항)
    - **user_uuid**: 사용자 UUID로 필터링 (선택사항)
    - **status**: 상태로 필터링 (선택사항)
    - **limit**: 조회할 개수 (기본값: 50)
    - **offset**: 건너뛸 개수 (기본값: 0)
    
    필터링 조건을 지정하지 않으면 모든 손실 데이터를 조회합니다.
    """
    try:
        query = db.query(LossModel)
        
        if user_id:
            query = query.filter(LossModel.user_id == user_id)
        
        if user_uuid:
            query = query.filter(LossModel.user_uuid == user_uuid)
        
        if status:
            query = query.filter(LossModel.status == status.value)
        
        losses = query.offset(offset).limit(limit).all()
        
        return [
            LossResponse.model_validate(loss) for loss in losses
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching losses: {str(e)}"
        )


@router.get(
    "/losses/{loss_id}", 
    response_model=LossResponse,
    summary="특정 손실 데이터 조회",
    description="특정 손실 데이터를 조회합니다",
    tags=["손실 데이터"]
)
async def get_loss(
    loss_id: int = Path(..., description="손실 데이터 ID", example=1),
    db: Session = Depends(get_db)
):
    """
    특정 손실 데이터 조회
    
    - **loss_id**: 조회할 손실 데이터 ID
    
    존재하지 않는 ID를 요청하면 404 오류를 반환합니다.
    """
    try:
        loss = db.query(LossModel).filter(LossModel.id == loss_id).first()
        
        if not loss:
            raise HTTPException(
                status_code=404, 
                detail="Loss not found - 손실 데이터를 찾을 수 없습니다"
            )
        
        return LossResponse.model_validate(loss)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching loss: {str(e)}"
        )


@router.put(
    "/losses/{loss_id}", 
    response_model=LossResponse,
    summary="손실 데이터 업데이트",
    description="손실 데이터를 업데이트합니다 (주로 관리자용)",
    tags=["손실 데이터"]
)
async def update_loss(
    loss_id: int = Path(..., description="업데이트할 손실 데이터 ID", example=1),
    loss_update: Optional[LossUpdateRequest] = None,
    db: Session = Depends(get_db)
):
    """
    손실 데이터 업데이트
    
    - **loss_id**: 업데이트할 손실 데이터 ID
    - **status**: 검증 상태 변경 (선택사항)
    - **notes**: 관리자 메모 (선택사항)
    - **nft_token_id**: NFT 토큰 ID 설정 (선택사항)
    - **nft_contract_address**: NFT 컨트랙트 주소 설정 (선택사항)
    
    주로 관리자가 검증 상태를 변경하거나 메모를 추가할 때 사용합니다.
    """
    try:
        loss = db.query(LossModel).filter(LossModel.id == loss_id).first()
        
        if not loss:
            raise HTTPException(
                status_code=404, 
                detail="Loss not found - 손실 데이터를 찾을 수 없습니다"
            )
        
        # 업데이트할 필드들
        if loss_update:
            update_data = loss_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(loss, field, value)
        
        db.commit()
        db.refresh(loss)
        
        return LossResponse.model_validate(loss)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating loss: {str(e)}"
        )


@router.post(
    "/losses/{loss_id}/verify", 
    response_model=LossVerificationResponse,
    summary="손실 데이터 검증",
    description="손실 데이터를 검증 완료 상태로 변경합니다",
    tags=["손실 데이터"]
)
async def verify_loss(
    loss_id: int = Path(..., description="검증할 손실 데이터 ID", example=1),
    verification_data: Optional[LossVerificationRequest] = None,
    db: Session = Depends(get_db)
):
    """
    손실 데이터 검증
    
    - **loss_id**: 검증할 손실 데이터 ID
    - **verified_by**: 검증자 ID
    
    검증 완료 시 상태가 'verified'로 변경되고 검증 시간이 기록됩니다.
    """
    try:
        loss = db.query(LossModel).filter(LossModel.id == loss_id).first()
        
        if not loss:
            raise HTTPException(
                status_code=404, 
                detail="Loss not found - 손실 데이터를 찾을 수 없습니다"
            )
        
        # 검증자 확인
        verifier_id = verification_data.verified_by if verification_data else 1
        verifier = db.query(UserModel).filter(UserModel.id == verifier_id).first()
        if not verifier:
            raise HTTPException(
                status_code=404, 
                detail="Verifier not found - 검증자를 찾을 수 없습니다"
            )
        
        # 상태 업데이트
        setattr(loss, "status", LossStatus.VERIFIED.value)
        setattr(loss, "verified_at", datetime.utcnow())
        setattr(loss, "verified_by", verifier_id)
        setattr(loss, "verified_by_uuid", str(verifier.uuid))
        
        db.commit()
        db.refresh(loss)
        
        return LossVerificationResponse(
            message="Loss verified successfully",
            loss_id=loss.__dict__["id"],
            loss_uuid=str(loss.__dict__["uuid"]),
            verified_by=verifier_id,
            verified_at=loss.__dict__["verified_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error verifying loss: {str(e)}"
        )


@router.post(
    "/losses/upload-transaction", 
    response_model=TransactionUploadResponse,
    summary="트랜잭션 데이터 업로드",
    description="트랜잭션 데이터 JSON 파일을 업로드합니다",
    tags=["손실 데이터"]
)
async def upload_transaction_data(
    file: UploadFile = File(..., description="업로드할 JSON 파일"),
    user_id: Optional[int] = Query(None, description="사용자 ID", example=1),
    user_uuid: Optional[str] = Query(None, description="사용자 UUID", example="550e8400-e29b-41d4-a716-446655440001"),
    asset_name: Optional[str] = Query(None, description="자산명", example="Bitcoin"),
    asset_ticker: Optional[str] = Query(None, description="자산 티커", example="BTC")
):
    """
    트랜잭션 데이터 파일 업로드
    
    - **file**: 업로드할 JSON 파일 (트랜잭션 데이터 포함)
    - **user_id**: 사용자 ID (선택사항)
    - **user_uuid**: 사용자 UUID (선택사항)
    - **asset_name**: 자산명 (선택사항)
    - **asset_ticker**: 자산 티커 (선택사항)
    
    JSON 파일에는 트랜잭션 해시, 송신자, 수신자, 금액 등의 정보가 포함되어야 합니다.
    """
    if not file.filename or not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=400, 
            detail="Only JSON files are allowed - JSON 파일만 업로드 가능합니다"
        )
    
    try:
        # 파일 내용 읽기
        content = await file.read()
        transaction_data = json.loads(content.decode())
        
        # 여기서 트랜잭션 데이터 검증 로직 추가 가능
        # 예: 해시 검증, 서명 검증 등
        
        return TransactionUploadResponse(
            message="Transaction data uploaded successfully",
            filename=file.filename,
            transaction_data=transaction_data,
            user_id=user_id,
            user_uuid=user_uuid,
            asset_name=asset_name,
            asset_ticker=asset_ticker
        )
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid JSON file - 유효하지 않은 JSON 파일입니다"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing file: {str(e)}"
        ) 