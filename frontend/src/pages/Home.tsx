import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAccount } from 'wagmi';
import WalletConnect from '../components/WalletConnect';

const Home: React.FC = () => {
  const { address, isConnected } = useAccount();
  const navigate = useNavigate();

  const handleLossCheck = () => {
    navigate('/loss-check');
  };

  return (
    <div className="home">
      <header className="home-header">
        <h1>🪦 Crypto Graves</h1>
        <p>Web3 자산 손실을 희화화하고 기록하는 DApp</p>
      </header>

      <main className="home-main">
        <div className="wallet-section">
          <h2>지갑 연결</h2>
          <WalletConnect />
        </div>

        {isConnected && (
          <div className="connected-section">
            <div className="wallet-address">
              <h3>연결된 지갑</h3>
              <p className="address">{address}</p>
            </div>
            
            <div className="action-section">
              <button 
                onClick={handleLossCheck}
                className="loss-check-button"
              >
                내 손실 확인하기
              </button>
            </div>
          </div>
        )}

        {!isConnected && (
          <div className="welcome-section">
            <h3>시작하기</h3>
            <p>지갑을 연결하여 손실 내역을 확인하고 NFT를 발행해보세요!</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default Home; 