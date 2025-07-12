import React from 'react';
import { useAccount, useConnect, useDisconnect } from 'wagmi';
import { injected, metaMask } from 'wagmi/connectors';

const WalletConnect: React.FC = () => {
  const { address, isConnected } = useAccount();
  const { connect, isPending } = useConnect();
  const { disconnect } = useDisconnect();

  const handleConnect = () => {
    connect({ connector: injected() });
  };

  const handleDisconnect = () => {
    disconnect();
  };

  return (
    <div className="wallet-connect">
      {!isConnected ? (
        <button 
          onClick={handleConnect}
          disabled={isPending}
          className="connect-button"
        >
          {isPending ? '연결 중...' : '지갑 연결'}
        </button>
      ) : (
        <div className="wallet-info">
          <span className="address">
            {address?.slice(0, 6)}...{address?.slice(-4)}
          </span>
          <button 
            onClick={handleDisconnect}
            className="disconnect-button"
          >
            연결 해제
          </button>
        </div>
      )}
    </div>
  );
};

export default WalletConnect; 