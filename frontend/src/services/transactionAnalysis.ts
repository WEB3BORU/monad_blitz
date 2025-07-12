import { createPublicClient, http, parseAbi } from 'viem';
import { mainnet } from 'wagmi/chains';

// Covalent API 설정
const COVALENT_API_KEY = 'cqt_rQRH7vwtPPGhyxxPCxBrMM6xM3g4';
const COVALENT_BASE_URL = 'https://api.covalenthq.com/v1';

// GoldRush API 설정 (향후 과거 가격 조회용)
// const GOLDRUSH_API_KEY = 'your_goldrush_api_key';
// const GOLDRUSH_BASE_URL = 'https://api.goldrush.com';

// 거래 내역 인터페이스 (기존과 호환)
interface TransactionRecord {
  tokenAddress: string;
  tokenSymbol: string;
  tokenName: string;
  type: 'buy' | 'sell';
  amount: number;
  price: number;
  timestamp: number;
  txHash: string;
}

export interface PnLResult {
  tokenSymbol: string;
  totalBought: number;
  totalSold: number;
  currentBalance: number;
  averageBuyPrice: number;
  averageSellPrice: number;
  currentPrice: number;
  totalPnL: number;
  pnlPercentage: number;
  lastTradeDate?: string;
  totalBoughtUSD: number;
  totalSoldUSD: number;
}

// Covalent Historical Price API로 특정 날짜의 토큰 가격 조회
export const getHistoricalPrice = async (
  tokenAddress: string, 
  date: string, 
  chainId: number = 1
): Promise<number> => {
  try {
    console.log(`Historical price 조회: ${tokenAddress} at ${date}`);
    
    // 정확한 Covalent Historical Price API 엔드포인트 사용
    const url = `${COVALENT_BASE_URL}/pricing/historical_by_addresses_v2/eth-mainnet/USD/${tokenAddress}/?from=${date}&to=${date}`;
    console.log('Historical price API URL:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${COVALENT_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Historical price API 요청 실패: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Historical price API 응답:', data);
    
    if (data.error) {
      throw new Error(`Historical price API 오류: ${data.error_message}`);
    }
    
    // 응답 구조 확인 및 가격 추출
    const price = data.data?.[0]?.prices?.[0]?.price || 0;
    console.log(`Historical price: $${price}`);
    
    return price;
  } catch (error) {
    console.error('Historical price 조회 실패:', error);
    return 0;
  }
};

