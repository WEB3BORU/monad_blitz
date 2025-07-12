from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import UserModel
from app.models.wallet_info import WalletInfoModel
import uuid
from datetime import datetime
import json
import os
from decimal import Decimal

router = APIRouter()


# NFT 민팅 관련 모델
class NFTMintRequest(BaseModel):
    """NFT 민팅 요청 모델"""
    wallet_address: str
    ticker: str
    avg_buyprice: str = "0.0"
    avg_sellprice: str = "0.0"
    current_price: str = "0.0"
    total_buyprice: str = "0.0"
    total_sellprice: str = "0.0"


class NFTMintResponse(BaseModel):
    """NFT 민팅 응답 모델"""
    wallet_address: str
    ticker: str
    token_id: Optional[int] = None
    contract_address: Optional[str] = None
    transaction_hash: Optional[str] = None
    metadata: Optional[dict] = None
    message: str


# 밈토큰 생성 관련 모델
class TokenMintRequest(BaseModel):
    """밈토큰 생성 요청 모델"""
    wallet_address: str
    ticker: str
    token_name: str
    token_symbol: str
    total_supply: int
    avg_buyprice: str = "0.0"
    avg_sellprice: str = "0.0"
    current_price: str = "0.0"
    total_buyprice: str = "0.0"
    total_sellprice: str = "0.0"


class TokenMintResponse(BaseModel):
    """밈토큰 생성 응답 모델"""
    wallet_address: str
    ticker: str
    token_id: Optional[int] = None
    contract_address: Optional[str] = None
    transaction_hash: Optional[str] = None
    token_name: str
    token_symbol: str
    total_supply: int
    message: str


class NFTMetadata(BaseModel):
    """NFT 메타데이터 모델"""
    name: str
    description: str
    image: str
    attributes: list


