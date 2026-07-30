/**
 * Universal Profile Constants
 * Contract addresses, data keys, and permission definitions
 */

/**
 * LSP6 Key Manager Permissions
 * Each permission is a single bit in a bytes32 value
 */
export const PERMISSIONS = {
  CHANGEOWNER: '0x0000000000000000000000000000000000000000000000000000000000000001',
  ADDCONTROLLER: '0x0000000000000000000000000000000000000000000000000000000000000002',
  EDITPERMISSIONS: '0x0000000000000000000000000000000000000000000000000000000000000004',
  ADDEXTENSIONS: '0x0000000000000000000000000000000000000000000000000000000000000008',
  CHANGEEXTENSIONS: '0x0000000000000000000000000000000000000000000000000000000000000010',
  ADDUNIVERSALRECEIVERDELEGATE: '0x0000000000000000000000000000000000000000000000000000000000000020',
  CHANGEUNIVERSALRECEIVERDELEGATE: '0x0000000000000000000000000000000000000000000000000000000000000040',
  REENTRANCY: '0x0000000000000000000000000000000000000000000000000000000000000080',
  SUPER_TRANSFERVALUE: '0x0000000000000000000000000000000000000000000000000000000000000100',
  TRANSFERVALUE: '0x0000000000000000000000000000000000000000000000000000000000000200',
  SUPER_CALL: '0x0000000000000000000000000000000000000000000000000000000000000400',
  CALL: '0x0000000000000000000000000000000000000000000000000000000000000800',
  SUPER_STATICCALL: '0x0000000000000000000000000000000000000000000000000000000000001000',
  STATICCALL: '0x0000000000000000000000000000000000000000000000000000000000002000',
  SUPER_DELEGATECALL: '0x0000000000000000000000000000000000000000000000000000000000004000',
  DELEGATECALL: '0x0000000000000000000000000000000000000000000000000000000000008000',
  DEPLOY: '0x0000000000000000000000000000000000000000000000000000000000010000',
  SUPER_SETDATA: '0x0000000000000000000000000000000000000000000000000000000000020000',
  SETDATA: '0x0000000000000000000000000000000000000000000000000000000000040000',
  ENCRYPT: '0x0000000000000000000000000000000000000000000000000000000000080000',
  DECRYPT: '0x0000000000000000000000000000000000000000000000000000000000100000',
  SIGN: '0x0000000000000000000000000000000000000000000000000000000000200000',
  EXECUTE_RELAY_CALL: '0x0000000000000000000000000000000000000000000000000000000000400000',
  
  // Combined permission for all
  ALL_PERMISSIONS: '0x00000000000000000000000000000000000000000000000000000000007fffff',
};

/**
 * Permission bit positions (for decoding)
 */
export const PERMISSION_NAMES = {
  0: 'CHANGEOWNER',
  1: 'ADDCONTROLLER',
  2: 'EDITPERMISSIONS',
  3: 'ADDEXTENSIONS',
  4: 'CHANGEEXTENSIONS',
  5: 'ADDUNIVERSALRECEIVERDELEGATE',
  6: 'CHANGEUNIVERSALRECEIVERDELEGATE',
  7: 'REENTRANCY',
  8: 'SUPER_TRANSFERVALUE',
  9: 'TRANSFERVALUE',
  10: 'SUPER_CALL',
  11: 'CALL',
  12: 'SUPER_STATICCALL',
  13: 'STATICCALL',
  14: 'SUPER_DELEGATECALL',
  15: 'DELEGATECALL',
  16: 'DEPLOY',
  17: 'SUPER_SETDATA',
  18: 'SETDATA',
  19: 'ENCRYPT',
  20: 'DECRYPT',
  21: 'SIGN',
  22: 'EXECUTE_RELAY_CALL',
};

/**
 * Permission presets for common use cases
 */
