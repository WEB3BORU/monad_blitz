#!/usr/bin/env python3
"""
Crypto Graves - Minting Test Script
더미 데이터로 NFT와 토큰 민팅을 테스트합니다.
"""

import json
import os
import asyncio
from web3 import Web3
from eth_account import Account
import time

# 배포된 컨트랙트 주소
NFT_CONTRACT_ADDRESS = "0xCCE694Cd2e6939F04b3efCb55BdaCc607AdB0a14"
TOKEN_CONTRACT_ADDRESS = "0xDDB9679FB69B80477b447c27BFB5c5fC13CAAc8E"

# Monad 테스트넷 RPC
RPC_URL = "https://testnet-rpc.monad.xyz"

# 컨트랙트 ABI (간단한 버전)
NFT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "walletAddress", "type": "string"},
            {"internalType": "uint256", "name": "lossRate", "type": "uint256"},
            {"internalType": "uint256", "name": "lossAmount", "type": "uint256"},
            {"internalType": "string", "name": "ticker", "type": "string"},
            {"internalType": "string", "name": "tokenURI", "type": "string"}
        ],
        "name": "mintNFT",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "walletAddress", "type": "string"},
            {"internalType": "bool", "name": "verified", "type": "bool"}
        ],
        "name": "verifyWallet",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

TOKEN_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "walletAddress", "type": "string"},
            {"internalType": "uint256", "name": "lossRate", "type": "uint256"},
            {"internalType": "uint256", "name": "lossAmount", "type": "uint256"},
            {"internalType": "string", "name": "ticker", "type": "string"},
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string", "name": "symbol", "type": "string"},
            {"internalType": "uint256", "name": "totalSupply", "type": "uint256"}
        ],
        "name": "createMemeToken",
        "outputs": [
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
            {"internalType": "address", "name": "tokenContract", "type": "address"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "walletAddress", "type": "string"},
            {"internalType": "bool", "name": "verified", "type": "bool"}
        ],
        "name": "verifyWallet",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def load_private_key():
    """환경 변수에서 프라이빗 키 로드"""
    from dotenv import load_dotenv
    load_dotenv()  # .env 파일 로드
    
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise ValueError("PRIVATE_KEY environment variable not set")
    return private_key

def create_dummy_wallet_info():
    """더미 지갑 정보 생성"""
    return {
        "wallet_address": "0xdd8e08015C2777518D7593c477bD863a0761923d",  # 현재 계정 주소
        "ticker": "BTC",
        "loss_rate": 1500,  # 15% 손실 (퍼센트 * 100)
        "loss_amount": 1000,  # 1000 MON 손실
        "created_at": "2025-07-12T07:30:00Z"
    }

def create_nft_metadata(wallet_info):
    """NFT 메타데이터 생성"""
    return json.dumps({
        "name": f"Crypto Grave - {wallet_info['ticker']}",
        "description": f"Loss NFT for {wallet_info['wallet_address']} - {wallet_info['loss_rate']}% loss on {wallet_info['ticker']}",
        "image": f"https://cryptograves.com/nft/{wallet_info['wallet_address']}_{wallet_info['ticker']}.png",
        "attributes": [
            {"trait_type": "Wallet Address", "value": wallet_info["wallet_address"]},
            {"trait_type": "Loss Rate", "value": f"{wallet_info['loss_rate']}%"},
            {"trait_type": "Loss Amount", "value": f"{wallet_info['loss_amount']} MON"},
            {"trait_type": "Ticker", "value": wallet_info["ticker"]},
            {"trait_type": "Minted At", "value": wallet_info["created_at"]}
        ]
    })

