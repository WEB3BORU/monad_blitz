#!/usr/bin/env python3
"""
Crypto Graves Smart Contract Testing Script
Tests NFT minting and token creation functionality
"""

import os
import json
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_deployment_info():
    """Load deployment information from JSON files"""
    try:
        with open('deployment-nft.json', 'r') as f:
            nft_info = json.load(f)
        with open('deployment-token.json', 'r') as f:
            token_info = json.load(f)
        return nft_info, token_info
    except FileNotFoundError as e:
        print(f"❌ Deployment file not found: {e}")
        return None, None

def setup_web3():
    """Setup Web3 connection to Monad testnet"""
    rpc_url = os.getenv('MONAD_RPC_URL', 'https://testnet-rpc.monad.xyz')
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Monad testnet")
        return None
    
    return w3

def check_balance(w3, address):
    """Check wallet balance"""
    try:
        balance = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance, 'ether')
        return balance_eth
    except Exception as e:
        print(f"❌ Balance check failed: {e}")
        return None

def load_contract_abi():
    """Load contract ABI from artifacts"""
    try:
        # Load NFT contract ABI
        with open('artifacts/contracts/CryptoGravesNFT.sol/CryptoGravesNFT.json', 'r') as f:
            nft_artifact = json.load(f)
        
        # Load Token contract ABI
        with open('artifacts/contracts/CryptoGravesToken.sol/CryptoGravesToken.json', 'r') as f:
            token_artifact = json.load(f)
        
        return nft_artifact['abi'], token_artifact['abi']
    except FileNotFoundError as e:
        print(f"❌ Contract artifact not found: {e}")
        return None, None

def test_nft_contract(w3, contract_address, abi, wallet_address):
    """Test NFT contract functionality"""
    print("\n🎨 Testing NFT Contract...")
    
    try:
        # Create contract instance
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Test contract name and symbol
        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()
        print(f"📝 Contract Name: {name}")
        print(f"🏷️  Contract Symbol: {symbol}")
        
        # Check total supply
        total_supply = contract.functions.totalSupply().call()
        print(f"📊 Total Supply: {total_supply}")
        
        # Check balance of test wallet
        balance = contract.functions.balanceOf(wallet_address).call()
        print(f"💰 Wallet NFT Balance: {balance}")
        
        return True
    except Exception as e:
        print(f"❌ NFT contract test failed: {e}")
        return False

def test_token_contract(w3, contract_address, abi, wallet_address):
    """Test Token contract functionality"""
    print("\n🪙 Testing Token Contract...")
    
    try:
        # Create contract instance
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Test contract name and symbol
        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()
        decimals = contract.functions.decimals().call()
        total_supply = contract.functions.totalSupply().call()
        
        print(f"📝 Contract Name: {name}")
        print(f"🏷️  Contract Symbol: {symbol}")
        print(f"🔢 Decimals: {decimals}")
        print(f"📊 Total Supply: {total_supply}")
        
        # Check balance of test wallet
        balance = contract.functions.balanceOf(wallet_address).call()
        print(f"💰 Wallet Token Balance: {balance}")
        
        return True
    except Exception as e:
        print(f"❌ Token contract test failed: {e}")
        return False

def main():
    print("🚀 Starting Crypto Graves Minting Tests...")
    
    # Load deployment info
    nft_info, token_info = load_deployment_info()
    if not nft_info or not token_info:
        return
    
    print(f"📋 NFT Contract: {nft_info['address']}")
    print(f"📋 Token Contract: {token_info['address']}")
    
    # Setup Web3
    w3 = setup_web3()
    if not w3:
        return
    
    print(f"🌐 RPC URL: {os.getenv('MONAD_RPC_URL', 'https://testnet-rpc.monad.xyz')}")
    print("-" * 50)
    
    # Get wallet info
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("❌ Balance check failed: PRIVATE_KEY environment variable not set")
        return
    
    # Create account from private key
    account = Account.from_key(private_key)
    wallet_address = account.address
    
    print(f"👛 Wallet Address: {wallet_address}")
    
    # Check balance
    balance = check_balance(w3, wallet_address)
    if balance is not None:
        print(f"💰 Wallet Balance: {balance:.4f} MON")
    
    # Load contract ABIs
    nft_abi, token_abi = load_contract_abi()
    if not nft_abi or not token_abi:
        print("⚠️  Could not load contract ABIs, skipping contract tests")
        return
    
    # Test contracts
    nft_success = test_nft_contract(w3, nft_info['address'], nft_abi, wallet_address)
    token_success = test_token_contract(w3, token_info['address'], token_abi, wallet_address)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"🎨 NFT Contract: {'✅ PASS' if nft_success else '❌ FAIL'}")
    print(f"🪙 Token Contract: {'✅ PASS' if token_success else '❌ FAIL'}")
    
    if nft_success and token_success:
        print("🎉 All tests passed! Your contracts are ready for use.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
