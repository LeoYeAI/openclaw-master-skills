import ViewFacetABI from "../abi/ViewFacet.json" with { type: "json" }
import PurchaseFacetABI from "../abi/PurchaseFacet.json" with { type: "json" }
import ExitFacetABI from "../abi/ExitFacet.json" with { type: "json" }
import LifecycleFacetABI from "../abi/LifecycleFacet.json" with { type: "json" }
import SlotMachineFacetABI from "../abi/SlotMachineFacet.json" with { type: "json" }
import SlotDepositFacetABI from "../abi/SlotDepositFacet.json" with { type: "json" }
import SlotViewFacetABI from "../abi/SlotViewFacet.json" with { type: "json" }
import PredViewFacetABI from "../abi/PredViewFacet.json" with { type: "json" }
import PredPredictionFacetABI from "../abi/PredPredictionFacet.json" with { type: "json" }
import PredSettleFacetABI from "../abi/PredSettleFacet.json" with { type: "json" }
import PredOracleSettleFacetABI from "../abi/PredOracleSettleFacet.json" with { type: "json" }
import PredOptimisticSettleFacetABI from "../abi/PredOptimisticSettleFacet.json" with { type: "json" }
import PredAdminFacetABI from "../abi/PredAdminFacet.json" with { type: "json" }

// Fomo3D 主游戏 Diamond ABI（合并所有 Facet）
export const FOMO3D_ABI = [
  ...ViewFacetABI,
  ...PurchaseFacetABI,
  ...ExitFacetABI,
  ...LifecycleFacetABI,
] as const

// 老虎机 Diamond ABI
export const SLOT_ABI = [
  ...SlotMachineFacetABI,
  ...SlotDepositFacetABI,
  ...SlotViewFacetABI,
] as const

// 预测市场 Diamond ABI
export const PREDICTION_ABI = [
  ...PredViewFacetABI,
  ...PredPredictionFacetABI,
  ...PredSettleFacetABI,
  ...PredOracleSettleFacetABI,
  ...PredOptimisticSettleFacetABI,
  ...PredAdminFacetABI,
] as const

// ERC20 最小 ABI
export const ERC20_ABI = [
  { type: "function", name: "approve", inputs: [{ name: "spender", type: "address" }, { name: "amount", type: "uint256" }], outputs: [{ type: "bool" }], stateMutability: "nonpayable" },
  { type: "function", name: "allowance", inputs: [{ name: "owner", type: "address" }, { name: "spender", type: "address" }], outputs: [{ type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "balanceOf", inputs: [{ name: "account", type: "address" }], outputs: [{ type: "uint256" }], stateMutability: "view" },
  { type: "function", name: "decimals", inputs: [], outputs: [{ type: "uint8" }], stateMutability: "view" },
  { type: "function", name: "symbol", inputs: [], outputs: [{ type: "string" }], stateMutability: "view" },
] as const

// VRF 费用回退值
export const VRF_FEE_FALLBACK = BigInt("150000000000000") // 0.00015 BNB
