import React from 'react';
import './LossSummaryDashboard.css';

const dummyWallet = '0x977a...1107b';
const dummyLoss = '₩1,250,000';
const dummyTopTickers = [
  { symbol: 'ETH', loss: '₩800,000' },
  { symbol: 'PEPE', loss: '₩300,000' },
  { symbol: 'BNB', loss: '₩150,000' },
];

const LossSummaryDashboard: React.FC = () => {
  return (
    <div className="loss-summary-dashboard">
      <div className="summary-row">
        <div className="summary-item">
          <div className="summary-label">지갑주소</div>
          <div className="summary-value">{dummyWallet}</div>
        </div>
        <div className="summary-item">
          <div className="summary-label">손실금액</div>
          <div className="summary-value loss">{dummyLoss}</div>
        </div>
        <div className="summary-item">
          <div className="summary-label">상위 손실 티커</div>
          <div className="summary-value">
            {dummyTopTickers.map(t => (
              <span className="top-ticker" key={t.symbol}>{t.symbol} <span className="ticker-loss">{t.loss}</span></span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LossSummaryDashboard; 