// Covalent API로 지갑 트랜잭션 조회
export const getCovalentTransactions = async (walletAddress: string): Promise<TransactionRecord[]> => {
  try {
    console.log('Covalent API로 트랜잭션 조회 시작, 지갑 주소:', walletAddress);
    
    const url = `${COVALENT_BASE_URL}/1/address/${walletAddress}/transactions_v2/?key=${COVALENT_API_KEY}`;
    console.log('API URL:', url);
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Covalent API 요청 실패: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Covalent API 응답:', data);
    
    if (data.error) {
      throw new Error(`Covalent API 오류: ${data.error_message}`);
    }
    
    const transactions: TransactionRecord[] = [];
    const covalentTxs = data.data.items || [];
    
    console.log(`총 ${covalentTxs.length}개 트랜잭션 조회됨`);
    
    for (const tx of covalentTxs) {
      try {
        console.log(`\n트랜잭션 처리: ${tx.tx_hash}`);
        console.log(`  - From: ${tx.from_address}`);
        console.log(`  - To: ${tx.to_address}`);
        console.log(`  - Value: ${tx.value}`);
        console.log(`  - Value Quote: ${tx.value_quote}`);
        console.log(`  - Gas Contract: ${tx.gas_metadata.contract_address}`);
        console.log(`  - Log Events: ${tx.log_events.length}개`);
        
        // ETH 전송 트랜잭션 처리
        if (tx.value && tx.value !== '0' && tx.gas_metadata.contract_address === '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee') {
          const amount = Number(tx.value) / Math.pow(10, 18);
          const price = tx.value_quote || 0;
          
          console.log(`  → ETH 전송 감지: ${amount} ETH ($${price})`);
          
          // ETH 전송을 매수/매도로 분류
          const isFromWallet = tx.from_address.toLowerCase() === walletAddress.toLowerCase();
          const isToWallet = tx.to_address.toLowerCase() === walletAddress.toLowerCase();
          
          // 같은 지갑으로의 전송은 제외
          if (isFromWallet && isToWallet) {
            console.log(`  → ETH self-transfer 무시: ${tx.tx_hash}`);
            continue;
          }
          
          let type: 'buy' | 'sell' = 'buy';
          if (isFromWallet && !isToWallet) {
            // 지갑에서 다른 주소로 전송 = 매도
            type = 'sell';
            console.log(`  → ETH 매도: ${amount} ETH`);
          } else if (!isFromWallet && isToWallet) {
            // 다른 주소에서 지갑으로 전송 = 매수
            type = 'buy';
            console.log(`  → ETH 매수: ${amount} ETH`);
          }
          
          // 모든 ETH 전송을 거래로 취급
          transactions.push({
            tokenAddress: '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
            tokenSymbol: 'ETH',
            tokenName: 'Ethereum',
            type: type,
            amount: amount,
            price: price,
            timestamp: new Date(tx.block_signed_at).getTime() / 1000,
            txHash: tx.tx_hash,
          });
        }
        
        // ERC20 토큰 트랜잭션 처리 (log_events에서)
        for (const logEvent of tx.log_events) {
          if (logEvent.decoded && logEvent.decoded.name === 'Transfer') {
            const params = logEvent.decoded.params;
            const fromAddress = params.find((p: any) => p.name === 'from')?.value;
            const toAddress = params.find((p: any) => p.name === 'to')?.value;
            const value = params.find((p: any) => p.name === 'value')?.value;
            
            console.log(`  → ERC20 Transfer 감지: ${logEvent.sender_contract_ticker_symbol}`);
            console.log(`    - From: ${fromAddress}`);
            console.log(`    - To: ${toAddress}`);
            console.log(`    - Value: ${value}`);
            
            if (fromAddress && toAddress && value) {
              const isFromWallet = fromAddress.toLowerCase() === walletAddress.toLowerCase();
              const isToWallet = toAddress.toLowerCase() === walletAddress.toLowerCase();
              
              if (isFromWallet || isToWallet) {
                const decimals = logEvent.sender_contract_decimals || 18;
                const amount = Number(value) / Math.pow(10, decimals);
                const symbol = logEvent.sender_contract_ticker_symbol || 'UNKNOWN';
                const name = logEvent.sender_name || symbol;
                
                let type: 'buy' | 'sell' = 'buy';
                if (isFromWallet && !isToWallet) {
                  // 지갑에서 다른 주소로 전송 = 매도
                  type = 'sell';
                  console.log(`    → ERC20 매도: ${amount} ${symbol}`);
                } else if (!isFromWallet && isToWallet) {
                  // 다른 주소에서 지갑으로 전송 = 매수
                  type = 'buy';
                  console.log(`    → ERC20 매수: ${amount} ${symbol}`);
                }
                
                // 같은 지갑으로의 전송은 제외 (self-transfer)
                if (isFromWallet && isToWallet) {
                  console.log(`    → Self-transfer 무시`);
                  continue;
                }
                
                // 모든 ERC20 Transfer를 거래로 취급
                transactions.push({
                  tokenAddress: logEvent.sender_address,
                  tokenSymbol: symbol,
                  tokenName: name,
                  type: type,
                  amount: amount,
                  price: 0, // USD 환산은 불가
                  timestamp: new Date(logEvent.block_signed_at).getTime() / 1000,
                  txHash: logEvent.tx_hash,
                });
              }
            }
          }
        }
        
      } catch (txError) {
        console.warn('개별 트랜잭션 처리 실패:', txError);
        continue;
      }
    }
    
    console.log(`총 ${transactions.length}개 거래 내역 변환 완료`);
    return transactions;
    
  } catch (error) {
    console.error('Covalent API 트랜잭션 조회 실패:', error);
    throw error;
  }
};

