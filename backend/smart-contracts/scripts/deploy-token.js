const hre = require("hardhat");

async function main() {
  console.log("Deploying CryptoGravesToken contract...");

  const CryptoGravesToken = await hre.ethers.getContractFactory("CryptoGravesToken");
  const tokenContract = await CryptoGravesToken.deploy();

  await tokenContract.waitForDeployment();

  const address = await tokenContract.getAddress();
  console.log("CryptoGravesToken deployed to:", address);

  // 배포된 주소를 파일에 저장
  const fs = require("fs");
  const deploymentInfo = {
    network: "monad_testnet",
    contract: "CryptoGravesToken",
    address: address,
    deployedAt: new Date().toISOString()
  };

  fs.writeFileSync(
    "deployment-token.json",
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("Deployment info saved to deployment-token.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 