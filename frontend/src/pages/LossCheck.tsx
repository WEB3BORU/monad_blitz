import React, { useState, useEffect } from 'react';
import { useAccount } from 'wagmi';
import { useNavigate } from 'react-router-dom';
import { 
  getERC20Transactions, 
  getSelectedTokenTransactions,
  getAvailableTokens,
  calculatePnL,
  calculatePnLWithHistoricalPrices
} from '../services/transactionAnalysis';
import '../App.css';

interface TickerData {
  symbol: string;
  name: string;
  lossAmount: number;
  lossPercentage: number;
  lastTradeDate: string;
  currentBalance: number;
  averageBuyPrice: number;
  averageSellPrice: number;
  currentPrice: number;
  totalBought: number;
  totalSold: number;
  totalBoughtUSD: number;
  totalSoldUSD: number;
}

const LossCheck: React.FC = () => {
  const { address, isConnected } = useAccount();
  const navigate = useNavigate();
  const [tickers, setTickers] = useState<TickerData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisMode, setAnalysisMode] = useState<'dummy' | 'real'>('dummy');
  
  // 코인 선택 관련 상태
  const [availableTokens, setAvailableTokens] = useState<string[]>([]);
  const [selectedTokens, setSelectedTokens] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showTokenSelector, setShowTokenSelector] = useState(false);

  useEffect(() => {
    if (!isConnected) {
      navigate('/');
      return;
    }

    // 사용 가능한 토큰 목록 로드
    const tokens = getAvailableTokens();
    setAvailableTokens(tokens);

    // 화면 진입 시에는 더미 데이터만 표시 (API 호출 중지)
    fetchDummyData();
  }, [isConnected, address, navigate]);

  const fetchDummyData = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('더미 데이터 로딩 시작');
      
      // 기존 더미 데이터
      const dummyTickers = [
        {
          symbol: 'PEPE',
          name: 'Pepe',
          lossAmount: -1500,
          lossPercentage: -25.5,
          lastTradeDate: '2025-03-21',
          currentBalance: 0.05,
          averageBuyPrice: 30000,
          averageSellPrice: 30000,
          currentPrice: 45000,
          totalBought: 0.1,
          totalSold: 0.05,
          totalBoughtUSD: 3000,
          totalSoldUSD: 1500
        },
        {
          symbol: 'LINK',
          name: 'Chainlink',
          lossAmount: -800,
          lossPercentage: -18.2,
          lastTradeDate: '2025-07-06',
          currentBalance: 2.5,
          averageBuyPrice: 2000,
          averageSellPrice: 2000,
          currentPrice: 3200,
          totalBought: 5,
          totalSold: 2.5,
          totalBoughtUSD: 10000,
          totalSoldUSD: 5000
        },
        {
          symbol: 'ETH',
          name: 'Ethereum',
          lossAmount: -300,
          lossPercentage: -15.0,
          lastTradeDate: '2025-07-12',
          currentBalance: 50,
          averageBuyPrice: 100,
          averageSellPrice: 100,
          currentPrice: 55,
          totalBought: 100,
          totalSold: 50,
          totalBoughtUSD: 10000,
          totalSoldUSD: 2750
        }
      ];

      // 더미 데이터에 현재 가격 조회 추가 코드 제거
      setTickers(dummyTickers);
      console.log('더미 데이터 로딩 완료:', dummyTickers);
    } catch (err) {
      console.error('더미 데이터 로딩 실패:', err);
      setError('데이터를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchRealTransactions = async () => {
    if (!address) return;

    setLoading(true);
    setError(null);

    try {
      console.log('=== 실제 트랜잭션 분석 시작 ===');
      console.log('지갑 주소:', address);
      
      let transactions;
      
      // 선택된 토큰이 있으면 선택된 토큰만 조회, 없으면 전체 조회
      if (selectedTokens.length > 0) {
        console.log('선택된 토큰들만 조회:', selectedTokens);
        transactions = await getSelectedTokenTransactions(address, selectedTokens);
      } else {
        console.log('전체 토큰 조회');
        transactions = await getERC20Transactions(address);
      }
      
      console.log('=== 조회된 트랜잭션 요약 ===');
      console.log(`총 ${transactions.length}개 트랜잭션 조회됨`);
      
      // 토큰별 트랜잭션 수 요약
      const tokenSummary: { [symbol: string]: number } = {};
      transactions.forEach(tx => {
        tokenSummary[tx.tokenSymbol] = (tokenSummary[tx.tokenSymbol] || 0) + 1;
      });
      console.log('토큰별 트랜잭션 수:', tokenSummary);
      
      // PnL 계산 (Historical Price 기반)
      console.log('\n=== Historical Price 기반 손실률 계산 시작 ===');
      const pnlResults = await calculatePnLWithHistoricalPrices(transactions);
      console.log('=== Historical Price 기반 PnL 계산 완료 ===');
      console.log('최종 PnL 결과:', pnlResults);
      
              // UI용 데이터 변환
        const tickerData: TickerData[] = pnlResults.map(result => ({
          symbol: result.tokenSymbol,
          name: result.tokenSymbol,
          lossAmount: result.totalPnL,
          lossPercentage: result.pnlPercentage,
          lastTradeDate: result.lastTradeDate || new Date().toISOString().split('T')[0],
          currentBalance: result.currentBalance,
          averageBuyPrice: result.averageBuyPrice,
          averageSellPrice: result.averageSellPrice,
          currentPrice: result.currentPrice,
          totalBought: result.totalBought,
          totalSold: result.totalSold,
          totalBoughtUSD: result.totalBoughtUSD,
          totalSoldUSD: result.totalSoldUSD
        }));

      console.log('최종 티커 데이터:', tickerData);
      setTickers(tickerData);
    } catch (err) {
      console.error('실제 트랜잭션 조회 실패:', err);
      setError('실제 트랜잭션을 불러올 수 없습니다. 더미 데이터로 표시합니다.');
      fetchDummyData();
    } finally {
      setLoading(false);
    }
  };

  const handleMintNFT = async (ticker: TickerData) => {
    try {
      // NFT 발행에 필요한 정보 매핑 (snake_case 컬럼명)
      const mintPayload = {
        wallet_address: String(address),
        ticker: String(ticker.symbol),
        avg_buyprice: ticker.averageBuyPrice.toFixed(2),
        avg_sellprice: ticker.averageSellPrice.toFixed(2),
        current_price: ticker.currentPrice.toFixed(2),
        total_buyprice: ticker.totalBoughtUSD.toFixed(2),
        total_sellprice: ticker.totalSoldUSD.toFixed(2),
      };
      console.log('[NFT 민트 요청 페이로드]', mintPayload);
      alert(`${ticker.symbol} NFT 발행이 시작되었습니다!`);
    } catch (err) {
      console.error('NFT 발행 실패:', err);
      alert('NFT 발행에 실패했습니다.');
    }
  };

  // 코인 선택 관련 함수들
  const handleTokenSelect = (token: string) => {
    if (selectedTokens.includes(token)) {
      setSelectedTokens(selectedTokens.filter(t => t !== token));
    } else {
      setSelectedTokens([...selectedTokens, token]);
    }
  };

  const handleSelectAll = () => {
    setSelectedTokens(availableTokens);
  };

  const handleClearSelection = () => {
    setSelectedTokens([]);
  };

  const handleAnalyzeSelected = () => {
    if (selectedTokens.length === 0) {
      // 선택된 토큰이 없으면 전체 토큰 분석
      console.log('선택된 토큰이 없어 전체 토큰을 분석합니다.');
    } else {
      console.log('선택된 토큰들을 분석합니다:', selectedTokens);
    }
    
    setShowTokenSelector(false);
    setAnalysisMode('real'); // 분석 모드를 real로 변경
    fetchRealTransactions();
  };

  const filteredTokens = availableTokens.filter(token =>
    token.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isConnected) {
    return null;
  }

  return (
    <div style={{ minHeight: '100vh', background: '#191c23' }}>
      {/* 좌측 상단 뒤로 가기 버튼 */}
      <button className="btn-main losscheck-back-small" onClick={() => navigate('/')}>
        ←
      </button>
      {/* 중앙 상단 '내 지갑 손실률 조회' 버튼 */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: 32, marginBottom: 32 }}>
        <button className="btn-main losscheck-main-btn">내 지갑 손실률 조회</button>
      </div>
      {/* 손실률 카드 리스트 */}
      <div className="losscheck-list">
        {tickers.map(ticker => (
          <div className="losscheck-card" key={ticker.symbol}>
            <div style={{fontWeight:700, fontSize:'1.1rem'}}>{ticker.symbol}</div>
            <div style={{color:'#bdbdbd', fontSize:'0.95rem'}}>{ticker.name}</div>
            <div>손실: <span className="amount">${ticker.lossAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>
            <div>{ticker.lossPercentage.toFixed(2)}%</div>
            <div>마지막 거래: {ticker.lastTradeDate}</div>
            <button className="btn-main btn-nft" onClick={() => handleMintNFT(ticker)}>NFT 발행</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LossCheck; 