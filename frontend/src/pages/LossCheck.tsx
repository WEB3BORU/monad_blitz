import React, { useState, useEffect } from 'react';
import { useAccount } from 'wagmi';
import { useNavigate } from 'react-router-dom';
import { 
  getERC20Transactions, 
  getSelectedTokenTransactions,
  getAvailableTokens,
  getCurrentPrice, 
  calculatePnL 
} from '../services/transactionAnalysis';

interface TickerData {
  symbol: string;
  name: string;
  lossAmount: number;
  lossPercentage: number;
  lastTradeDate: string;
  currentBalance: number;
  averageBuyPrice: number;
  currentPrice: number;
  totalBought: number;
  totalSold: number;
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

    if (analysisMode === 'real') {
      fetchRealTransactions();
    } else {
      fetchDummyData();
    }
  }, [isConnected, address, navigate, analysisMode]);

  const fetchDummyData = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('더미 데이터 로딩 시작');
      
      // 기존 더미 데이터
      const dummyTickers = [
        {
          symbol: 'BTC',
          name: 'Bitcoin',
          lossAmount: -1500,
          lossPercentage: -25.5,
          lastTradeDate: '2024-01-15',
          currentBalance: 0.05,
          averageBuyPrice: 30000,
          currentPrice: 45000,
          totalBought: 0.1,
          totalSold: 0.05
        },
        {
          symbol: 'ETH',
          name: 'Ethereum',
          lossAmount: -800,
          lossPercentage: -18.2,
          lastTradeDate: '2024-01-20',
          currentBalance: 2.5,
          averageBuyPrice: 2000,
          currentPrice: 3200,
          totalBought: 5,
          totalSold: 2.5
        },
        {
          symbol: 'SOL',
          name: 'Solana',
          lossAmount: -300,
          lossPercentage: -45.0,
          lastTradeDate: '2024-01-25',
          currentBalance: 50,
          averageBuyPrice: 100,
          currentPrice: 55,
          totalBought: 100,
          totalSold: 50
        }
      ];

      // 더미 데이터에 현재 가격 조회 추가
      const tickersWithPrices = await Promise.all(
        dummyTickers.map(async (ticker) => {
          try {
            console.log(`${ticker.symbol} 현재 가격 조회 중...`);
            const currentPrice = await getCurrentPrice(ticker.symbol);
            console.log(`${ticker.symbol} 현재 가격: ${currentPrice}`);
            
            return {
              ...ticker,
              currentPrice: currentPrice || ticker.currentPrice // API 실패 시 기존 가격 사용
            };
          } catch (error) {
            console.warn(`${ticker.symbol} 가격 조회 실패:`, error);
            return ticker;
          }
        })
      );

      console.log('더미 데이터 로딩 완료:', tickersWithPrices);
      setTickers(tickersWithPrices);
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
      console.log('실제 트랜잭션 분석 시작');
      
      let transactions;
      
      // 선택된 토큰이 있으면 선택된 토큰만 조회, 없으면 전체 조회
      if (selectedTokens.length > 0) {
        console.log('선택된 토큰들만 조회:', selectedTokens);
        transactions = await getSelectedTokenTransactions(address, selectedTokens);
      } else {
        console.log('전체 토큰 조회');
        transactions = await getERC20Transactions(address);
      }
      
      console.log('조회된 트랜잭션:', transactions);
      
      // PnL 계산
      const pnlResults = calculatePnL(transactions);
      console.log('PnL 계산 결과:', pnlResults);
      
      // 현재 가격 조회 및 데이터 변환
      const tickerData: TickerData[] = [];
      
      for (const result of pnlResults) {
        try {
          console.log(`${result.tokenSymbol} 현재 가격 조회 중...`);
          // CoinGecko API로 현재 가격 조회
          const currentPrice = await getCurrentPrice(result.tokenSymbol);
          console.log(`${result.tokenSymbol} 현재 가격: ${currentPrice}`);
          
          tickerData.push({
            symbol: result.tokenSymbol,
            name: result.tokenSymbol,
            lossAmount: result.totalPnL,
            lossPercentage: result.pnlPercentage,
            lastTradeDate: new Date().toISOString().split('T')[0], // 실제로는 마지막 거래 날짜
            currentBalance: result.currentBalance,
            averageBuyPrice: result.averageBuyPrice,
            currentPrice: currentPrice,
            totalBought: result.totalBought,
            totalSold: result.totalSold
          });
        } catch (priceError) {
          console.warn(`${result.tokenSymbol} 가격 조회 실패:`, priceError);
          // 가격 조회 실패 시에도 기본 데이터는 추가
          tickerData.push({
            symbol: result.tokenSymbol,
            name: result.tokenSymbol,
            lossAmount: result.totalPnL,
            lossPercentage: result.pnlPercentage,
            lastTradeDate: new Date().toISOString().split('T')[0],
            currentBalance: result.currentBalance,
            averageBuyPrice: result.averageBuyPrice,
            currentPrice: 0,
            totalBought: result.totalBought,
            totalSold: result.totalSold
          });
        }
      }

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
      // NFT 발행 로직 (스마트 컨트랙트 호출)
      console.log('NFT 발행:', ticker.symbol);
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
      alert('분석할 코인을 선택해주세요.');
      return;
    }
    setShowTokenSelector(false);
    fetchRealTransactions();
  };

  const filteredTokens = availableTokens.filter(token =>
    token.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isConnected) {
    return null;
  }

  return (
    <div className="loss-check">
      <header className="loss-check-header">
        <button 
          onClick={() => navigate('/')}
          className="back-button"
        >
          ← 뒤로 가기
        </button>
        <h1>내 손실 확인</h1>
        <p className="wallet-address">지갑: {address}</p>
        
        <div className="analysis-mode-selector">
          <button 
            onClick={() => setAnalysisMode('dummy')}
            className={analysisMode === 'dummy' ? 'active' : ''}
          >
            더미 데이터
          </button>
          <button 
            onClick={() => setAnalysisMode('real')}
            className={analysisMode === 'real' ? 'active' : ''}
          >
            실제 트랜잭션
          </button>
        </div>

        {/* 코인 선택 UI */}
        {analysisMode === 'real' && (
          <div className="token-selector-section">
            <div className="token-selector-header">
              <h3>분석할 코인 선택</h3>
              <div className="token-selector-buttons">
                <button 
                  onClick={() => setShowTokenSelector(!showTokenSelector)}
                  className="toggle-selector-btn"
                >
                  {showTokenSelector ? '선택창 닫기' : '코인 선택'}
                </button>
                {selectedTokens.length > 0 && (
                  <button 
                    onClick={handleAnalyzeSelected}
                    className="analyze-selected-btn"
                  >
                    선택된 코인 분석 ({selectedTokens.length}개)
                  </button>
                )}
              </div>
            </div>

            {showTokenSelector && (
              <div className="token-selector">
                <div className="token-selector-controls">
                  <input
                    type="text"
                    placeholder="코인 검색..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="token-search"
                  />
                  <div className="token-selector-actions">
                    <button onClick={handleSelectAll} className="select-all-btn">
                      전체 선택
                    </button>
                    <button onClick={handleClearSelection} className="clear-btn">
                      선택 해제
                    </button>
                  </div>
                </div>

                <div className="selected-tokens">
                  {selectedTokens.length > 0 && (
                    <div className="selected-tokens-list">
                      <h4>선택된 코인 ({selectedTokens.length}개):</h4>
                      <div className="selected-tokens-chips">
                        {selectedTokens.map(token => (
                          <span key={token} className="token-chip">
                            {token}
                            <button 
                              onClick={() => handleTokenSelect(token)}
                              className="remove-token-btn"
                            >
                              ×
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="token-list">
                  <h4>사용 가능한 코인:</h4>
                  <div className="token-grid">
                    {filteredTokens.map(token => (
                      <button
                        key={token}
                        onClick={() => handleTokenSelect(token)}
                        className={`token-item ${selectedTokens.includes(token) ? 'selected' : ''}`}
                      >
                        {token}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {selectedTokens.length > 0 && !showTokenSelector && (
              <div className="selected-tokens-summary">
                <p>선택된 코인: {selectedTokens.join(', ')}</p>
                <button onClick={handleAnalyzeSelected} className="analyze-btn">
                  분석 시작
                </button>
              </div>
            )}
          </div>
        )}
      </header>

      <main className="loss-check-main">
        {loading ? (
          <div className="loading">
            <p>
              {analysisMode === 'real' 
                ? '실제 트랜잭션을 분석하고 있습니다...' 
                : '손실 내역을 조회하고 있습니다...'
              }
            </p>
          </div>
        ) : error ? (
          <div className="error">
            <p>{error}</p>
          </div>
        ) : (
          <div className="tickers-list">
            <h2>손실 내역</h2>
            {tickers.length === 0 ? (
              <p className="no-losses">손실 내역이 없습니다. 다행이네요! 🎉</p>
            ) : (
              <div className="tickers-grid">
                {tickers.map((ticker) => (
                  <div key={ticker.symbol} className="ticker-card">
                    <div className="ticker-header">
                      <h3>{ticker.symbol}</h3>
                      <span className="ticker-name">{ticker.name}</span>
                    </div>
                    
                    <div className="ticker-details">
                      <div className="loss-info">
                        <p className="loss-amount">
                          손실: {ticker.lossAmount.toLocaleString()} USDT
                        </p>
                        <p className="loss-percentage">
                          {ticker.lossPercentage.toFixed(2)}%
                        </p>
                      </div>
                      
                      {analysisMode === 'real' && (
                        <div className="detailed-info">
                          <p>보유 수량: {ticker.currentBalance.toFixed(4)}</p>
                          <p>평균 매수가: ${ticker.averageBuyPrice.toFixed(2)}</p>
                          <p>현재 가격: ${ticker.currentPrice.toFixed(2)}</p>
                          <p>총 매수: {ticker.totalBought.toFixed(4)}</p>
                          <p>총 매도: {ticker.totalSold.toFixed(4)}</p>
                        </div>
                      )}
                      
                      <p className="last-trade">
                        마지막 거래: {ticker.lastTradeDate}
                      </p>
                    </div>

                    <button 
                      onClick={() => handleMintNFT(ticker)}
                      className="mint-nft-button"
                    >
                      NFT 발행
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default LossCheck; 