async def test_nft_minting():
    """NFT 민팅 테스트"""
    print("🎨 Testing NFT Minting...")
    
    try:
        # Web3 연결
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if not w3.is_connected():
            raise Exception("Failed to connect to Monad testnet")
        
        # 계정 설정
        private_key = load_private_key()
        account = Account.from_key(private_key)
        w3.eth.default_account = account.address
        
        # 컨트랙트 인스턴스 생성
        nft_contract = w3.eth.contract(
            address=Web3.to_checksum_address(NFT_CONTRACT_ADDRESS),
            abi=NFT_ABI
        )
        
        # 더미 데이터 생성
        wallet_info = create_dummy_wallet_info()
        
        # 1. 먼저 지갑 주소 검증
        print("🔐 Verifying wallet address...")
        verify_gas = nft_contract.functions.verifyWallet(
            wallet_info["wallet_address"],
            True
        ).estimate_gas()
        
        verify_transaction = nft_contract.functions.verifyWallet(
            wallet_info["wallet_address"],
            True
        ).build_transaction({
            'gas': verify_gas,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        signed_verify_txn = w3.eth.account.sign_transaction(verify_transaction, private_key)
        verify_tx_hash = w3.eth.send_raw_transaction(signed_verify_txn.rawTransaction)
        verify_receipt = w3.eth.wait_for_transaction_receipt(verify_tx_hash)
        print(f"✅ Wallet verified! Block: {verify_receipt['blockNumber']}")
        
        # 2. NFT 민팅
        print("🎨 Minting NFT...")
        metadata = create_nft_metadata(wallet_info)
        
        # 가스비 추정
        gas_estimate = nft_contract.functions.mintNFT(
            wallet_info["wallet_address"],  # string으로 전달
            wallet_info["loss_rate"],
            wallet_info["loss_amount"],
            wallet_info["ticker"],
            metadata
        ).estimate_gas()
        
        print(f"Estimated gas: {gas_estimate}")
        
        # 트랜잭션 빌드
        transaction = nft_contract.functions.mintNFT(
            wallet_info["wallet_address"],  # string으로 전달
            wallet_info["loss_rate"],
            wallet_info["loss_amount"],
            wallet_info["ticker"],
            metadata
        ).build_transaction({
            'gas': gas_estimate,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        # 트랜잭션 서명 및 전송
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        print(f"🎉 NFT Minting Transaction Hash: {tx_hash.hex()}")
        
        # 트랜잭션 완료 대기
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ NFT Minting completed! Block: {tx_receipt['blockNumber']}")
        
        return tx_hash.hex()
        
    except Exception as e:
        print(f"❌ NFT Minting failed: {str(e)}")
        return None

async def test_token_creation():
    """밈 토큰 생성 테스트"""
    print("🪙 Testing Meme Token Creation...")
    
    try:
        # Web3 연결
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if not w3.is_connected():
            raise Exception("Failed to connect to Monad testnet")
        
        # 계정 설정
        private_key = load_private_key()
        account = Account.from_key(private_key)
        w3.eth.default_account = account.address
        
        # 컨트랙트 인스턴스 생성
        token_contract = w3.eth.contract(
            address=Web3.to_checksum_address(TOKEN_CONTRACT_ADDRESS),
            abi=TOKEN_ABI
        )
        
        # 더미 데이터 생성
        wallet_info = create_dummy_wallet_info()
        token_name = "seoulmonad"  # 토큰 이름을 seoulmonad로 변경
        token_symbol = f"{wallet_info['ticker']}LOSS"
        total_supply = 1000000  # 100만 토큰
        
        # 1. 먼저 지갑 주소 검증
        print("🔐 Verifying wallet address for token creation...")
        verify_gas = token_contract.functions.verifyWallet(
            wallet_info["wallet_address"],
            True
        ).estimate_gas()
        
        verify_transaction = token_contract.functions.verifyWallet(
            wallet_info["wallet_address"],
            True
        ).build_transaction({
            'gas': verify_gas,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        signed_verify_txn = w3.eth.account.sign_transaction(verify_transaction, private_key)
        verify_tx_hash = w3.eth.send_raw_transaction(signed_verify_txn.rawTransaction)
        verify_receipt = w3.eth.wait_for_transaction_receipt(verify_tx_hash)
        print(f"✅ Wallet verified for token! Block: {verify_receipt['blockNumber']}")
        
        # 2. 토큰 생성
        print("🪙 Creating meme token...")
        
        # 가스비 추정
        gas_estimate = token_contract.functions.createMemeToken(
            wallet_info["wallet_address"],  # string으로 전달
            wallet_info["loss_rate"],
            wallet_info["loss_amount"],
            wallet_info["ticker"],
            token_name,
            token_symbol,
            total_supply
        ).estimate_gas()
        
        print(f"Estimated gas: {gas_estimate}")
        
        # 트랜잭션 빌드
        transaction = token_contract.functions.createMemeToken(
            wallet_info["wallet_address"],  # string으로 전달
            wallet_info["loss_rate"],
            wallet_info["loss_amount"],
            wallet_info["ticker"],
            token_name,
            token_symbol,
            total_supply
        ).build_transaction({
            'gas': gas_estimate,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        # 트랜잭션 서명 및 전송
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        print(f"🎉 Token Creation Transaction Hash: {tx_hash.hex()}")
        
        # 트랜잭션 완료 대기
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Token Creation completed! Block: {tx_receipt['blockNumber']}")
        
        return tx_hash.hex()
        
    except Exception as e:
        print(f"❌ Token Creation failed: {str(e)}")
        return None

async def main():
    """메인 테스트 함수"""
    print("🚀 Starting Crypto Graves Minting Tests...")
    print(f"📋 NFT Contract: {NFT_CONTRACT_ADDRESS}")
    print(f"📋 Token Contract: {TOKEN_CONTRACT_ADDRESS}")
    print(f"🌐 RPC URL: {RPC_URL}")
    print("-" * 50)
    
    # 잔액 확인
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        private_key = load_private_key()
        account = Account.from_key(private_key)
        balance = w3.eth.get_balance(account.address)
        print(f"💰 Wallet Balance: {Web3.from_wei(balance, 'ether')} MON")
        print(f"📍 Wallet Address: {account.address}")
        print("-" * 50)
    except Exception as e:
        print(f"❌ Balance check failed: {str(e)}")
        return
    
    # NFT 민팅 테스트
    nft_tx_hash = await test_nft_minting()
    print("-" * 50)
    
    # 잠시 대기
    await asyncio.sleep(2)
    
    # 토큰 생성 테스트
    token_tx_hash = await test_token_creation()
    print("-" * 50)
    
    # 결과 요약
    print("📊 Test Results Summary:")
    print(f"🎨 NFT Minting: {'✅ Success' if nft_tx_hash else '❌ Failed'}")
    if nft_tx_hash:
        print(f"   Transaction: {nft_tx_hash}")
    
    print(f"🪙 Token Creation: {'✅ Success' if token_tx_hash else '❌ Failed'}")
    if token_tx_hash:
        print(f"   Transaction: {token_tx_hash}")
    
    print("🎉 Testing completed!")

if __name__ == "__main__":
    asyncio.run(main()) 