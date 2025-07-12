const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Starting deployment to Monad Testnet...");

  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying contracts with account:", deployer.address);
  console.log("💰 Account balance:", (await deployer.getBalance()).toString());

  // Deploy CryptoGravesNFT first
  console.log("\n🎨 Deploying CryptoGravesNFT...");
  const CryptoGravesNFT = await ethers.getContractFactory("CryptoGravesNFT");
  const nftContract = await CryptoGravesNFT.deploy();
  await nftContract.deployed();
  console.log("✅ CryptoGravesNFT deployed to:", nftContract.address);

  // Deploy CryptoGravesToken
  console.log("\n🪙 Deploying CryptoGravesToken...");
  const CryptoGravesToken = await ethers.getContractFactory("CryptoGravesToken");
  const tokenContract = await CryptoGravesToken.deploy();
  await tokenContract.deployed();
  console.log("✅ CryptoGravesToken deployed to:", tokenContract.address);

  // Set up cross-contract references
  console.log("\n🔗 Setting up contract references...");
  
  // Set NFT contract address in Token contract
  await tokenContract.setNFTContract(nftContract.address);
  console.log("✅ NFT contract address set in Token contract");

  // Set Token contract address in NFT contract
  await nftContract.setTokenContract(tokenContract.address);
  console.log("✅ Token contract address set in NFT contract");

  console.log("\n🎉 Deployment completed successfully!");
  console.log("📋 Contract Addresses:");
  console.log("   NFT Contract:", nftContract.address);
  console.log("   Token Contract:", tokenContract.address);
  console.log("\n🔍 Verify contracts on Monad Explorer:");
  console.log("   NFT: https://explorer.testnet.monad.tech/address/" + nftContract.address);
  console.log("   Token: https://explorer.testnet.monad.tech/address/" + tokenContract.address);
  
  // Save deployment info to file
  const deploymentInfo = {
    network: "monad_testnet",
    deployer: deployer.address,
    contracts: {
      nft: nftContract.address,
      token: tokenContract.address
    },
    timestamp: new Date().toISOString()
  };
  
  console.log("\n💾 Deployment info saved to deployment-info.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  }); 