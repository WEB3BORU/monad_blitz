# Monad 테스트넷 배포 가이드

## 사전 준비

### 1. 환경 설정
```bash
cd smart-contracts
npm install
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가:
```env
MONAD_RPC_URL=https://rpc.testnet.monad.xyz
PRIVATE_KEY=your_private_key_here
```

### 3. Monad 테스트넷 정보
- **체인 ID**: 1337
- **RPC URL**: https://rpc.testnet.monad.xyz
- **Explorer**: https://explorer.testnet.monad.xyz
- **가스비**: 매우 낮음 (거의 무료)

## 배포 단계

### 1단계: 컨트랙트 컴파일
```bash
npm run compile
```

### 2단계: NFT 컨트랙트 배포
```bash
npm run deploy:nft
```

**예상 출력:**
```
Deploying CryptoGravesNFT contract...
CryptoGravesNFT deployed to: 0x1234567890123456789012345678901234567890
Deployment info saved to deployment-nft.json
```

### 3단계: 토큰 컨트랙트 배포
```bash
npm run deploy:token
```

**예상 출력:**
```
Deploying CryptoGravesToken contract...
CryptoGravesToken deployed to: 0xabcdefabcdefabcdefabcdefabcdefabcdefabcd
Deployment info saved to deployment-token.json
```

### 4단계: 배포 확인
```bash
# 배포된 파일 확인
ls -la deployment-*.json

# 파일 내용 확인
cat deployment-nft.json
cat deployment-token.json
```

## 배포 후 설정

### 1. API 연동
배포된 컨트랙트 주소를 API에서 사용하려면:

```bash
# 배포 파일을 백엔드 루트로 복사
cp deployment-*.json ../
```

### 2. 지갑 검증
배포 후 관리자 지갑으로 지갑 주소를 검증해야 합니다:

```javascript
// NFT 컨트랙트에서 지갑 검증
await nftContract.verifyWallet("0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6", true);

// 토큰 컨트랙트에서 지갑 검증
await tokenContract.verifyWallet("0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6", true);
```

### 3. 테스트 민팅
```javascript
// NFT 민팅 테스트
await nftContract.mintNFT(
    "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    1500, // 15% 손실
    1000, // 1000 MON 손실
    "BTC",
    "ipfs://QmYourMetadataHash"
);

// 밈토큰 생성 테스트
await tokenContract.createMemeToken(
    "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    1500, // 15% 손실
    1000, // 1000 MON 손실
    "BTC",
    "Bitcoin Loss Token",
    "BTCLOSS",
    1000000 // 100만 토큰
);
```

## 문제 해결

### 1. 가스비 부족
```bash
# Monad 테스트넷에서 테스트 MON 받기
# https://faucet.testnet.monad.xyz 에서 받기
```

### 2. 네트워크 연결 문제
```bash
# RPC URL 확인
curl -X POST https://rpc.testnet.monad.xyz \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### 3. 컨트랙트 배포 실패
```bash
# 가스비 확인
npx hardhat console --network monad_testnet
> const gasPrice = await ethers.provider.getGasPrice()
> console.log("Gas price:", ethers.utils.formatUnits(gasPrice, "gwei"), "gwei")
```

## 보안 체크리스트

### 배포 전
- [ ] 프라이빗 키가 안전한지 확인
- [ ] 컨트랙트가 컴파일되는지 확인
- [ ] 테스트넷에서 충분한 MON 보유

### 배포 후
- [ ] 컨트랙트 주소가 올바른지 확인
- [ ] Explorer에서 컨트랙트가 보이는지 확인
- [ ] 관리자 권한이 올바른지 확인
- [ ] 지갑 검증 기능 테스트

### 운영 전
- [ ] 민팅 조건 테스트
- [ ] 보안 기능 테스트
- [ ] API 연동 테스트

## 유용한 명령어

```bash
# 컨트랙트 검증
npx hardhat verify --network monad_testnet 0xYourContractAddress

# 가스비 추정
npx hardhat console --network monad_testnet
> const gasEstimate = await contract.estimateGas.mintNFT(...)
> console.log("Estimated gas:", gasEstimate.toString())

# 이벤트 확인
npx hardhat console --network monad_testnet
> const filter = contract.filters.NFTMinted()
> const events = await contract.queryFilter(filter)
> console.log("Events:", events)
```

## 지원

문제가 발생하면:
1. Monad Discord: https://discord.gg/monad
2. Monad 문서: https://docs.monad.xyz
3. 이슈 트래커: GitHub Issues 