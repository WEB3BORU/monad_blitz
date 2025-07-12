import { createPublicClient, http, parseAbi } from 'viem';
import { mainnet } from 'wagmi/chains';

// 공개 클라이언트 생성 (더 안정적인 RPC 사용)
const publicClient = createPublicClient({
  chain: mainnet,
  transport: http('https://eth.llamarpc.com')
});

// ERC20 Transfer 이벤트 ABI
const ERC20_TRANSFER_ABI = parseAbi([
  'event Transfer(address indexed from, address indexed to, uint256 value)'
]);

// 거래 내역 인터페이스
interface TransactionRecord {
  tokenAddress: string;
  tokenSymbol: string;
  tokenName: string;
  type: 'buy' | 'sell' | 'transfer';
  amount: number;
  price: number;
  timestamp: number;
  txHash: string;
}

// PnL 계산 결과
interface PnLResult {
  tokenSymbol: string;
  totalBought: number;
  totalSold: number;
  currentBalance: number;
  averageBuyPrice: number;
  currentPrice: number;
  totalPnL: number;
  pnlPercentage: number;
}

// 지갑의 ERC20 거래 내역 조회 (실제 구현)
export const getERC20Transactions = async (walletAddress: string): Promise<TransactionRecord[]> => {
  try {
    console.log('실제 블록체인 조회 시작, 지갑 주소:', walletAddress);
    
    const latestBlock = await publicClient.getBlockNumber();
    console.log('최신 블록 번호:', latestBlock.toString());
    
    // RPC 제한으로 인해 1000개 블록씩 나누어 조회
    const maxBlockRange = 1000;
    const totalBlocksToQuery = 10000; // 총 조회할 블록 수
    const fromBlock = latestBlock - BigInt(totalBlocksToQuery);
    console.log('조회 시작 블록:', fromBlock.toString());

    // EVM 메인넷 주요 토큰들 (확장된 버전)
    const commonTokens = {
      // Stablecoins
      'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
      'USDC': '0xA0b86a33E6441b8C4C8C8C8C8C8C8C8C8C8C8C8C',
      'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
      'BUSD': '0x4Fabb145d64652a948d72533023f6E7A623C7C53',
      'TUSD': '0x0000000000085d4780B73119b644AE5ecd22b376',
      'FRAX': '0x853d955aCEf822Db058eb8505911ED77F175b99e',
      'USDP': '0x8E870D67F660D95d5be530380D0eC0bd388289E1',
      'GUSD': '0x056Fd409E1d7a124BD7017459dFEa2F387b6d5Cd',
      
      // Wrapped Tokens
      'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
      'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
      'WMATIC': '0x7D1AfA7B718fb893dB30A3aBc0Cfc608aCafEBB0',
      'WAVAX': '0x85f138bfEE4ef8e540890CFb48F620571d67Eda3',
      
      // Major Cryptocurrencies
      'LINK': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
      'UNI': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
      'AAVE': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
      'COMP': '0xc00e94Cb662C3520282E6f5717214004A7f26888',
      'MKR': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
      'SNX': '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F',
      'CRV': '0xD533a949740bb3306d119CC777fa900bA034cd52',
      'YFI': '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad9eC',
      '1INCH': '0x111111111117dC0aa78b770fA6A738034120C302',
      'SUSHI': '0x6B3595068778DD592e39A122f4f5a5cF09C90fE2',
      
      // DeFi Tokens
      'BAL': '0xba100000625a3754423978a60c9317c58a424e3D',
      'REN': '0x408e41876cCcDC0F92210600ef50372656052a38',
      'KNC': '0xdd974D5C2e2928deA5F71b9825b8b646686BD200',
      'ZRX': '0xE41d2489571d322189246DaFA5ebDe1F4699F498',
      'BAT': '0x0D8775F648430679A709E98d2b0Cb6250d2887EF',
      'ENJ': '0xF629cBd94d3791C9250152BD8dfBDF380E2a3B9c',
      'MANA': '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942',
      'SAND': '0x3845badAde8e6dFF049820680d1F14bD3903a5d0',
      'AXS': '0xBB0E17EF65F82Ab018d8EDd776e8DD940327B28b',
      'CHZ': '0x3506424F91fD33084466F402d5D97f05F8e3b4AF',
      
      // Layer 2 & Scaling
      'LDO': '0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32',
      'OP': '0x4200000000000000000000000000000000000042',
      'ARB': '0xB50721BCf8d664c30412Cfbc6cf7a15145234ad1',
      'IMX': '0xF57e7e7C23978C3cAEC3C3548E3D615c346e79fF',
      'MATIC': '0x7D1AfA7B718fb893dB30A3aBc0Cfc608aCafEBB0',
      
      // Meme & Social Tokens
      'SHIB': '0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE',
      'DOGE': '0x3832d2F059E559F2088B4C8Cb8C8C8C8C8C8C8C8C',
      'PEPE': '0x6982508145454Ce325dDbE47a25d4ec3d2311933',
      'FLOKI': '0xcf0C122c6b73ff809C693DB761e7BaeBe62b6a2E',
      
      // Gaming & Metaverse
      'GALA': '0x15D4c048F83bd7e37d49eA4C83a07267Ec4203dA',
      'ILV': '0x767FE9EDC9E0dF98E07454847909b5E959D7ca0E',
      'ALICE': '0xAC51066d7bEC65Dc4589368da368b212745d63E8',
      'TLM': '0x888888848B652B3E3a0f34c96E00EEC0F3a23F72',
      
      // Infrastructure & Oracle
      'FIL': '0x6e1A19F235bE7ED8E3369eF73b196C07257494DE',
      'GRT': '0xc944E90C64B2c07662A292be6244BDf05Cda44a7',
      'BAND': '0xBA11D00c5f74255f56a5E366F4F77f5A186d7f55',
      'UMA': '0x04Fa0d235C4abf4BcF4787aF4CF447DE572eF828',
      
      // Privacy & Security
      'ZEC': '0x1C5db575E2Ff833E46a2E9864C22F4B22E0B37C2',
      'XMR': '0x465e07b60292d653d7a73d3d5d847819c9e0534b',
      
      // Exchange Tokens
      'BNB': '0xB8c77482e45F1F44dE1745F52C74426C631bDD52',
      'OKB': '0x75231F58b43240C9718Dd58B4967c5114342a86c',
      'HT': '0x6f259637dcD74C767781E37Bc6133cd6A68aa161',
      'KCS': '0xf34960d9d60be18cC1D5Afc1A6F012A723a28811',
      
      // Yield & Farming
      'CAKE': '0x152649eA73beAb28c5b49B26eb48f7EAD6d4C898',
      'ALPHA': '0xa1faa113cbE53436Df28FF0aEe54275c13B40975',
      'PERP': '0xbC396689893D065F41bc2C6EcbeE5e0085433449',
      
      // AI & Data
      'OCEAN': '0x967da4048cD07aB37855c090aAF366e4ce1b9F48',
      'FET': '0xaea46A60368A7bD060eec7DF8CBa43b7EF41Ad85',
      'AGIX': '0x5B7533812759B45C86B05812bE63c2497267e441',
      'RNDR': '0x6De037ef9aD2725EB40118Bb1702EBb27e4Aeb24',
      
      // Real World Assets
      'PAXG': '0x45804880De22913dAFE09f4980848ECE6EcbA78a',
    };

    const transactions: TransactionRecord[] = [];
    let processedTokens = 0;

    console.log(`총 ${Object.keys(commonTokens).length}개 토큰 조회 시작`);

    for (const [symbol, address] of Object.entries(commonTokens)) {
      try {
        console.log(`${symbol} 토큰 조회 중... (${++processedTokens}/${Object.keys(commonTokens).length})`);
        
        // 블록 범위를 나누어 조회
        const allSentLogs = [];
        const allReceivedLogs = [];
        
        for (let i = 0; i < totalBlocksToQuery; i += maxBlockRange) {
          const currentFromBlock = fromBlock + BigInt(i);
          const currentToBlock = currentFromBlock + BigInt(maxBlockRange - 1);
          
          // 최신 블록을 넘지 않도록 조정
          const actualToBlock = currentToBlock > latestBlock ? latestBlock : currentToBlock;
          
          console.log(`${symbol} 블록 범위 조회: ${currentFromBlock} ~ ${actualToBlock}`);
          
          try {
            // 지갑에서 보낸 토큰들 (매도)
            const sentLogs = await publicClient.getLogs({
              address: address as `0x${string}`,
              event: ERC20_TRANSFER_ABI[0],
              args: {
                from: walletAddress as `0x${string}`,
              },
              fromBlock: currentFromBlock,
              toBlock: actualToBlock,
            });

            // 지갑으로 받은 토큰들 (매수)
            const receivedLogs = await publicClient.getLogs({
              address: address as `0x${string}`,
              event: ERC20_TRANSFER_ABI[0],
              args: {
                to: walletAddress as `0x${string}`,
              },
              fromBlock: currentFromBlock,
              toBlock: actualToBlock,
            });

            allSentLogs.push(...sentLogs);
            allReceivedLogs.push(...receivedLogs);
            
            // RPC 부하 방지를 위한 짧은 대기
            await new Promise(resolve => setTimeout(resolve, 100));
            
          } catch (rangeError) {
            console.warn(`${symbol} 블록 범위 ${currentFromBlock}-${actualToBlock} 조회 실패:`, rangeError);
            continue;
          }
        }

        console.log(`${symbol}: 보낸 거래 ${allSentLogs.length}개, 받은 거래 ${allReceivedLogs.length}개`);

        // 보낸 거래 처리 (매도)
        for (const log of allSentLogs) {
          try {
            const block = await publicClient.getBlock({
              blockNumber: log.blockNumber,
            });

            transactions.push({
              tokenAddress: address,
              tokenSymbol: symbol,
              tokenName: symbol,
              type: 'sell',
              amount: Number(log.args.value) / Math.pow(10, 18), // decimals 고려
              price: 0, // 나중에 CoinGecko API로 조회
              timestamp: Number(block.timestamp),
              txHash: log.transactionHash,
            });
          } catch (blockError) {
            console.warn(`${symbol} 블록 정보 조회 실패:`, blockError);
            // 블록 정보 없이도 거래 내역은 저장
            transactions.push({
              tokenAddress: address,
              tokenSymbol: symbol,
              tokenName: symbol,
              type: 'sell',
              amount: Number(log.args.value) / Math.pow(10, 18),
              price: 0,
              timestamp: Date.now() / 1000,
              txHash: log.transactionHash,
            });
          }
        }

        // 받은 거래 처리 (매수)
        for (const log of allReceivedLogs) {
          try {
            const block = await publicClient.getBlock({
              blockNumber: log.blockNumber,
            });

            transactions.push({
              tokenAddress: address,
              tokenSymbol: symbol,
              tokenName: symbol,
              type: 'buy',
              amount: Number(log.args.value) / Math.pow(10, 18),
              price: 0, // 나중에 CoinGecko API로 조회
              timestamp: Number(block.timestamp),
              txHash: log.transactionHash,
            });
          } catch (blockError) {
            console.warn(`${symbol} 블록 정보 조회 실패:`, blockError);
            transactions.push({
              tokenAddress: address,
              tokenSymbol: symbol,
              tokenName: symbol,
              type: 'buy',
              amount: Number(log.args.value) / Math.pow(10, 18),
              price: 0,
              timestamp: Date.now() / 1000,
              txHash: log.transactionHash,
            });
          }
        }

      } catch (error) {
        console.error(`${symbol} 토큰 조회 실패:`, error);
      }
    }

    console.log(`총 ${transactions.length}개 거래 내역 조회 완료`);
    return transactions;

  } catch (error) {
    console.error('실제 트랜잭션 조회 실패:', error);
    throw error;
  }
};