@router.post(
    "/nft", 
    response_model=NFTMintResponse,
    summary="NFT 민팅",
    description="지갑 정보를 저장하고 NFT를 민팅합니다",
    tags=["mint"]
)
async def mint_nft(
    mint_request: NFTMintRequest, 
    db: Session = Depends(get_db)
):
    """
    NFT 민팅
    
    - **wallet_address**: 지갑 주소
    - **ticker**: 자산 티커
    - **avg_buyprice**: 평균 매수가 (string)
    - **avg_sellprice**: 평균 매도가 (string)
    - **current_price**: 현재가 (string)
    - **total_buyprice**: 총 매수금액 (string)
    - **total_sellprice**: 총 매도금액 (string)
    
    지갑 정보를 먼저 저장하고, 해당 정보를 기반으로 NFT를 민팅합니다.
    """
    try:
        # 지갑 주소 형식 검증
        if not mint_request.wallet_address.startswith('0x') or len(mint_request.wallet_address) != 42:
            raise HTTPException(
                status_code=400, 
                detail="Invalid wallet address format"
            )
        
        # String 값을 float로 변환하고 검증
        try:
            avg_buyprice = float(mint_request.avg_buyprice)
            avg_sellprice = float(mint_request.avg_sellprice)
            current_price = float(mint_request.current_price)
            total_buyprice = float(mint_request.total_buyprice)
            total_sellprice = float(mint_request.total_sellprice)
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
            UserModel.wallet_address == mint_request.wallet_address
        ).first()
        
        if not user:
            # 새 사용자 생성
            user = UserModel(
                wallet_address=mint_request.wallet_address,
                uuid=uuid.uuid4()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 지갑 정보 저장 또는 업데이트
        existing_wallet_info = db.query(WalletInfoModel).filter(
            WalletInfoModel.wallet_address == mint_request.wallet_address,
            WalletInfoModel.ticker == mint_request.ticker
        ).first()
        
        if existing_wallet_info:
            # 기존 데이터 업데이트
            existing_wallet_info.avg_buyprice = Decimal(str(avg_buyprice))  # type: ignore
            existing_wallet_info.avg_sellprice = Decimal(str(avg_sellprice))  # type: ignore
            existing_wallet_info.current_price = Decimal(str(current_price))  # type: ignore
            existing_wallet_info.total_buyprice = Decimal(str(total_buyprice))  # type: ignore
            existing_wallet_info.total_sellprice = Decimal(str(total_sellprice))  # type: ignore
            db.commit()
            db.refresh(existing_wallet_info)
            wallet_info = existing_wallet_info
        else:
            # 새 wallet_info 생성
            new_wallet_info = WalletInfoModel(
                uuid=uuid.uuid4(),
                user_id=user.id,
                user_uuid=user.uuid,
                wallet_address=mint_request.wallet_address,  # type: ignore
                ticker=mint_request.ticker,  # type: ignore
                avg_buyprice=Decimal(str(avg_buyprice)),  # type: ignore
                avg_sellprice=Decimal(str(avg_sellprice)),  # type: ignore
                current_price=Decimal(str(current_price)),  # type: ignore
                total_buyprice=Decimal(str(total_buyprice)),  # type: ignore
                total_sellprice=Decimal(str(total_sellprice))  # type: ignore
            )
            db.add(new_wallet_info)
            db.commit()
            db.refresh(new_wallet_info)
            wallet_info = new_wallet_info
        
        # 컨트랙트 주소 로드
        contract_addresses = load_contract_addresses()
        nft_address = contract_addresses.get("nft") or "0x0000000000000000000000000000000000000000"
        
        # NFT 민팅
        result = await mint_nft_asset(wallet_info, nft_address)
        
        return NFTMintResponse(
            wallet_address=mint_request.wallet_address,
            ticker=mint_request.ticker,
            token_id=result.get("token_id"),
            contract_address=result.get("contract_address"),
            transaction_hash=result.get("transaction_hash"),
            metadata=result.get("metadata"),
            message="NFT minted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error minting NFT: {str(e)}"
        )


@router.post(
    "/token", 
    response_model=TokenMintResponse,
    summary="밈토큰 생성",
    description="지갑 정보를 저장하고 밈토큰을 생성합니다",
    tags=["mint"]
)
async def create_meme_token(
    mint_request: TokenMintRequest, 
    db: Session = Depends(get_db)
):
    """
    밈토큰 생성
    
    - **wallet_address**: 지갑 주소
    - **ticker**: 자산 티커
    - **token_name**: 토큰 이름
    - **token_symbol**: 토큰 심볼
    - **total_supply**: 총 공급량
    - **avg_buyprice**: 평균 매수가 (string)
    - **avg_sellprice**: 평균 매도가 (string)
    - **current_price**: 현재가 (string)
    - **total_buyprice**: 총 매수금액 (string)
    - **total_sellprice**: 총 매도금액 (string)
    
    지갑 정보를 먼저 저장하고, 해당 정보를 기반으로 밈토큰을 생성합니다.
    """
    try:
        # 지갑 주소 형식 검증
        if not mint_request.wallet_address.startswith('0x') or len(mint_request.wallet_address) != 42:
            raise HTTPException(
                status_code=400, 
                detail="Invalid wallet address format"
            )
        
        # 입력값 검증
        if not mint_request.token_name or not mint_request.token_symbol:
            raise HTTPException(
                status_code=400, 
                detail="token_name and token_symbol are required"
            )
        
        if mint_request.total_supply <= 0:
            raise HTTPException(
                status_code=400, 
                detail="total_supply must be greater than 0"
            )
        
        # String 값을 float로 변환하고 검증
        try:
            avg_buyprice = float(mint_request.avg_buyprice)
            avg_sellprice = float(mint_request.avg_sellprice)
            current_price = float(mint_request.current_price)
            total_buyprice = float(mint_request.total_buyprice)
            total_sellprice = float(mint_request.total_sellprice)
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
            UserModel.wallet_address == mint_request.wallet_address
        ).first()
        
        if not user:
            # 새 사용자 생성
            user = UserModel(
                wallet_address=mint_request.wallet_address,
                uuid=uuid.uuid4()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 지갑 정보 저장 또는 업데이트
        existing_wallet_info = db.query(WalletInfoModel).filter(
            WalletInfoModel.wallet_address == mint_request.wallet_address,
            WalletInfoModel.ticker == mint_request.ticker
        ).first()
        
        if existing_wallet_info:
            # 기존 데이터 업데이트
            existing_wallet_info.avg_buyprice = Decimal(str(avg_buyprice))  # type: ignore
            existing_wallet_info.avg_sellprice = Decimal(str(avg_sellprice))  # type: ignore
            existing_wallet_info.current_price = Decimal(str(current_price))  # type: ignore
            existing_wallet_info.total_buyprice = Decimal(str(total_buyprice))  # type: ignore
            existing_wallet_info.total_sellprice = Decimal(str(total_sellprice))  # type: ignore
            db.commit()
            db.refresh(existing_wallet_info)
            wallet_info = existing_wallet_info
        else:
            # 새 wallet_info 생성
            new_wallet_info = WalletInfoModel(
                uuid=uuid.uuid4(),
                user_id=user.id,
                user_uuid=user.uuid,
                wallet_address=mint_request.wallet_address,  # type: ignore
                ticker=mint_request.ticker,  # type: ignore
                avg_buyprice=Decimal(str(avg_buyprice)),  # type: ignore
                avg_sellprice=Decimal(str(avg_sellprice)),  # type: ignore
                current_price=Decimal(str(current_price)),  # type: ignore
                total_buyprice=Decimal(str(total_buyprice)),  # type: ignore
                total_sellprice=Decimal(str(total_sellprice))  # type: ignore
            )
            db.add(new_wallet_info)
            db.commit()
            db.refresh(new_wallet_info)
            wallet_info = new_wallet_info
        
        # 컨트랙트 주소 로드
        contract_addresses = load_contract_addresses()
        token_address = contract_addresses.get("token") or "0x0000000000000000000000000000000000000000"
        
        # 밈토큰 생성
        result = await create_meme_token_asset(
            wallet_info, 
            mint_request.token_name,
            mint_request.token_symbol,
            mint_request.total_supply,
            token_address
        )
        
        return TokenMintResponse(
            wallet_address=mint_request.wallet_address,
            ticker=mint_request.ticker,
            token_id=result.get("token_id"),
            contract_address=result.get("contract_address"),
            transaction_hash=result.get("transaction_hash"),
            token_name=mint_request.token_name,
            token_symbol=mint_request.token_symbol,
            total_supply=mint_request.total_supply,
            message="Meme token created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error creating meme token: {str(e)}"
        )


async def mint_nft_asset(wallet_info, nft_contract_address: str) -> dict:
    """NFT 민팅 함수"""
    try:
        # NFT 메타데이터 생성
        metadata = create_nft_metadata(wallet_info)
        
        # 실제 블록체인 호출 (여기서는 시뮬레이션)
        # 실제 구현 시에는 Web3.py를 사용하여 컨트랙트 호출
        
        return {
            "token_id": 1,  # 실제로는 컨트랙트에서 반환된 토큰 ID
            "contract_address": nft_contract_address,
            "transaction_hash": "0x" + "0" * 64,  # 실제 트랜잭션 해시
            "metadata": metadata
        }
    except Exception as e:
        raise Exception(f"Failed to mint NFT: {str(e)}")


async def create_meme_token_asset(wallet_info, token_name: str, token_symbol: str, total_supply: int, token_contract_address: str) -> dict:
    """밈토큰 생성 함수"""
    try:
        # 실제 블록체인 호출 (여기서는 시뮬레이션)
        # 실제 구현 시에는 Web3.py를 사용하여 컨트랙트 호출
        
        return {
            "token_id": 1,  # 실제로는 컨트랙트에서 반환된 토큰 ID
            "contract_address": token_contract_address,
            "transaction_hash": "0x" + "0" * 64,  # 실제 트랜잭션 해시
            "token_name": token_name,
            "token_symbol": token_symbol,
            "total_supply": total_supply
        }
    except Exception as e:
        raise Exception(f"Failed to create meme token: {str(e)}")


def create_nft_metadata(wallet_info) -> dict:
    """NFT 메타데이터 생성"""
    return {
        "name": f"Crypto Grave - {wallet_info.ticker}",
        "description": f"Loss NFT for {wallet_info.wallet_address} - {wallet_info.loss_rate}% loss on {wallet_info.ticker}",
        "image": f"https://cryptograves.com/nft/{wallet_info.wallet_address}_{wallet_info.ticker}.png",
        "attributes": [
            {
                "trait_type": "Wallet Address",
                "value": wallet_info.wallet_address
            },
            {
                "trait_type": "Loss Rate",
                "value": f"{wallet_info.loss_rate}%"
            },
            {
                "trait_type": "Loss Amount",
                "value": f"{wallet_info.loss_amount} MON"
            },
            {
                "trait_type": "Ticker",
                "value": wallet_info.ticker
            },
            {
                "trait_type": "Minted At",
                "value": wallet_info.created_at.isoformat() if wallet_info.created_at else ""
            }
        ]
    }


def load_contract_addresses() -> dict:
    """컨트랙트 주소 로드"""
    # 실제 배포 후 이 파일들을 생성하고 주소를 업데이트
    addresses = {
        "nft": "0xCCE694Cd2e6939F04b3efCb55BdaCc607AdB0a14",  # 배포 후 업데이트
        "token": "0xDDB9679FB69B80477b447c27BFB5c5fC13CAAc8E"  # 배포 후 업데이트
    }
    
    # 배포 파일에서 주소 로드 시도
    try:
        if os.path.exists("deployment-nft.json"):
            with open("deployment-nft.json", "r") as f:
                nft_deployment = json.load(f)
                addresses["nft"] = nft_deployment["address"]
        
        if os.path.exists("deployment-token.json"):
            with open("deployment-token.json", "r") as f:
                token_deployment = json.load(f)
                addresses["token"] = token_deployment["address"]
    except Exception:
        pass
    
    return addresses 