import React from 'react';
import { useNavigate } from 'react-router-dom';
import HeaderWallet from '../components/HeaderWallet';
import NftCarouselDashboard from '../components/NftCarouselDashboard';
import LossSummaryDashboard from '../components/LossSummaryDashboard';
import LossLeaderboardDashboard from '../components/LossLeaderboardDashboard';
import '../App.css';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const dummyWallets = [
    {
      address: '0x977a...1107b',
      lossAmount: 1250,
      topTickers: ['ETH', 'PEPE', 'BNB'],
    },
    {
      address: '0xA1b2...C3d4',
      lossAmount: 980,
      topTickers: ['BTC', 'ARB', 'DOGE'],
    },
    {
      address: '0xFfE2...9aBc',
      lossAmount: 2100,
      topTickers: ['SOL', 'MATIC', 'OP'],
    },
    {
      address: '0x1234...5678',
      lossAmount: 450,
      topTickers: ['XRP', 'SHIB', 'UNI'],
    },
    {
      address: '0x9e8d...7c6b',
      lossAmount: 3200,
      topTickers: ['AVAX', 'LINK', 'SUI'],
    },
    {
      address: '0xBEEF...CAFE',
      lossAmount: 1750,
      topTickers: ['DOGE', 'PEPE', 'ARB'],
    },
    {
      address: '0xDEAD...BEEF',
      lossAmount: 600,
      topTickers: ['BTC', 'ETH', 'SOL'],
    },
  ];
  return (
    <div>
      <HeaderWallet />
      <main style={{ maxWidth: 900, margin: '0 auto', padding: '0 0 32px 0' }}>
        <NftCarouselDashboard />
        <LossLeaderboardDashboard />
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: 32 }}>
          <button className="main-action-btn" onClick={() => navigate('/loss-check')}>
            내 손실률 확인
          </button>
        </div>
      </main>
    </div>
  );
};

export default Home; 