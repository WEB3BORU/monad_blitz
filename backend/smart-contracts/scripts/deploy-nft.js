const hre = require("hardhat");

async function main() {
  console.log("Deploying CryptoGravesNFT contract...");

  const CryptoGravesNFT = await hre.ethers.getContractFactory("CryptoGravesNFT");
  const nftContract = await CryptoGravesNFT.deploy();

  await nftContract.waitForDeployment();

  const address = await nftContract.getAddress();
  console.log("CryptoGravesNFT deployed to:", address);

  // 배포된 주소를 파일에 저장
  const fs = require("fs");
  const deploymentInfo = {
    network: "monad_testnet",
    contract: "CryptoGravesNFT",
    address: address,
    deployedAt: new Date().toISOString()
  };

  fs.writeFileSync(
    "deployment-nft.json",
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("Deployment info saved to deployment-nft.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 