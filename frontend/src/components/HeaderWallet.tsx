import React from 'react';
import './HeaderWallet.css';

const dummyWallet = '0x977a...1107b';
const isConnected = true; // 실제 연동 시 상태로 대체

const HeaderWallet: React.FC = () => {
  return (
    <header className="header-wallet">
      <div className="header-title">Crypto Graves</div>
      <div className="header-wallet-info">
        {isConnected ? (
          <span className="wallet-address">{dummyWallet}</span>
        ) : (
          <button className="connect-btn">지갑 연결</button>
        )}
      </div>
    </header>
  );
};

export default HeaderWallet; 