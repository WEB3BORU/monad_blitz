import React, { useEffect, useState } from 'react';
import { usePublicClient } from 'wagmi';
import { parseAbi, decodeFunctionResult } from 'viem';
import './NftCarouselDashboard.css';

const NFT_CONTRACT = '0xCCE694Cd2e6939F04b3efCb55BdaCc607AdB0a14';
const NFT_ABI = parseAbi([
  'function totalSupply() view returns (uint256)',
  'function tokenURI(uint256) view returns (string)',
]);

interface NftMeta {
  id: number;
  name?: string;
  image?: string;
  desc?: string;
}

const NftCarouselDashboard: React.FC = () => {
  const publicClient = usePublicClient();
  const [nfts, setNfts] = useState<NftMeta[]>([]);
  const [startIdx, setStartIdx] = useState(0);
  const visibleCount = 3;
  const canPrev = startIdx > 0;
  const canNext = startIdx + visibleCount < nfts.length;

  useEffect(() => {
    const fetchNfts = async () => {
      if (!publicClient) return;
      try {
        // totalSupply 조회
        const totalSupply = await publicClient.readContract({
          address: NFT_CONTRACT,
          abi: NFT_ABI,
          functionName: 'totalSupply',
        }) as bigint;
        const max = Math.min(Number(totalSupply), 6);
        const nftList: NftMeta[] = [];
        for (let i = 0; i < max; i++) {
          let tokenId = i + 1; // ERC721은 1번부터 시작하는 경우 많음
          let tokenUri = '';
          try {
            tokenUri = await publicClient.readContract({
              address: NFT_CONTRACT,
              abi: NFT_ABI,
              functionName: 'tokenURI',
              args: [BigInt(tokenId)],
            }) as string;
          } catch (e) {
            continue;
          }
          // 메타데이터 fetch
          let meta: NftMeta = { id: tokenId };
          try {
            // IPFS 변환
            if (tokenUri.startsWith('ipfs://')) {
              tokenUri = tokenUri.replace('ipfs://', 'https://ipfs.io/ipfs/');
            }
            const res = await fetch(tokenUri);
            const data = await res.json();
            meta = {
              id: tokenId,
              name: data.name,
              image: data.image?.startsWith('ipfs://') ? data.image.replace('ipfs://', 'https://ipfs.io/ipfs/') : data.image,
              desc: data.description,
            };
          } catch (e) {
            // 메타데이터 fetch 실패 시 토큰ID만
            meta = { id: tokenId };
          }
          nftList.push(meta);
        }
        setNfts(nftList);
      } catch (e) {
        setNfts([]);
      }
    };
    fetchNfts();
  }, [publicClient]);

  const handlePrev = () => { if (canPrev) setStartIdx(startIdx - 1); };
  const handleNext = () => { if (canNext) setStartIdx(startIdx + 1); };

  return (
    <div className="nft-carousel-dashboard">
      <h2>테스트넷 NFT</h2>
      <div className="nft-slider-row">
        <button className="nft-arrow-btn" onClick={handlePrev} disabled={!canPrev}>&lt;</button>
        <div className="nft-slider-cards">
          {nfts.length === 0 ? (
            <div style={{ color: '#aaa', padding: 24 }}>NFT를 불러오는 중이거나 없음</div>
          ) : (
            nfts.slice(startIdx, startIdx + visibleCount).map(nft => (
              <div className="nft-card" key={nft.id}>
                {nft.image ? (
                  <img src={nft.image} alt={nft.name || `NFT #${nft.id}`} />
                ) : (
                  <div style={{ width: 90, height: 90, background: '#222', borderRadius: 10, marginBottom: 10 }} />
                )}
                <div className="nft-info">
                  <div className="nft-name">{nft.name || `NFT #${nft.id}`}</div>
                  <div className="nft-desc">{nft.desc || `Token ID: ${nft.id}`}</div>
                </div>
              </div>
            ))
          )}
        </div>
        <button className="nft-arrow-btn" onClick={handleNext} disabled={!canNext}>&gt;</button>
      </div>
    </div>
  );
};

export default NftCarouselDashboard; 