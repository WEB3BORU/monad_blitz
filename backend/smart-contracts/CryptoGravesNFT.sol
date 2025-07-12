// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract CryptoGravesNFT is ERC721, ERC721URIStorage, Ownable, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIds;
    
    // NFT 메타데이터 구조
    struct NFTMetadata {
        string walletAddress;
        uint256 lossRate;      // 손실률 (퍼센트 * 100, 예: 15.5% = 1550)
        uint256 lossAmount;    // 손실 금액 (MON 기준)
        string ticker;         // 자산 티커
        uint256 timestamp;     // 민팅 시간
        bool verified;         // 검증 여부
    }
    
    // 토큰 ID -> 메타데이터 매핑
    mapping(uint256 => NFTMetadata) public tokenMetadata;
    
    // 지갑 주소 -> 토큰 ID 매핑 (같은 지갑의 같은 티커는 하나만)
    mapping(string => mapping(string => uint256)) public walletTickerToTokenId;
    
    // 검증된 지갑 주소들 (백엔드에서 검증된 지갑만 민팅 가능)
    mapping(string => bool) public verifiedWallets;
    
    // 민팅 조건
    uint256 public constant MIN_LOSS_RATE = 500;  // 최소 5% 손실
    uint256 public constant MIN_LOSS_AMOUNT = 100; // 최소 100 MON 손실
    uint256 public constant MAX_LOSS_RATE = 10000; // 최대 100% 손실
    
    // 이벤트
    event NFTMinted(
        uint256 indexed tokenId,
        string indexed walletAddress,
        string ticker,
        uint256 lossRate,
        uint256 lossAmount,
        uint256 timestamp
    );
    
    event WalletVerified(string indexed walletAddress, bool verified);
    
    constructor() ERC721("Crypto Graves NFT", "CGNFT") Ownable(msg.sender) {}
    
    /**
     * @dev 지갑 주소 검증 (관리자만)
     */
    function verifyWallet(string memory walletAddress, bool verified) public onlyOwner {
        verifiedWallets[walletAddress] = verified;
        emit WalletVerified(walletAddress, verified);
    }
    
    /**
     * @dev 여러 지갑 주소 일괄 검증
     */
    function batchVerifyWallets(string[] memory walletAddresses, bool[] memory verified) public onlyOwner {
        require(walletAddresses.length == verified.length, "Arrays length mismatch");
        for (uint i = 0; i < walletAddresses.length; i++) {
            verifiedWallets[walletAddresses[i]] = verified[i];
            emit WalletVerified(walletAddresses[i], verified[i]);
        }
    }
    
    /**
     * @dev NFT 민팅 함수 (검증된 지갑만)
     */
    function mintNFT(
        string memory walletAddress,
        uint256 lossRate,
        uint256 lossAmount,
        string memory ticker,
        string memory tokenURI
    ) public nonReentrant whenNotPaused returns (uint256) {
        // 1. 지갑 주소 검증 확인
        require(verifiedWallets[walletAddress], "Wallet not verified");
        
        // 2. 민팅 조건 검증
        require(lossRate >= MIN_LOSS_RATE, "Loss rate too low");
        require(lossRate <= MAX_LOSS_RATE, "Loss rate too high");
        require(lossAmount >= MIN_LOSS_AMOUNT, "Loss amount too low");
        
        // 3. 같은 지갑 주소와 티커 조합이 이미 존재하는지 확인
        require(
            walletTickerToTokenId[walletAddress][ticker] == 0,
            "NFT already exists for this wallet and ticker"
        );
        
        // 4. 티커 길이 검증
        require(bytes(ticker).length > 0 && bytes(ticker).length <= 10, "Invalid ticker length");
        
        // 5. 지갑 주소 형식 검증 (간단한 검증)
        require(bytes(walletAddress).length == 42, "Invalid wallet address length");
        
        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();
        
        // NFT 민팅
        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        
        // 메타데이터 저장
        tokenMetadata[newTokenId] = NFTMetadata({
            walletAddress: walletAddress,
            lossRate: lossRate,
            lossAmount: lossAmount,
            ticker: ticker,
            timestamp: block.timestamp,
            verified: true
        });
        
        // 매핑 업데이트
        walletTickerToTokenId[walletAddress][ticker] = newTokenId;
        
        emit NFTMinted(
            newTokenId,
            walletAddress,
            ticker,
            lossRate,
            lossAmount,
            block.timestamp
        );
        
        return newTokenId;
    }
    
    /**
     * @dev 지갑 주소와 티커로 NFT 조회
     */
    function getNFTByWalletAndTicker(
        string memory walletAddress,
        string memory ticker
    ) public view returns (uint256 tokenId, NFTMetadata memory metadata) {
        tokenId = walletTickerToTokenId[walletAddress][ticker];
        require(tokenId > 0, "NFT not found");
        metadata = tokenMetadata[tokenId];
    }
    
    /**
     * @dev 토큰 ID로 메타데이터 조회
     */
    function getTokenMetadata(uint256 tokenId) public view returns (NFTMetadata memory) {
        require(_exists(tokenId), "Token does not exist");
        return tokenMetadata[tokenId];
    }
    
    /**
     * @dev 지갑 주소의 모든 NFT 조회
     */
    function getNFTsByWallet(string memory walletAddress) public view returns (uint256[] memory tokenIds) {
        // 구현: 지갑 주소로 모든 NFT 토큰 ID 반환
        // 실제 구현에서는 더 복잡한 로직이 필요할 수 있음
    }
    
    /**
     * @dev 컨트랙트 일시정지 (긴급 상황용)
     */
    function pause() public onlyOwner {
        _pause();
    }
    
    /**
     * @dev 컨트랙트 재개
     */
    function unpause() public onlyOwner {
        _unpause();
    }
    
    // Override functions
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
    
    /**
     * @dev 재진입 공격 방지
     */
    function _beforeTokenTransfer(address from, address to, uint256 tokenId, uint256 batchSize) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }
} 