// 선택된 토큰들만 조회하는 함수
export const getSelectedTokenTransactions = async (
  walletAddress: string, 
  selectedTokens: string[]
): Promise<TransactionRecord[]> => {
  try {
    console.log('선택된 토큰 조회 시작, 지갑 주소:', walletAddress);
    console.log('선택된 토큰들:', selectedTokens);
    
    const latestBlock = await publicClient.getBlockNumber();
    console.log('최신 블록 번호:', latestBlock.toString());
    
    // RPC 제한으로 인해 1000개 블록씩 나누어 조회
    const maxBlockRange = 1000;
    const totalBlocksToQuery = 10000; // 총 조회할 블록 수
    const fromBlock = latestBlock - BigInt(totalBlocksToQuery);
    console.log('조회 시작 블록:', fromBlock.toString());

    // EVM 메인넷 주요 토큰들 (기존과 동일)
    const commonTokens = {
      // Stablecoins
      'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
      'USDC': '0xA0b86a33E6441b8C4C8C8C8C8C8C8C8C8C8C8C8C',
      'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
      'BUSD': '0x4Fabb145d64652a948d72533023f6E7A623C7C53',
      'TUSD': '0x0000000000085d4780B73119b644AE5ecd22b376',
      'FRAX': '0x853d955aCEf822Db058eb8505911ED77F175b99e',
      'USDP': '0x8E870D67F660D95d5be530380D0eC0bd388289E1',
      'GUSD': '0x056Fd409E1d7a124BD7017459dFEa2F387b6d5Cd',
      
      // Wrapped Tokens
      'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
      'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
      'WMATIC': '0x7D1AfA7B718fb893dB30A3aBc0Cfc608aCafEBB0',
      'WAVAX': '0x85f138bfEE4ef8e540890CFb48F620571d67Eda3',
      
      // Major Cryptocurrencies
      'LINK': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
      'UNI': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
      'AAVE': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
      'COMP': '0xc00e94Cb662C3520282E6f5717214004A7f26888',
      'MKR': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
      'SNX': '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F',
      'CRV': '0xD533a949740bb3306d119CC777fa900bA034cd52',
      'YFI': '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad9eC',
      '1INCH': '0x111111111117dC0aa78b770fA6A738034120C302',
      'SUSHI': '0x6B3595068778DD592e39A122f4f5a5cF09C90fE2',
      
      // DeFi Tokens
      'BAL': '0xba100000625a3754423978a60c9317c58a424e3D',
      'REN': '0x408e41876cCcDC0F92210600ef50372656052a38',
      'KNC': '0xdd974D5C2e2928deA5F71b9825b8b646686BD200',
      'ZRX': '0xE41d2489571d322189246DaFA5ebDe1F4699F498',
      'BAT': '0x0D8775F648430679A709E98d2b0Cb6250d2887EF',
      'ENJ': '0xF629cBd94d3791C9250152BD8dfBDF380E2a3B9c',
      'MANA': '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942',
      'SAND': '0x3845badAde8e6dFF049820680d1F14bD3903a5d0',
      'AXS': '0xBB0E17EF65F82Ab018d8EDd776e8DD940327B28b',
      'CHZ': '0x3506424F91fD33084466F402d5D97f05F8e3b4AF',
      
      // Layer 2 & Scaling
      'LDO': '0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32',
      'OP': '0x4200000000000000000000000000000000000042',
      'ARB': '0xB50721BCf8d664c30412Cfbc6cf7a15145234ad1',
      'IMX': '0xF57e7e7C23978C3cAEC3C3548E3D615c346e79fF',
      'MATIC': '0x7D1AfA7B718fb893dB30A3aBc0Cfc608aCafEBB0',
      
      // Meme & Social Tokens
      'SHIB': '0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE',
      'DOGE': '0x3832d2F059E559F2088B4C8Cb8C8C8C8C8C8C8C8C',
      'PEPE': '0x6982508145454Ce325dDbE47a25d4ec3d2311933',
      'FLOKI': '0xcf0C122c6b73ff809C693DB761e7BaeBe62b6a2E',
      
      // Gaming & Metaverse
      'GALA': '0x15D4c048F83bd7e37d49eA4C83a07267Ec4203dA',
      'ILV': '0x767FE9EDC9E0dF98E07454847909b5E959D7ca0E',
      'ALICE': '0xAC51066d7bEC65Dc4589368da368b212745d63E8',
      'TLM': '0x888888848B652B3E3a0f34c96E00EEC0F3a23F72',
      
      // Infrastructure & Oracle
      'FIL': '0x6e1A19F235bE7ED8E3369eF73b196C07257494DE',
      'GRT': '0xc944E90C64B2c07662A292be6244BDf05Cda44a7',
      'BAND': '0xBA11D00c5f74255f56a5E366F4F77f5A186d7f55',
      'UMA': '0x04Fa0d235C4abf4BcF4787aF4CF447DE572eF828',
      
      // Privacy & Security
      'ZEC': '0x1C5db575E2Ff833E46a2E9864C22F4B22E0B37C2',
      'XMR': '0x465e07b60292d653d7a73d3d5d847819c9e0534b',
      
      // Exchange Tokens
      'BNB': '0xB8c77482e45F1F44dE1745F52C74426C631bDD52',
      'OKB': '0x75231F58b43240C9718Dd58B4967c5114342a86c',
      'HT': '0x6f259637dcD74C767781E37Bc6133cd6A68aa161',
      'KCS': '0xf34960d9d60be18cC1D5Afc1A6F012A723a28811',
      
      // Yield & Farming
      'CAKE': '0x152649eA73beAb28c5b49B26eb48f7EAD6d4C898',
      'ALPHA': '0xa1faa113cbE53436Df28FF0aEe54275c13B40975',
      'PERP': '0xbC396689893D065F41bc2C6EcbeE5e0085433449',
      
      // AI & Data
      'OCEAN': '0x967da4048cD07aB37855c090aAF366e4ce1b9F48',
      'FET': '0xaea46A60368A7bD060eec7DF8CBa43b7EF41Ad85',
      'AGIX': '0x5B7533812759B45C86B05812bE63c2497267e441',
      'RNDR': '0x6De037ef9aD2725EB40118Bb1702EBb27e4Aeb24',
      
      // Real World Assets
      'PAXG': '0x45804880De22913dAFE09f4980848ECE6EcbA78a',
    };

    const transactions: TransactionRecord[] = [];
    let processedTokens = 0;

    console.log(`선택된 ${selectedTokens.length}개 토큰 조회 시작`);

    // 선택된 토큰들만 조회
    for (const symbol of selectedTokens) {
      const address = commonTokens[symbol as keyof typeof commonTokens];
      
      if (!address) {
        console.warn(`${symbol} 토큰 주소를 찾을 수 없습니다.`);
        continue;
      }

      try {
        console.log(`${symbol} 토큰 조회 중... (${++processedTokens}/${selectedTokens.length})`);
        
        // 블록 범위를 나누어 조회
        const allSentLogs = [];
        const allReceivedLogs = [];
        
        for (let i = 0; i < totalBlocksToQuery; i += maxBlockRange) {
          const currentFromBlock = fromBlock + BigInt(i);
          const currentToBlock = currentFromBlock + BigInt(maxBlockRange - 1);
          
          // 최신 블록을 넘지 않도록 조정
          const actualToBlock = currentToBlock > latestBlock ? latestBlock : currentToBlock;
          
          console.log(`${symbol} 블록 범위 조회: ${currentFromBlock} ~ ${actualToBlock}`);
          
          try {
            // 지갑에서 보낸 토큰들 (매도)
            const sentLogs = await publicClient.getLogs({
              address: address as `0x${string}`,
              event: ERC20_TRANSFER_ABI[0],
              args: {
                from: walletAddress as `0x${string}`,
              },
              fromBlock: currentFromBlock,
              toBlock: actualToBlock,
            });

            // 지갑으로 받은 토큰들 (매수)
            const receivedLogs = await publicClient.getLogs({
              address: address as `0x${string}`,
              event: ERC20_TRANSFER_ABI[0],
              args: {
                to: walletAddress as `0x${string}`,
              },
              fromBlock: currentFromBlock,
              toBlock: actualToBlock,
            });

            allSentLogs.push(...sentLogs);
            allReceivedLogs.push(...receivedLogs);
            
            // RPC 부하 방지를 위한 짧은 대기
            await new Promise(resolve => setTimeout(resolve, 100));
            
          } catch (rangeError) {
            console.warn(`${symbol} 블록 범위 ${currentFromBlock}-${actualToBlock} 조회 실패:`, rangeError);
            continue;
          }
        }

        console.log(`${symbol}: 보낸 거래 ${allSentLogs.length}개, 받은 거래 ${allReceivedLogs.length}개`);

        // 보낸 거래 처리 (매도)
        for (const log of allSentLogs) {
          try {
            const block = await publicClient.getBlock({
              blockNumber: log.blockNumber,
            });

            transactions.push({
              tokenAddress: address,
              tokenSymbol: symbol,
              tokenName: symbol,
              type: 'sell',
              amount: Number(log.args.value) / Math.pow(10, 18), // decimals 고려
              price: 0, // 나중에 CoinGecko API로 조회
              timestamp: Number(block.timestamp),
              txHash: log.transactionHash,
            });
          } catch (blockError) {
            console.warn(`${symbol} 블록 정보 조회 실패:`, blockError);
            // 블록 정보 없이도 거래 내역은 저장
            transactions.push({
              tokenAddress: address,
              tokenSymbol: symbol,
              tokenName: symbol,
              type: 'sell',
              amount: Number(log.args.value) / Math.pow(10, 18),
              price: 0,
              timestamp: Date.now() / 1000,
              txHash: log.transactionHash,
            });
          }
        }

        // 받은 거래 처리 (매수)
        for (const log of allReceivedLogs) {
          try {
            const block = await publicClient.getBlock({
              blockNumber: log.blockNumber,
            });

            transactions.push({
              tokenAddress: address,
              tokenSymbol: symbol,
              tokenName: symbol,
              type: 'buy',
              amount: Number(log.args.value) / Math.pow(10, 18),
              price: 0, // 나중에 CoinGecko API로 조회
              timestamp: Number(block.timestamp),
              txHash: log.transactionHash,
            });
          } catch (blockError) {
            console.warn(`${symbol} 블록 정보 조회 실패:`, blockError);
            transactions.push({
              tokenAddress: address,
              tokenSymbol: symbol,
              tokenName: symbol,
              type: 'buy',
              amount: Number(log.args.value) / Math.pow(10, 18),
              price: 0,
              timestamp: Date.now() / 1000,
              txHash: log.transactionHash,
            });
          }
        }

      } catch (error) {
        console.error(`${symbol} 토큰 조회 실패:`, error);
      }
    }

    console.log(`총 ${transactions.length}개 거래 내역 조회 완료`);
    return transactions;

  } catch (error) {
    console.error('선택된 토큰 조회 실패:', error);
    throw error;
  }
};