// 선택된 토큰들만 조회하는 함수 (Covalent API 사용)
export const getSelectedTokenTransactions = async (
  walletAddress: string, 
  selectedTokens: string[]
): Promise<TransactionRecord[]> => {
  try {
    console.log('선택된 토큰 조회 시작 (Covalent API), 지갑 주소:', walletAddress);
    console.log('선택된 토큰들:', selectedTokens);
    
    // 전체 트랜잭션 조회
    const allTransactions = await getCovalentTransactions(walletAddress);
    
    // 선택된 토큰들만 필터링
    const filteredTransactions = allTransactions.filter(tx => 
      selectedTokens.includes(tx.tokenSymbol)
    );
    
    console.log(`선택된 토큰들 중 ${filteredTransactions.length}개 거래 내역 필터링 완료`);
    return filteredTransactions;
    
  } catch (error) {
    console.error('선택된 토큰 조회 실패:', error);
    throw error;
  }
};

// 기존 함수들 (호환성을 위해 유지)
export const getERC20Transactions = async (walletAddress: string): Promise<TransactionRecord[]> => {
  console.log('기존 viem 방식 대신 Covalent API 사용');
  return getCovalentTransactions(walletAddress);
};

// 사용 가능한 토큰 목록 반환 함수 (Covalent API 기반으로 업데이트)
export const getAvailableTokens = () => {
  // Covalent API는 모든 토큰을 자동으로 감지하므로, 
  // 실제로는 트랜잭션에서 발견된 토큰들을 반환하는 것이 좋습니다.
  // 여기서는 주요 토큰들만 미리 정의해둡니다.
  return [
    'ETH', 'USDT', 'USDC', 'DAI', 'BUSD', 'TUSD', 'FRAX', 'USDP', 'GUSD',
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

// Covalent 기반 단순 손실률 계산 함수 (USD 환산 없이 토큰 수량 기준)
export const calculatePnL = (transactions: TransactionRecord[]): PnLResult[] => {
  // 토큰별로 그룹화
  const tokenGroups: { [symbol: string]: TransactionRecord[] } = {};
  for (const tx of transactions) {
    if (!tokenGroups[tx.tokenSymbol]) tokenGroups[tx.tokenSymbol] = [];
    tokenGroups[tx.tokenSymbol].push(tx);
  }
  
  const results: PnLResult[] = [];
  
  for (const [symbol, txs] of Object.entries(tokenGroups)) {
    let totalBought = 0;
    let totalSold = 0;
    let currentBalance = 0;
    let lastTradeDate = '';
    
    // 시간순 정렬
    const sortedTxs = txs.sort((a, b) => a.timestamp - b.timestamp);
    
    for (const tx of sortedTxs) {
      lastTradeDate = new Date(tx.timestamp * 1000).toISOString().split('T')[0];
      
      if (tx.type === 'buy') {
        totalBought += tx.amount;
        currentBalance += tx.amount;
      } else if (tx.type === 'sell') {
        totalSold += tx.amount;
        currentBalance -= tx.amount;
      }
    }
    
    // 평균 매수가, 현재가, USD 환산 등은 불가(0)
    results.push({
      tokenSymbol: symbol,
      totalBought,
      totalSold,
      currentBalance: currentBalance < 0 ? 0 : currentBalance,
      averageBuyPrice: 0,
      averageSellPrice: 0,
      currentPrice: 0,
      totalPnL: totalBought - totalSold,
      pnlPercentage: totalBought > 0 ? ((totalBought - totalSold) / totalBought) * 100 : 0,
      lastTradeDate,
      totalBoughtUSD: 0,
      totalSoldUSD: 0,
    });
  }
  
  return results;
};

// Historical Price를 활용한 정확한 USD 기준 손실률 계산 함수
export const calculatePnLWithHistoricalPrices = async (transactions: TransactionRecord[]): Promise<PnLResult[]> => {
  console.log('=== Historical price 기반 손실률 계산 시작 ===');
  console.log(`총 ${transactions.length}개 트랜잭션 분석 시작`);
  
  // 토큰별로 그룹화
  const tokenGroups: { [symbol: string]: TransactionRecord[] } = {};
  for (const tx of transactions) {
    if (!tokenGroups[tx.tokenSymbol]) tokenGroups[tx.tokenSymbol] = [];
    tokenGroups[tx.tokenSymbol].push(tx);
  }
  
  console.log('토큰별 그룹화 결과:', Object.keys(tokenGroups));
  
  const results: PnLResult[] = [];
  
  for (const [symbol, txs] of Object.entries(tokenGroups)) {
    console.log(`\n=== ${symbol} 토큰 상세 분석 시작 ===`);
    console.log(`${symbol} 토큰 총 ${txs.length}개 트랜잭션`);
    
    let totalBoughtUSD = 0;
    let totalSoldUSD = 0;
    let totalBoughtAmount = 0;
    let totalSoldAmount = 0;
    let currentBalance = 0;
    let lastTradeDate = '';
    
    // 시간순 정렬
    const sortedTxs = txs.sort((a, b) => a.timestamp - b.timestamp);
    
    console.log(`\n1. ${symbol} 토큰 트랜잭션 상세 내역:`);
    console.log('일자 | 타입 | 수량 | 트랜잭션 해시');
    console.log('----------------------------------------');
    
    for (const tx of sortedTxs) {
      lastTradeDate = new Date(tx.timestamp * 1000).toISOString().split('T')[0];
      const txDate = new Date(tx.timestamp * 1000).toISOString().split('T')[0];
      
      console.log(`${txDate} | ${tx.type} | ${tx.amount.toFixed(6)} | ${tx.txHash.substring(0, 10)}...`);
    }
    
    console.log(`\n2. ${symbol} 토큰 일자별 가격 조회:`);
    console.log('일자 | 토큰 가격 (USD)');
    console.log('---------------------');
    
    for (const tx of sortedTxs) {
      const txDate = new Date(tx.timestamp * 1000).toISOString().split('T')[0];
      
      // Historical price 조회
      let historicalPrice = 0;
      if (tx.tokenAddress !== '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee') {
        historicalPrice = await getHistoricalPrice(tx.tokenAddress, txDate);
      } else {
        // ETH의 경우도 Historical Price API 사용
        historicalPrice = await getHistoricalPrice('0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', txDate);
      }
      
      console.log(`${txDate} | $${historicalPrice.toFixed(6)}`);
      
      // 트랜잭션에 가격 정보 저장
      tx.price = historicalPrice;
    }
    
    console.log(`\n3. ${symbol} 토큰 매수/매도 금액 계산:`);
    console.log('일자 | 타입 | 수량 | 가격 | USD 금액');
    console.log('----------------------------------------');
    
    for (const tx of sortedTxs) {
      const txDate = new Date(tx.timestamp * 1000).toISOString().split('T')[0];
      const usdAmount = tx.amount * tx.price;
      
      console.log(`${txDate} | ${tx.type} | ${tx.amount.toFixed(6)} | $${tx.price.toFixed(6)} | $${usdAmount.toFixed(2)}`);
      
      if (tx.type === 'buy') {
        totalBoughtAmount += tx.amount;
        totalBoughtUSD += usdAmount;
        currentBalance += tx.amount;
      } else if (tx.type === 'sell') {
        // 매도 시 현재 보유량을 초과하지 않도록 제한
        const availableToSell = Math.min(tx.amount, currentBalance);
        if (availableToSell > 0) {
          totalSoldAmount += availableToSell;
          totalSoldUSD += availableToSell * tx.price;
          currentBalance -= availableToSell;
          console.log(`  → 실제 매도: ${availableToSell.toFixed(6)} (보유량 초과로 제한됨)`);
        } else {
          console.log(`  → 매도 무시: 보유량 부족 (보유: ${currentBalance.toFixed(6)}, 매도시도: ${tx.amount.toFixed(6)})`);
        }
      }
    }
    
    // 평균 매수가, 평균 매도가 계산
    const averageBuyPrice = totalBoughtAmount > 0 ? totalBoughtUSD / totalBoughtAmount : 0;
    const averageSellPrice = totalSoldAmount > 0 ? totalSoldUSD / totalSoldAmount : 0;
    
    // 현재 가격 조회 (최신 날짜 기준)
    let currentPrice = 0;
    if (lastTradeDate && txs.length > 0) {
      const latestTx = txs[0];
      if (latestTx.tokenAddress !== '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee') {
        currentPrice = await getHistoricalPrice(latestTx.tokenAddress, lastTradeDate);
      } else {
        // ETH의 경우도 Historical Price API 사용
        currentPrice = await getHistoricalPrice('0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', lastTradeDate);
      }
    }
    
    // USD 기준 손실률 계산
    const totalPnL = totalBoughtUSD - totalSoldUSD;
    const pnlPercentage = totalBoughtUSD > 0 ? (totalPnL / totalBoughtUSD) * 100 : 0;
    
    console.log(`\n4. ${symbol} 토큰 손실률 계산 결과:`);
    console.log('----------------------------------------');
    console.log(`총 매수 수량: ${totalBoughtAmount.toFixed(6)} ${symbol}`);
    console.log(`총 매도 수량: ${totalSoldAmount.toFixed(6)} ${symbol}`);
    console.log(`총 매수 금액: $${totalBoughtUSD.toFixed(2)}`);
    console.log(`총 매도 금액: $${totalSoldUSD.toFixed(2)}`);
    console.log(`평균 매수가: $${averageBuyPrice.toFixed(6)}`);
    console.log(`평균 매도가: $${averageSellPrice.toFixed(6)}`);
    console.log(`현재 가격: $${currentPrice.toFixed(6)}`);
    console.log(`현재 보유량: ${currentBalance.toFixed(6)} ${symbol}`);
    console.log(`총 손익: $${totalPnL.toFixed(2)}`);
    console.log(`손실률: ${pnlPercentage.toFixed(2)}%`);
    console.log(`마지막 거래일: ${lastTradeDate}`);
    
    // 보유량 검증
    if (currentBalance < 0) {
      console.log(`⚠️  경고: 현재 보유량이 음수입니다. 데이터 오류 가능성 있음.`);
      currentBalance = 0;
    }
    
    console.log('----------------------------------------');
    
    results.push({
      tokenSymbol: symbol,
      totalBought: totalBoughtAmount,
      totalSold: totalSoldAmount,
      currentBalance: currentBalance < 0 ? 0 : currentBalance,
      averageBuyPrice,
      averageSellPrice,
      currentPrice,
      totalPnL,
      pnlPercentage,
      lastTradeDate,
      totalBoughtUSD,
      totalSoldUSD,
    });
  }
  
  console.log('\n=== 전체 분석 완료 ===');
  console.log('최종 결과:', results);
  
  return results;
};

// GoldRush API를 활용한 과거 가격 기반 손실률 계산 예시 (향후 적용용)
/*
export const calculatePnLWithHistoricalPrices = async (transactions: TransactionRecord[]): Promise<PnLResult[]> => {
  // GoldRush API를 사용하여 각 트랜잭션 시점의 가격을 조회
  // 이를 통해 정확한 USD 기준 손실률 계산 가능
  
  const results: PnLResult[] = [];
  
  for (const tx of transactions) {
    // GoldRush API로 해당 날짜의 토큰 가격 조회
    const historicalPrice = await getHistoricalPrice(tx.tokenAddress, tx.timestamp);
    
    // USD 기준 손실률 계산
    // ... 구현 예정
  }
  
  return results;
};

const getHistoricalPrice = async (tokenAddress: string, timestamp: number): Promise<number> => {
  const date = new Date(timestamp * 1000).toISOString().split('T')[0];
  const url = `${GOLDRUSH_BASE_URL}/v1/historical-price/${tokenAddress}?date=${date}&api_key=${GOLDRUSH_API_KEY}`;
  
  const response = await fetch(url);
  const data = await response.json();
  
  return data.price || 0;
};
*/ 