export const PERMISSION_PRESETS = {
  'read-only': {
    name: 'Read Only',
    description: 'Can only read data, cannot make changes',
    permissions: ['STATICCALL'],
    riskLevel: 'LOW',
  },
  'token-operator': {
    name: 'Token Operator',
    description: 'Can transfer tokens and NFTs',
    permissions: ['CALL', 'TRANSFERVALUE'],
    riskLevel: 'MEDIUM',
  },
  'nft-trader': {
    name: 'NFT Trader',
    description: 'Marketplace operations - list, buy, sell NFTs',
    permissions: ['CALL', 'TRANSFERVALUE', 'STATICCALL'],
    riskLevel: 'MEDIUM',
  },
  'defi-trader': {
    name: 'DeFi Trader',
    description: 'DEX swaps, liquidity provision, marketplace operations',
    permissions: ['CALL', 'TRANSFERVALUE', 'STATICCALL'],
    riskLevel: 'HIGH',
  },
  'profile-manager': {
    name: 'Profile Manager',
    description: 'Can update profile metadata and data',
    permissions: ['SETDATA', 'CALL'],
    riskLevel: 'MEDIUM',
  },
  'full-access': {
    name: 'Full Access',
    description: 'Complete control over the Universal Profile (dangerous!)',
    permissions: ['ALL_PERMISSIONS'],
    riskLevel: 'CRITICAL',
    warning: 'This grants full control over your Universal Profile',
  },
};

/**
 * ERC725Y Data Keys
 */
export const DATA_KEYS = {
  // LSP3 Profile
  LSP3Profile: '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5',
  
  // LSP5 Received Assets
  'LSP5ReceivedAssets[]': '0x6460ee3c0aac563ccbf76d6e1d07bada78e3a9514e6382b736ed3f478ab7b90b',
  'LSP5ReceivedAssetsMap': '0x812c4334633eb816c80d0000', // + asset address
  
  // LSP6 Key Manager Permissions
  'AddressPermissions[]': '0xdf30dba06db6a30e65354d9a64c609861f089545ca58c6b4dbe31a5f338cb0e3',
  'AddressPermissions:Permissions': '0x4b80742de2bf82acb3630000', // + controller address
  'AddressPermissions:AllowedCalls': '0x4b80742de2bf393a64c70000', // + controller address
  'AddressPermissions:AllowedERC725YDataKeys': '0x4b80742de2bf866c29110000', // + controller address
  
  // LSP10 Received Vaults
  'LSP10Vaults[]': '0x55482936e01da86729a45d2b87a6b1d3bc582bea0ec00e38bdb340e3af6f9f06',
  'LSP10VaultsMap': '0x192448c3c0f88c7f238c0000', // + vault address
  
  // LSP12 Issued Assets
  'LSP12IssuedAssets[]': '0x7c8c3416d6cda87cd42c71ea1843df28ac4850354f988d55ee2eaa47b6dc05cd',
  'LSP12IssuedAssetsMap': '0x74ac2555c10b9349e78f0000', // + asset address
};

/**
 * Chain configurations
 */
export const CHAINS = {
  lukso: {
    chainId: 42,
    name: 'LUKSO',
    rpcUrl: 'https://42.rpc.thirdweb.com',
    explorer: 'https://explorer.lukso.network',
    currency: { name: 'LYX', symbol: 'LYX', decimals: 18 },
  },
  'lukso-testnet': {
    chainId: 4201,
    name: 'LUKSO Testnet',
    rpcUrl: 'https://rpc.testnet.lukso.network',
    explorer: 'https://explorer.testnet.lukso.network',
    currency: { name: 'LYXt', symbol: 'LYXt', decimals: 18 },
  },
  base: {
    chainId: 8453,
    name: 'Base',
    rpcUrl: 'https://mainnet.base.org',
    explorer: 'https://basescan.org',
    currency: { name: 'Ether', symbol: 'ETH', decimals: 18 },
  },
  ethereum: {
    chainId: 1,
    name: 'Ethereum',
    rpcUrl: 'https://eth.llamarpc.com',
    explorer: 'https://etherscan.io',
    currency: { name: 'Ether', symbol: 'ETH', decimals: 18 },
  },
};

/**
 * Factory contract addresses (deterministic across chains)
 */
export const FACTORY_ADDRESSES = {
  LSP16_UNIVERSAL_FACTORY: '0x1600016e23e25D20CA8759338BfB8A8d11563C4e',
  LSP23_LINKED_CONTRACTS_FACTORY: '0x2300000A84D25dF63081feAa37ba6b62C4c89a30',
};

/**
 * Singleton contract addresses (same on mainnet & testnet)
 */
export const SINGLETON_ADDRESSES = {
  LSP26_FOLLOWER_SYSTEM: '0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA',
};

