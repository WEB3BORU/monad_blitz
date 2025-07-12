import React from 'react';
import './LossLeaderboardCard.css';

interface Props {
  rank: number;
  profile: string;
  address: string;
  lossRate: number;
  lossAmount: number;
  topTickers: string[];
  lastTradeDate: string;
}

const rankClass = (rank: number) => {
  if (rank === 1) return 'card-gold';
  if (rank === 2) return 'card-silver';
  if (rank === 3) return 'card-bronze';
  return '';
};

const LossLeaderboardCard: React.FC<Props> = ({ rank, profile, address, lossRate, lossAmount, topTickers, lastTradeDate }) => {
  return (
    <div className={`loss-leaderboard-card ${rankClass(rank)}`}>
      <div className="card-header">
        <span className={`rank-badge rank-${rank}`}>{rank}</span>
        <span className="profile-circle">{profile}</span>
        <span className="address">{address}</span>
      </div>
      <div className="card-main">
        <div className="loss-rate">{lossRate}%</div>
        <div className="loss-amount">${lossAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
        <div className="top-tickers">
          {topTickers.map(ticker => (
            <span className="ticker-badge" key={ticker}>{ticker}</span>
          ))}
        </div>
      </div>
      <div className="card-footer">
        <span className="last-trade">마지막 거래: {lastTradeDate}</span>
      </div>
    </div>
  );
};

export default LossLeaderboardCard; 