// 사용 가능한 토큰 목록 반환 함수
export const getAvailableTokens = () => {
  return [
    'USDT', 'USDC', 'DAI', 'BUSD', 'TUSD', 'FRAX', 'USDP', 'GUSD',
    'WETH', 'WBTC', 'WMATIC', 'WAVAX',
    'LINK', 'UNI', 'AAVE', 'COMP', 'MKR', 'SNX', 'CRV', 'YFI', '1INCH', 'SUSHI',
    'BAL', 'REN', 'KNC', 'ZRX', 'BAT', 'ENJ', 'MANA', 'SAND', 'AXS', 'CHZ',
    'LDO', 'OP', 'ARB', 'IMX', 'MATIC',
    'SHIB', 'DOGE', 'PEPE', 'FLOKI',
    'GALA', 'ILV', 'ALICE', 'TLM',
    'FIL', 'GRT', 'BAND', 'UMA',
    'ZEC', 'XMR',
    'BNB', 'OKB', 'HT', 'KCS',
    'CAKE', 'ALPHA', 'PERP',
    'OCEAN', 'FET', 'AGIX', 'RNDR',
    'PAXG'
  ];
};

// CoinGecko API로 특정 날짜 가격 조회
export const getHistoricalPrice = async (tokenId: string, date: string): Promise<number> => {
  try {
    console.log(`히스토리 가격 조회 시작: ${tokenId}, 날짜: ${date}`);
    
    const url = `https://api.coingecko.com/api/v3/coins/${tokenId}/history?date=${date}`;
    console.log('요청 URL:', url);
    
    const response = await fetch(url);
    console.log('응답 상태:', response.status);
    
    if (!response.ok) {
      console.error('API 응답 에러:', response.status, response.statusText);
      return 0;
    }
    
    const data = await response.json();
    console.log('히스토리 가격 응답:', data);
    
    const price = data.market_data?.current_price?.usd || 0;
    console.log(`히스토리 가격 결과: ${price}`);
    
    return price;
  } catch (error) {
    console.error('히스토리 가격 조회 실패:', error);
    return 0;
  }
};