/**
 * Contract ABIs (minimal interfaces)
 */
export const ABIS = {
  // ERC725Y (Key-Value Store)
  ERC725Y: [
    'function getData(bytes32 dataKey) view returns (bytes)',
    'function getDataBatch(bytes32[] dataKeys) view returns (bytes[])',
    'function setData(bytes32 dataKey, bytes dataValue)',
    'function setDataBatch(bytes32[] dataKeys, bytes[] dataValues)',
  ],
  
  // LSP0 (Universal Profile / ERC725Account)
  LSP0: [
    'function execute(uint256 operationType, address target, uint256 value, bytes data) payable returns (bytes)',
    'function executeBatch(uint256[] operationTypes, address[] targets, uint256[] values, bytes[] datas) payable returns (bytes[])',
    'function getData(bytes32 dataKey) view returns (bytes)',
    'function getDataBatch(bytes32[] dataKeys) view returns (bytes[])',
    'function setData(bytes32 dataKey, bytes dataValue)',
    'function setDataBatch(bytes32[] dataKeys, bytes[] dataValues)',
    'function owner() view returns (address)',
    'function supportsInterface(bytes4 interfaceId) view returns (bool)',
  ],
  
  // LSP6 (Key Manager)
  LSP6: [
    'function execute(bytes calldata payload) payable returns (bytes)',
    'function executeBatch(uint256[] values, bytes[] payloads) payable returns (bytes[])',
    'function executeRelayCall(bytes signature, uint256 nonce, uint256 validityTimestamps, bytes payload) payable returns (bytes)',
    'function executeRelayCallBatch(bytes[] signatures, uint256[] nonces, uint256[] validityTimestamps, uint256[] values, bytes[] payloads) payable returns (bytes[])',
    'function getNonce(address from, uint128 channelId) view returns (uint256)',
    'function target() view returns (address)',
    'function isValidSignature(bytes32 dataHash, bytes signature) view returns (bytes4)',
  ],
  
  // LSP7 (Digital Asset - Fungible Token)
  LSP7: [
    'function name() view returns (string)',
    'function symbol() view returns (string)',
    'function decimals() view returns (uint8)',
    'function totalSupply() view returns (uint256)',
    'function balanceOf(address tokenOwner) view returns (uint256)',
    'function transfer(address from, address to, uint256 amount, bool force, bytes data)',
    'function authorizeOperator(address operator, uint256 amount, bytes operatorNotificationData)',
    'function revokeOperator(address operator, address tokenOwner, bool notify, bytes operatorNotificationData)',
    'function authorizedAmountFor(address operator, address tokenOwner) view returns (uint256)',
  ],
  
  // LSP8 (Identifiable Digital Asset - NFT)
  LSP8: [
    'function name() view returns (string)',
    'function symbol() view returns (string)',
    'function totalSupply() view returns (uint256)',
    'function balanceOf(address tokenOwner) view returns (uint256)',
    'function tokenOwnerOf(bytes32 tokenId) view returns (address)',
    'function tokenIdsOf(address tokenOwner) view returns (bytes32[])',
    'function transfer(address from, address to, bytes32 tokenId, bool force, bytes data)',
    'function authorizeOperator(address operator, bytes32 tokenId, bytes operatorNotificationData)',
    'function revokeOperator(address operator, bytes32 tokenId, bool notify, bytes operatorNotificationData)',
    'function isOperatorFor(address operator, bytes32 tokenId) view returns (bool)',
  ],

  // LSP26 (Follower System)
  LSP26: [
    'function follow(address addr)',
    'function unfollow(address addr)',
    'function isFollowing(address follower, address addr) view returns (bool)',
    'function followerCount(address addr) view returns (uint256)',
    'function followingCount(address addr) view returns (uint256)',
  ],
};

/**
 * Interface IDs for contract detection
 */
export const INTERFACE_IDS = {
  ERC165: '0x01ffc9a7',
  ERC725X: '0x7545acac',
  ERC725Y: '0x629aa694',
  LSP0: '0x24871b3d', // ERC725Account
  LSP6: '0x23f34c62', // Key Manager
  LSP7: '0xc52d6008', // Digital Asset
  LSP8: '0x3a271706', // Identifiable Digital Asset
  LSP9: '0x28af17e6', // Vault
  LSP26: '0x2b299cea', // Follower System
};

