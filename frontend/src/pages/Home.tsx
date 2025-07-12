import React from 'react';
import { useNavigate } from 'react-router-dom';
import HeaderWallet from '../components/HeaderWallet';
import NftCarouselDashboard from '../components/NftCarouselDashboard';
import LossSummaryDashboard from '../components/LossSummaryDashboard';
import '../App.css';

const Home: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div>
      <HeaderWallet />
      <main style={{ maxWidth: 900, margin: '0 auto', padding: '0 0 32px 0' }}>
        <NftCarouselDashboard />
        <LossSummaryDashboard />
        <button className="main-action-btn" onClick={() => navigate('/loss-check')}>
          내 손실률 확인
        </button>
      </main>
    </div>
  );
};

export default Home; 