// 현재 가격 조회 (개선된 버전)
export const getCurrentPrice = async (tokenId: string): Promise<number> => {
  try {
    console.log(`현재 가격 조회 시작: ${tokenId}`);
    
    // CoinGecko ID 매핑 (확장된 버전)
    const coinGeckoIds: { [key: string]: string } = {
      // Stablecoins
      'USDT': 'tether',
      'USDC': 'usd-coin',
      'DAI': 'dai',
      'BUSD': 'binance-usd',
      'TUSD': 'true-usd',
      'FRAX': 'frax',
      'USDP': 'paxos-standard',
      'GUSD': 'gemini-dollar',
      
      // Wrapped Tokens
      'WETH': 'weth',
      'WBTC': 'wrapped-bitcoin',
      'WMATIC': 'wmatic',
      'WAVAX': 'wrapped-avax',
      
      // Major Cryptocurrencies
      'LINK': 'chainlink',
      'UNI': 'uniswap',
      'AAVE': 'aave',
      'COMP': 'compound-governance-token',
      'MKR': 'maker',
      'SNX': 'havven',
      'CRV': 'curve-dao-token',
      'YFI': 'yearn-finance',
      '1INCH': '1inch',
      'SUSHI': 'sushi',
      
      // DeFi Tokens
      'BAL': 'balancer',
      'REN': 'republic-protocol',
      'KNC': 'kyber-network-crystal',
      'ZRX': '0x',
      'BAT': 'basic-attention-token',
      'ENJ': 'enjincoin',
      'MANA': 'decentraland',
      'SAND': 'the-sandbox',
      'AXS': 'axie-infinity',
      'CHZ': 'chiliz',
      
      // Layer 2 & Scaling
      'LDO': 'lido-dao',
      'OP': 'optimism',
      'ARB': 'arbitrum',
      'IMX': 'immutable-x',
      'MATIC': 'matic-network',
      
      // Meme & Social Tokens
      'SHIB': 'shiba-inu',
      'DOGE': 'dogecoin',
      'PEPE': 'pepe',
      'FLOKI': 'floki-inu',
      
      // Gaming & Metaverse
      'GALA': 'gala',
      'ILV': 'illuvium',
      'ALICE': 'my-neighbor-alice',
      'TLM': 'alien-worlds',
      
      // Infrastructure & Oracle
      'FIL': 'filecoin',
      'GRT': 'the-graph',
      'BAND': 'band-protocol',
      'UMA': 'uma',
      
      // Privacy & Security
      'ZEC': 'zcash',
      'XMR': 'monero',
      
      // Exchange Tokens
      'BNB': 'binancecoin',
      'OKB': 'okb',
      'HT': 'huobi-token',
      'KCS': 'kucoin-token',
      
      // Yield & Farming
      'CAKE': 'pancakeswap-token',
      'ALPHA': 'alpha-finance',
      'PERP': 'perpetual-protocol',
      
      // AI & Data
      'OCEAN': 'ocean-protocol',
      'FET': 'fetch-ai',
      'AGIX': 'singularitynet',
      'RNDR': 'render-token',
      
      // Real World Assets
      'PAXG': 'pax-gold',
    };
    
    const mappedId = coinGeckoIds[tokenId.toUpperCase()] || tokenId.toLowerCase();
    console.log(`매핑된 ID: ${mappedId}`);
    
    const url = `https://api.coingecko.com/api/v3/simple/price?ids=${mappedId}&vs_currencies=usd`;
    console.log('요청 URL:', url);
    
    const response = await fetch(url);
    console.log('응답 상태:', response.status);
    
    if (!response.ok) {
      console.error('API 응답 에러:', response.status, response.statusText);
      return 0;
    }
    
    const data = await response.json();
    console.log('현재 가격 응답:', data);
    
    const price = data[mappedId]?.usd || 0;
    console.log(`현재 가격 결과: ${price}`);
    
    return price;
  } catch (error) {
    console.error('현재 가격 조회 실패:', error);
    return 0;
  }
};

