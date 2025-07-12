# Crypto Graves Smart Contracts

## 개요
Crypto Graves 프로젝트의 스마트 컨트랙트입니다. NFT 민팅과 밈토큰 생성을 지원합니다.

## 컨트랙트

### 1. CryptoGravesNFT.sol
- **기능**: NFT 민팅
- **특징**: 
  - 지갑 주소와 티커별로 고유한 NFT 생성
  - 손실률, 손실 금액, 티커 정보를 메타데이터에 포함
  - ERC721 표준 준수

### 2. CryptoGravesToken.sol
- **기능**: 밈토큰 생성 (pump.fun 스타일)
- **특징**:
  - 손실 정보를 기반으로 밈토큰 생성
  - ERC20 표준 준수
  - 거래소에서 거래 가능

## 배포 방법

### 1. 환경 설정
```bash
cd smart-contracts
npm install
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가:
```
MONAD_RPC_URL=https://rpc.testnet.monad.xyz
PRIVATE_KEY=your_private_key_here
```

### 3. 컨트랙트 컴파일
```bash
npm run compile
```

### 4. 컨트랙트 배포

#### NFT 컨트랙트 배포
```bash
npm run deploy:nft
```

#### 토큰 컨트랙트 배포
```bash
npm run deploy:token
```

### 5. 배포 확인
배포 후 `deployment-nft.json`과 `deployment-token.json` 파일이 생성됩니다.

## API 연동

배포된 컨트랙트 주소를 API에서 사용하려면:

1. `deployment-nft.json`과 `deployment-token.json` 파일을 백엔드 루트로 복사
2. API가 자동으로 컨트랙트 주소를 로드합니다

## 사용 예시

### NFT 민팅
```json
POST /api/v1/mint/
{
  "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "ticker": "BTC",
  "mint_type": "nft"
}
```

### 밈토큰 생성
```json
POST /api/v1/mint/
{
  "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "ticker": "BTC",
  "mint_type": "token",
  "token_name": "Bitcoin Loss Token",
  "token_symbol": "BTCLOSS",
  "total_supply": 1000000
}
```

## 주의사항

1. **테스트넷 사용**: 현재 Monad 테스트넷에 배포됩니다
2. **가스비**: 배포 시 가스비가 필요합니다
3. **프라이빗 키**: 안전하게 관리하세요
4. **컨트랙트 주소**: 배포 후 API에서 사용할 수 있도록 주소를 업데이트하세요 