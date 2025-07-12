import axios from 'axios';

// API 기본 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 손실 내역 조회 API
export const getLossHistory = async (walletAddress: string) => {
  try {
    const response = await api.get(`/api/loss-check/${walletAddress}`);
    return response.data;
  } catch (error) {
    console.error('손실 내역 조회 실패:', error);
    throw error;
  }
};

// NFT 발행 API
export const mintNFT = async (walletAddress: string, tickerData: any) => {
  try {
    const response = await api.post('/api/mint-nft', {
      walletAddress,
      tickerData,
    });
    return response.data;
  } catch (error) {
    console.error('NFT 발행 실패:', error);
    throw error;
  }
};

export default api; 