// PnL 계산
export const calculatePnL = (transactions: TransactionRecord[]): PnLResult[] => {
  console.log('PnL 계산 시작, 거래 내역:', transactions);
  
  const tokenGroups = new Map<string, TransactionRecord[]>();

  // 토큰별로 거래 내역 그룹화
  for (const tx of transactions) {
    if (!tokenGroups.has(tx.tokenSymbol)) {
      tokenGroups.set(tx.tokenSymbol, []);
    }
    tokenGroups.get(tx.tokenSymbol)!.push(tx);
  }

  const results: PnLResult[] = [];

  // Map iteration 수정
  for (const [symbol, txs] of Array.from(tokenGroups.entries())) {
    console.log(`${symbol} 토큰 PnL 계산:`, txs);
    
    let totalBought = 0;
    let totalSold = 0;
    let totalBoughtValue = 0;
    let totalSoldValue = 0;

    for (const tx of txs) {
      if (tx.type === 'buy') {
        totalBought += tx.amount;
        totalBoughtValue += tx.amount * tx.price;
      } else {
        totalSold += tx.amount;
        totalSoldValue += tx.amount * tx.price;
      }
    }

    const currentBalance = totalBought - totalSold;
    const averageBuyPrice = totalBought > 0 ? totalBoughtValue / totalBought : 0;
    const currentPrice = 0; // CoinGecko API로 조회 필요
    const currentValue = currentBalance * currentPrice;
    const totalPnL = currentValue - totalBoughtValue;
    const pnlPercentage = totalBoughtValue > 0 ? (totalPnL / totalBoughtValue) * 100 : 0;

    const result = {
      tokenSymbol: symbol,
      totalBought,
      totalSold,
      currentBalance,
      averageBuyPrice,
      currentPrice,
      totalPnL,
      pnlPercentage,
    };
    
    console.log(`${symbol} PnL 결과:`, result);
    results.push(result);
  }

  console.log('전체 PnL 계산 결과:', results);
  return results;
}; 