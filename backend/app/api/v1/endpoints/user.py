from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import UserModel
import uuid

router = APIRouter()


class UserCreateRequest(BaseModel):
    """사용자 생성 요청 모델"""
    wallet_address: str


class UserCreateResponse(BaseModel):
    """사용자 생성 응답 모델"""
    wallet_address: str
    user_id: int
    user_uuid: str
    message: str


class UserInfoResponse(BaseModel):
    """사용자 정보 응답 모델"""
    wallet_address: str
    user_id: int
    user_uuid: str
    created_at: str


@router.post(
    "/", 
    response_model=UserCreateResponse,
    summary="지갑 주소로 회원가입",
    description="지갑 주소로 새로운 사용자를 생성합니다",
    tags=["user"]
)
async def create_user(
    user_data: UserCreateRequest, 
    db: Session = Depends(get_db)
):
    """
    지갑 주소로 회원가입
    
    - **wallet_address**: 이더리움 지갑 주소
    
    지갑 주소가 이미 존재하면 기존 사용자 정보를 반환합니다.
    """
    try:
        # 지갑 주소 형식 검증
        if not user_data.wallet_address.startswith('0x') or len(user_data.wallet_address) != 42:
            raise HTTPException(
                status_code=400, 
                detail="Invalid wallet address format"
            )
        
        # 기존 사용자 확인
        existing_user = db.query(UserModel).filter(
            UserModel.wallet_address == user_data.wallet_address
        ).first()
        
        if existing_user:
            # 기존 사용자가 있으면 해당 정보 반환
                    return UserCreateResponse(
            wallet_address=existing_user.__dict__["wallet_address"],
            user_id=existing_user.__dict__["id"],
            user_uuid=str(existing_user.uuid),
            message="User already exists"
        )
        
        # 새 사용자 생성
        new_user = UserModel(
            wallet_address=user_data.wallet_address,
            uuid=uuid.uuid4()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return UserCreateResponse(
            wallet_address=new_user.__dict__["wallet_address"],
            user_id=new_user.__dict__["id"],
            user_uuid=str(new_user.uuid),
            message="User created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error creating user: {str(e)}"
        )


@router.get(
    "/", 
    response_model=UserInfoResponse,
    summary="유저 정보 조회",
    description="지갑 주소로 사용자 정보를 조회합니다",
    tags=["user"]
)
async def get_user_info(
    wallet_address: str = Query(
        ..., 
        description="조회할 지갑 주소",
        example="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
    ),
    db: Session = Depends(get_db)
):
    """
    유저 정보 조회
    
    - **wallet_address**: 조회할 지갑 주소
    
    해당 지갑 주소의 사용자 정보를 반환합니다.
    """
    try:
        user = db.query(UserModel).filter(
            UserModel.wallet_address == wallet_address
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=404, 
                detail="User not found"
            )
        
        return UserInfoResponse(
            wallet_address=user.__dict__["wallet_address"],
            user_id=user.__dict__["id"],
            user_uuid=str(user.uuid),
            created_at=user.__dict__["created_at"].isoformat() if user.__dict__["created_at"] else ""
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching user info: {str(e)}"
        ) 