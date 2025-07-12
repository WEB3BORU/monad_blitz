import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { WagmiProvider } from 'wagmi';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { config } from './config/wagmi';
import Home from './pages/Home';
import LossCheck from './pages/LossCheck';
import './App.css';

const queryClient = new QueryClient();

function App() {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/loss-check" element={<LossCheck />} />
            </Routes>
          </div>
        </Router>
      </QueryClientProvider>
    </WagmiProvider>
  );
}

export default App;
