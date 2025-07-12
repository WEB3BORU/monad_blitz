import { createConfig, http } from 'wagmi';
import { mainnet, polygon } from 'wagmi/chains';
import { injected, metaMask } from 'wagmi/connectors';

// Monad 체인 설정 (테스트넷)
const monadTestnet = {
  id: 1337,
  name: 'Monad Testnet',
  network: 'monad-testnet',
  nativeCurrency: {
    decimals: 18,
    name: 'MON',
    symbol: 'MON',
  },
  rpcUrls: {
    public: { http: ['https://rpc.testnet.monad.xyz'] },
    default: { http: ['https://rpc.testnet.monad.xyz'] },
  },
  blockExplorers: {
    default: { name: 'Monad Explorer', url: 'https://explorer.testnet.monad.xyz' },
  },
} as const;

export const config = createConfig({
  chains: [monadTestnet, mainnet, polygon],
  connectors: [
    injected(),
    metaMask(),
  ],
  transports: {
    [monadTestnet.id]: http(),
    [mainnet.id]: http(),
    [polygon.id]: http(),
  },
});

export { monadTestnet }; 