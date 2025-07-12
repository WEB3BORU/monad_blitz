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

router = APIRouter()


class MintRequest(BaseModel):
    """민팅 요청 모델"""
    wallet_address: str
    ticker: str
    mint_type: str  # "nft" 또는 "token"
    token_name: Optional[str] = None  # 밈토큰용
    token_symbol: Optional[str] = None  # 밈토큰용
    total_supply: Optional[int] = None  # 밈토큰용


class MintResponse(BaseModel):
    """민팅 응답 모델"""
    wallet_address: str
    ticker: str
    mint_type: str
    token_id: Optional[int] = None
    contract_address: Optional[str] = None
    transaction_hash: Optional[str] = None
    message: str


class NFTMetadata(BaseModel):
    """NFT 메타데이터 모델"""
    name: str
    description: str
    image: str
    attributes: list


@router.post(
    "/", 
    response_model=MintResponse,
    summary="NFT 또는 밈토큰 민팅",
    description="지갑 정보를 기반으로 NFT 또는 밈토큰을 민팅합니다",
    tags=["mint"]
)
async def mint_asset(
    mint_request: MintRequest, 
    db: Session = Depends(get_db)
):
    """
    NFT 또는 밈토큰 민팅
    
    - **wallet_address**: 지갑 주소
    - **ticker**: 자산 티커
    - **mint_type**: 민팅 타입 ("nft" 또는 "token")
    - **token_name**: 밈토큰 이름 (token 타입일 때만)
    - **token_symbol**: 밈토큰 심볼 (token 타입일 때만)
    - **total_supply**: 총 공급량 (token 타입일 때만)
    
    해당 지갑 주소의 손실 정보를 기반으로 NFT 또는 밈토큰을 민팅합니다.
    """
    try:
        # 지갑 주소 형식 검증
        if not mint_request.wallet_address.startswith('0x') or len(mint_request.wallet_address) != 42:
            raise HTTPException(
                status_code=400, 
                detail="Invalid wallet address format"
            )
        
        # 민팅 타입 검증
        if mint_request.mint_type not in ["nft", "token"]:
            raise HTTPException(
                status_code=400, 
                detail="Mint type must be 'nft' or 'token'"
            )
        
        # 밈토큰 타입일 때 추가 필드 검증
        if mint_request.mint_type == "token":
            if not mint_request.token_name or not mint_request.token_symbol or not mint_request.total_supply:
                raise HTTPException(
                    status_code=400, 
                    detail="token_name, token_symbol, and total_supply are required for token minting"
                )
        
        # 지갑 정보 조회
        wallet_info = db.query(WalletInfoModel).filter(
            WalletInfoModel.wallet_address == mint_request.wallet_address,
            WalletInfoModel.ticker == mint_request.ticker
        ).first()
        
        if not wallet_info:
            raise HTTPException(
                status_code=404, 
                detail="Wallet info not found for this wallet address and ticker"
            )
        
        # 컨트랙트 주소 로드 (실제 배포 후 업데이트 필요)
        contract_addresses = load_contract_addresses()
        
        if mint_request.mint_type == "nft":
            # NFT 민팅
            nft_address = contract_addresses.get("nft") or "0x0000000000000000000000000000000000000000"
            result = await mint_nft(wallet_info, nft_address)
        else:
            # 밈토큰 생성
            token_address = contract_addresses.get("token") or "0x0000000000000000000000000000000000000000"
            result = await create_meme_token(
                wallet_info, 
                mint_request.token_name or "",
                mint_request.token_symbol or "",
                mint_request.total_supply or 0,
                token_address
            )
        
        return MintResponse(
            wallet_address=mint_request.wallet_address,
            ticker=mint_request.ticker,
            mint_type=mint_request.mint_type,
            token_id=result.get("token_id"),
            contract_address=result.get("contract_address"),
            transaction_hash=result.get("transaction_hash"),
            message=f"{mint_request.mint_type.upper()} minted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error minting asset: {str(e)}"
        )


async def mint_nft(wallet_info, nft_contract_address: str) -> dict:
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


async def create_meme_token(wallet_info, token_name: str, token_symbol: str, total_supply: int, token_contract_address: str) -> dict:
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
        "name": f"Crypto Grave - {wallet_info.__dict__['ticker']}",
        "description": f"Loss NFT for {wallet_info.__dict__['wallet_address']} - {wallet_info.__dict__['loss_rate']}% loss on {wallet_info.__dict__['ticker']}",
        "image": f"https://cryptograves.com/nft/{wallet_info.__dict__['wallet_address']}_{wallet_info.__dict__['ticker']}.png",
        "attributes": [
            {
                "trait_type": "Wallet Address",
                "value": wallet_info.__dict__["wallet_address"]
            },
            {
                "trait_type": "Loss Rate",
                "value": f"{wallet_info.__dict__['loss_rate']}%"
            },
            {
                "trait_type": "Loss Amount",
                "value": f"{wallet_info.__dict__['loss_amount']} MON"
            },
            {
                "trait_type": "Ticker",
                "value": wallet_info.__dict__["ticker"]
            },
            {
                "trait_type": "Minted At",
                "value": wallet_info.__dict__["created_at"].isoformat() if wallet_info.__dict__["created_at"] else ""
            }
        ]
    }


def load_contract_addresses() -> dict:
    """컨트랙트 주소 로드"""
    # 실제 배포 후 이 파일들을 생성하고 주소를 업데이트
    addresses = {
        "nft": "0x0000000000000000000000000000000000000000",  # 배포 후 업데이트
        "token": "0x0000000000000000000000000000000000000000"  # 배포 후 업데이트
    }
    
    # 배포 파일에서 주소 로드 시도
    try:
        if os.path.exists("smart-contracts/deployment-nft.json"):
            with open("smart-contracts/deployment-nft.json", "r") as f:
                nft_deployment = json.load(f)
                addresses["nft"] = nft_deployment["address"]
        
        if os.path.exists("smart-contracts/deployment-token.json"):
            with open("smart-contracts/deployment-token.json", "r") as f:
                token_deployment = json.load(f)
                addresses["token"] = token_deployment["address"]
    except Exception:
        pass
    
    return addresses 