# Base mainnet deployments

Chain
- Base mainnet chainId: 8453

Swap deployments
- ERC20 sender Swap: `0x8a9969ed0A9bb3cDA7521DDaA614aE86e72e0A57`
  - requiredSenderKind: `0x36372b07` (ERC20)
- ERC721 sender Swap: `0x2aa29F096257bc6B253bfA9F6404B20Ae0ef9C4d`
  - requiredSenderKind: `0x80ac58cd` (ERC721)
- ERC1155 sender Swap: `0xD19783B48b11AFE1544b001c6d807A513e5A95cf`
  - requiredSenderKind: `0xd9b67a26` (ERC1155)

Shared fee config
- protocolFee: 50 bps
- protocolFeeWallet: `0xdb3Ec7B16Fd60fB4fDB58A438Bd8AF57d8d3a91c`

Adapters
- ERC20Adapter: `0x466BF4Aa2F9F07e7CF7dF02ab5DF657ab16F7954` kind `0x36372b07`
- ERC721Adapter: `0x51F3867d5D2Aea62E0F0B5D6EA3be0cECe32321e` kind `0x80ac58cd`
- ERC1155Adapter: `0x634E17f67fA3d81245aFAbD9724fFaEF9ccA3bd4` kind `0xd9b67a26`

Common Base tokens
- WETH: `0x4200000000000000000000000000000000000006`
- USDC: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
