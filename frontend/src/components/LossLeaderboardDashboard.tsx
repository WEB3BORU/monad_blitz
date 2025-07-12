import React from 'react';
import LossLeaderboardCard from './LossLeaderboardCard';
import './LossLeaderboardDashboard.css';

const leaderboardData = [
  {
    rank: 1,
    address: '0x977a...1107b',
    lossRate: -52.3,
    lossAmount: 3250,
    topTickers: ['ETH', 'PEPE', 'BNB'],
    lastTradeDate: '2025-07-12',
    profile: 'A',
  },
  {
    rank: 2,
    address: '0xA1b2...C3d4',
    lossRate: -48.1,
    lossAmount: 2980,
    topTickers: ['BTC', 'ARB', 'DOGE'],
    lastTradeDate: '2025-07-10',
    profile: 'B',
  },
  {
    rank: 3,
    address: '0xFfE2...9aBc',
    lossRate: -44.7,
    lossAmount: 2100,
    topTickers: ['SOL', 'MATIC', 'OP'],
    lastTradeDate: '2025-07-09',
    profile: 'C',
  },
  {
    rank: 4,
    address: '0x1234...5678',
    lossRate: -39.2,
    lossAmount: 1450,
    topTickers: ['XRP', 'SHIB', 'UNI'],
    lastTradeDate: '2025-07-08',
    profile: 'D',
  },
  {
    rank: 5,
    address: '0x9e8d...7c6b',
    lossRate: -36.5,
    lossAmount: 1200,
    topTickers: ['AVAX', 'LINK', 'SUI'],
    lastTradeDate: '2025-07-07',
    profile: 'E',
  },
  {
    rank: 6,
    address: '0xBEEF...CAFE',
    lossRate: -33.8,
    lossAmount: 950,
    topTickers: ['DOGE', 'PEPE', 'ARB'],
    lastTradeDate: '2025-07-06',
    profile: 'F',
  },
];

const LossLeaderboardDashboard: React.FC = () => {
  return (
    <div className="loss-leaderboard-grid">
      {leaderboardData.map((item) => (
        <LossLeaderboardCard key={item.address} {...item} />
      ))}
    </div>
  );
};

export default LossLeaderboardDashboard; 