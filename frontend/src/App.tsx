import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { WagmiProvider } from 'wagmi';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { config } from './config/wagmi';
import Home from './pages/Home';
import LossCheck from './pages/LossCheck';

const queryClient = new QueryClient();

const App: React.FC = () => {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/loss-check" element={<LossCheck />} />
          </Routes>
        </Router>
      </QueryClientProvider>
    </WagmiProvider>
  );
};

export default App;