/**
 * Operation types for execute()
 */
export const OPERATION_TYPES = {
  CALL: 0,
  CREATE: 1,
  CREATE2: 2,
  STATICCALL: 3,
  DELEGATECALL: 4,
};

/**
 * Permission risk levels and warnings
 */
export const PERMISSION_RISKS = {
  CHANGEOWNER: {
    level: 'CRITICAL',
    warning: 'Can transfer profile ownership - use only for recovery',
  },
  SUPER_DELEGATECALL: {
    level: 'CRITICAL',
    warning: 'Can execute arbitrary code in UP context - extremely dangerous',
  },
  DELEGATECALL: {
    level: 'CRITICAL',
    warning: 'Can execute code in UP context with restrictions - dangerous',
  },
  EDITPERMISSIONS: {
    level: 'HIGH',
    warning: 'Can modify permissions of other controllers',
  },
  ADDCONTROLLER: {
    level: 'HIGH',
    warning: 'Can add new controllers to the profile',
  },
  SUPER_SETDATA: {
    level: 'HIGH',
    warning: 'Can modify any data on profile without restrictions',
  },
  SUPER_CALL: {
    level: 'HIGH',
    warning: 'Can call any contract without restrictions',
  },
  SUPER_TRANSFERVALUE: {
    level: 'HIGH',
    warning: 'Can transfer native tokens without restrictions',
  },
  SETDATA: {
    level: 'MEDIUM',
    warning: 'Can modify profile data (restricted by AllowedERC725YDataKeys)',
  },
  CALL: {
    level: 'MEDIUM',
    warning: 'Can call contracts (restricted by AllowedCalls)',
  },
  TRANSFERVALUE: {
    level: 'MEDIUM',
    warning: 'Can transfer native tokens',
  },
  DEPLOY: {
    level: 'MEDIUM',
    warning: 'Can deploy new contracts from the profile',
  },
  STATICCALL: {
    level: 'LOW',
    warning: 'Can read data from any contract - safe for queries',
  },
  SUPER_STATICCALL: {
    level: 'LOW',
    warning: 'Can read data from any contract without restrictions',
  },
  SIGN: {
    level: 'LOW',
    warning: 'Can sign messages on behalf of the profile',
  },
  ENCRYPT: {
    level: 'LOW',
    warning: 'Can encrypt data',
  },
  DECRYPT: {
    level: 'LOW',
    warning: 'Can decrypt data',
  },
  EXECUTE_RELAY_CALL: {
    level: 'LOW',
    warning: 'Can execute relay calls (meta-transactions)',
  },
  REENTRANCY: {
    level: 'MEDIUM',
    warning: 'Allows reentrant calls - may be needed for some protocols',
  },
  ADDEXTENSIONS: {
    level: 'MEDIUM',
    warning: 'Can add new extensions to the profile',
  },
  CHANGEEXTENSIONS: {
    level: 'MEDIUM',
    warning: 'Can modify existing extensions',
  },
  ADDUNIVERSALRECEIVERDELEGATE: {
    level: 'MEDIUM',
    warning: 'Can add universal receiver delegates',
  },
  CHANGEUNIVERSALRECEIVERDELEGATE: {
    level: 'MEDIUM',
    warning: 'Can modify universal receiver delegates',
  },
};

export default {
  PERMISSIONS,
  PERMISSION_NAMES,
  PERMISSION_PRESETS,
  DATA_KEYS,
  CHAINS,
  FACTORY_ADDRESSES,
  ABIS,
  INTERFACE_IDS,
  OPERATION_TYPES,
  PERMISSION_RISKS,
};

/**
 * Resolve explorer base URL from chain ID
 */
function getExplorerBase(chainId = 42) {
  const map = { 42: 'https://explorer.lukso.network', 4201: 'https://explorer.testnet.lukso.network', 8453: 'https://basescan.org', 1: 'https://etherscan.io' };
  return map[chainId] || map[42];
}

/**
 * Get explorer URL for a transaction
 */
export function getExplorerUrl(txHash, chainId = 42) {
  return `${getExplorerBase(chainId)}/tx/${txHash}`;
}

/**
 * Get explorer URL for an address
 */
export function getAddressExplorerUrl(address, chainId = 42) {
  return `${getExplorerBase(chainId)}/address/${address}`;
}
