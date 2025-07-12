// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract CryptoGravesToken is ERC20, Ownable, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIds;
    
    // 토큰 메타데이터 구조
    struct TokenMetadata {
        string walletAddress;
        uint256 lossRate;      // 손실률 (퍼센트 * 100)
        uint256 lossAmount;    // 손실 금액 (MON 기준)
        string ticker;         // 자산 티커
        uint256 timestamp;     // 생성 시간
        string name;           // 토큰 이름
        string symbol;         // 토큰 심볼
        uint256 totalSupply;   // 총 공급량
        bool verified;         // 검증 여부
    }
    
    // 토큰 ID -> 메타데이터 매핑
    mapping(uint256 => TokenMetadata) public tokenMetadata;
    
    // 지갑 주소 -> 토큰 ID 매핑
    mapping(string => mapping(string => uint256)) public walletTickerToTokenId;
    
    // 토큰 ID -> 컨트랙트 주소 매핑
    mapping(uint256 => address) public tokenIdToContract;
    
    // 검증된 지갑 주소들
    mapping(string => bool) public verifiedWallets;
    
    // 민팅 조건
    uint256 public constant MIN_LOSS_RATE = 500;  // 최소 5% 손실
    uint256 public constant MIN_LOSS_AMOUNT = 100; // 최소 100 MON 손실
    uint256 public constant MAX_LOSS_RATE = 10000; // 최대 100% 손실
    uint256 public constant MAX_TOTAL_SUPPLY = 1000000000; // 최대 10억 토큰
    
    // 이벤트
    event TokenCreated(
        uint256 indexed tokenId,
        string indexed walletAddress,
        string ticker,
        uint256 lossRate,
        uint256 lossAmount,
        address tokenContract,
        string name,
        string symbol,
        uint256 totalSupply
    );
    
    event WalletVerified(string indexed walletAddress, bool verified);
    
    constructor() ERC20("Crypto Graves Token Factory", "CGTF") Ownable(msg.sender) {}
    
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
     * @dev 밈토큰 생성 함수 (검증된 지갑만)
     */
    function createMemeToken(
        string memory walletAddress,
        uint256 lossRate,
        uint256 lossAmount,
        string memory ticker,
        string memory name,
        string memory symbol,
        uint256 totalSupply
    ) public nonReentrant whenNotPaused returns (uint256 tokenId, address tokenContract) {
        // 1. 지갑 주소 검증 확인
        require(verifiedWallets[walletAddress], "Wallet not verified");
        
        // 2. 민팅 조건 검증
        require(lossRate >= MIN_LOSS_RATE, "Loss rate too low");
        require(lossRate <= MAX_LOSS_RATE, "Loss rate too high");
        require(lossAmount >= MIN_LOSS_AMOUNT, "Loss amount too low");
        require(totalSupply > 0 && totalSupply <= MAX_TOTAL_SUPPLY, "Invalid total supply");
        
        // 3. 같은 지갑 주소와 티커 조합이 이미 존재하는지 확인
        require(
            walletTickerToTokenId[walletAddress][ticker] == 0,
            "Token already exists for this wallet and ticker"
        );
        
        // 4. 입력값 검증
        require(bytes(ticker).length > 0 && bytes(ticker).length <= 10, "Invalid ticker length");
        require(bytes(name).length > 0 && bytes(name).length <= 50, "Invalid name length");
        require(bytes(symbol).length > 0 && bytes(symbol).length <= 10, "Invalid symbol length");
        require(bytes(walletAddress).length == 42, "Invalid wallet address length");
        
        _tokenIds.increment();
        tokenId = _tokenIds.current();
        
        // 새로운 밈토큰 컨트랙트 배포
        MemeToken newToken = new MemeToken(name, symbol, totalSupply, msg.sender);
        tokenContract = address(newToken);
        
        // 메타데이터 저장
        tokenMetadata[tokenId] = TokenMetadata({
            walletAddress: walletAddress,
            lossRate: lossRate,
            lossAmount: lossAmount,
            ticker: ticker,
            timestamp: block.timestamp,
            name: name,
            symbol: symbol,
            totalSupply: totalSupply,
            verified: true
        });
        
        // 매핑 업데이트
        walletTickerToTokenId[walletAddress][ticker] = tokenId;
        tokenIdToContract[tokenId] = tokenContract;
        
        emit TokenCreated(
            tokenId,
            walletAddress,
            ticker,
            lossRate,
            lossAmount,
            tokenContract,
            name,
            symbol,
            totalSupply
        );
    }
    
    /**
     * @dev 지갑 주소와 티커로 토큰 조회
     */
    function getTokenByWalletAndTicker(
        string memory walletAddress,
        string memory ticker
    ) public view returns (uint256 tokenId, TokenMetadata memory metadata, address tokenContract) {
        tokenId = walletTickerToTokenId[walletAddress][ticker];
        require(tokenId > 0, "Token not found");
        metadata = tokenMetadata[tokenId];
        tokenContract = tokenIdToContract[tokenId];
    }
    
    /**
     * @dev 토큰 ID로 메타데이터 조회
     */
    function getTokenMetadata(uint256 tokenId) public view returns (TokenMetadata memory) {
        require(tokenId > 0 && tokenId <= _tokenIds.current(), "Token does not exist");
        return tokenMetadata[tokenId];
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
    
    /**
     * @dev 재진입 공격 방지
     */
    function _beforeTokenTransfer(address from, address to, uint256 amount) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }
}

/**
 * @dev 밈토큰 컨트랙트
 */
contract MemeToken is ERC20, Ownable, ReentrancyGuard, Pausable {
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply,
        address initialOwner
    ) ERC20(name, symbol) Ownable(initialOwner) {
        _mint(initialOwner, initialSupply * 10**decimals());
    }
    
    /**
     * @dev 토큰 전송 (거래소에서 거래 가능)
     */
    function transfer(address to, uint256 amount) public override whenNotPaused returns (bool) {
        return super.transfer(to, amount);
    }
    
    /**
     * @dev 토큰 승인 (거래소에서 거래 가능)
     */
    function approve(address spender, uint256 amount) public override whenNotPaused returns (bool) {
        return super.approve(spender, amount);
    }
    
    /**
     * @dev 토큰 전송 (from -> to)
     */
    function transferFrom(address from, address to, uint256 amount) public override whenNotPaused returns (bool) {
        return super.transferFrom(from, to, amount);
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
} 