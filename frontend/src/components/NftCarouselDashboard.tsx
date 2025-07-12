import React from 'react';
import pepeImg from '../assets/pepe_graves.png';
import shibImg from '../assets/shib_graves.png';
import ethImg from '../assets/eth_graves.png';
import './NftCarouselDashboard.css';

const nfts = [
  { name: 'PEPE Graves', image: pepeImg, desc: 'PEPE NFT', id: 1 },
  { name: 'SHIB Graves', image: shibImg, desc: 'SHIB NFT', id: 2 },
  { name: 'ETH Graves', image: ethImg, desc: 'ETH NFT', id: 3 },
];

const NftCarouselDashboard: React.FC = () => {
  return (
    <div className="nft-carousel">
      {nfts.map((nft) => (
        <div className="nft-card" key={nft.id}>
          <img src={nft.image} alt={nft.name} className="nft-card-image-full" />
          <div className="nft-card-meta">
            <div className="nft-name-small">{nft.name}</div>
            <div className="nft-desc-small">{nft.desc}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default NftCarouselDashboard; 