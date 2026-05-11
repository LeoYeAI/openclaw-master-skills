# EIP-712 Signed Macro Example (SuperBoring)

> Prerequisite: read `macro-forwarders.md` for the core MacroForwarder pattern,
> `IUserDefinedMacro` interface, and batch operation types.

The SuperBoring project extends the basic macro pattern with **EIP-712 typed
data signing**. This allows a dapp to present a human-readable message to the
user for wallet signing, then verify the signature on-chain before executing
the macro. The pattern adds:

- **Off-chain signature verification** — the dapp constructs a typed message,
  the user signs it, and the macro verifies the signature against `msgSender`
- **Language-aware messages** — the signed message can be localized
  (e.g., "Set your DCA position to 100 USDCx/month")
- **Action routing** — a single macro contract handles multiple action types
  via action codes
- **Post-check validation** — verifies expected state after execution

The architecture layers as follows:

```
IUserDefinedMacro (protocol interface)
  └── EIP712MacroBase (abstract — adds signature verification, action routing)
        └── SB712Macro (concrete — SuperBoring DCA position management)
```

`EIP712MacroBase` overrides `buildBatchOperations` and `postCheck` to:
1. Decode `params` as `(actionCode, lang, actionParams, signatureVRS)`
2. Look up the action by code, compute the EIP-712 digest, verify the signature
3. Delegate to the action's `buildOperations` function
4. After execution, delegate to the action's `postCheckHandler`

## EIP712MacroBase Source

```solidity
// SPDX-License-Identifier: AGPLv3
pragma solidity ^0.8.26;

import { EIP712 } from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

import { ISuperfluid } from "@superfluid-finance/ethereum-contracts/contracts/interfaces/superfluid/ISuperfluid.sol";
import { IUserDefinedMacro } from "@superfluid-finance/ethereum-contracts/contracts/utils/MacroForwarder.sol";

/**
 * @title Abstract contract that extends EIP712 and implements IUserDefinedMacro.
 *
 * This contract provides a base for handling actions with associated operations and validation
 *  using EIP712 signatures.
 * The contract maintains a mapping of action codes to `Action` structs and provides functions to
 *  build batch operations and handle post-checks per action.
 *
 * @dev The `batchParams` format is as follows:
 * - `actionCode` (uint8): The unique code identifying the action.
 * - `lang` (bytes32): The language code for the message.
 * - `actionParams` (bytes): Arbitrary data for building operations and validation.
 * - `signatureVRS` (bytes): The signature in VRS format.
 */
abstract contract EIP712MacroBase is EIP712, IUserDefinedMacro {

    error UnknownActionCode(uint8 actionCode);
    error InvalidSignature();
    error UnsupportedLanguage();

    struct Action {
        uint8 actionCode;
        bool exists;
        function(ISuperfluid, bytes memory, address)
            internal view returns (ISuperfluid.Operation[] memory) buildOperations;
        function(bytes memory, bytes32)
            internal view returns (bytes32) getDigest;
        bool skipPostCheck;
        function(ISuperfluid, bytes memory, address)
            internal view postCheckHandler;
    }

    mapping(uint8 => Action) internal _actionHandlers;

    constructor(string memory name, string memory version) EIP712(name, version) {
        Action[] memory actions = _getActions();
        for (uint256 i = 0; i < actions.length; i++) {
            _actionHandlers[actions[i].actionCode] = actions[i];
        }
    }

    function _getActions() internal view virtual returns (Action[] memory);

    function buildBatchOperations(ISuperfluid host, bytes memory params, address msgSender)
        external view override
        returns (ISuperfluid.Operation[] memory operations)
    {
        (uint8 actionCode, bytes32 lang, bytes memory actionParams, bytes memory signatureVRS) =
            _decodeBatchParams(params);

        if (_actionHandlers[actionCode].exists == false) {
            revert UnknownActionCode(actionCode);
        }

        bytes32 digest = _actionHandlers[actionCode].getDigest(actionParams, lang);
        if (!_validateSignature(digest, signatureVRS, msgSender)) {
            revert InvalidSignature();
        }

        return _actionHandlers[actionCode].buildOperations(host, actionParams, msgSender);
    }

    function postCheck(ISuperfluid host, bytes memory params, address msgSender)
        external view override
    {
        (uint8 actionCode,, bytes memory actionParams,) = _decodeBatchParams(params);

        if (_actionHandlers[actionCode].skipPostCheck) return;
        if (_actionHandlers[actionCode].exists == false) {
            revert UnknownActionCode(actionCode);
        }

        _actionHandlers[actionCode].postCheckHandler(host, actionParams, msgSender);
    }

    function _validateSignature(bytes32 digest, bytes memory signatureVRS, address msgSender)
        private pure returns (bool)
    {
        (uint8 v, bytes32 r, bytes32 s) = abi.decode(signatureVRS, (uint8, bytes32, bytes32));
        return ecrecover(digest, v, r, s) == msgSender;
    }

    function _decodeBatchParams(bytes memory batchParams)
        private pure
        returns (uint8 actionCode, bytes32 lang, bytes memory actionParams, bytes memory signatureVRS)
    {
        (actionCode, lang, actionParams, signatureVRS) = abi.decode(batchParams, (uint8, bytes32, bytes, bytes));
    }
}
```

## SB712Macro Source

This contract manages DCA (Dollar-Cost Averaging) positions. A single
`SetDCAPosition` action atomically: upgrades underlying tokens, approves a
Torex contract, creates/updates a CFA stream, and connects to a GDA pool.

```solidity
// SPDX-License-Identifier: AGPLv3
pragma solidity ^0.8.26;

import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";

import {
    ISuperfluid,
    BatchOperation,
    IConstantFlowAgreementV1,
    IGeneralDistributionAgreementV1,
    ISuperToken,
    ISuperfluidPool,
    IERC20
} from "@superfluid-finance/ethereum-contracts/contracts/interfaces/superfluid/ISuperfluid.sol";
import {SuperTokenV1Library} from "@superfluid-finance/ethereum-contracts/contracts/apps/SuperTokenV1Library.sol";
import {ITorex} from "../interfaces/torex/ITorex.sol";
import {FlowRateFormatter} from "./FlowRateFormatter.sol";
import {EIP712MacroBase} from "./EIP712MacroBase.sol";

/**
 * User defined macro for SuperBoring with EIP712 signature validation.
 * How to use this contract:
 * - Deploy to a network with Superfluid and the MacroForwarder available
 * - Call `encode712SetDCAPosition()` to get the userfacing message param of the EIP712 signature,
 *      the actionCode and the encoded parameters.
 * - Sign the message object with the user's wallet.
 * - Construct the `macroparams` as follows:
 *     - `actionCode` (uint8): The action code for the SetDCAPosition action.
 *     - `lang` (bytes32): The language code for the message.
 *     - `actionParams` (bytes): The encoded SetDCAPositionParams object.
 *     - `signatureVRS` (bytes): The signature in VRS format.
 * - Make a call to `MacroForwarder.runMacro(this.address, macroparams)`,
 *     providing the address of this contract and the encoded parameters.
 */
contract SB712Macro is EIP712MacroBase {
    using SuperTokenV1Library for ISuperToken;
    using FlowRateFormatter for int96;

    error NoOutTokenPoolUnits();

    struct SetDCAPositionParams {
        ITorex torex;
        int96 flowRate;
        address distributor;
        address referrer;
        uint256 upgradeAmount;
    }

    uint8 public constant ACTION_SET_DCA_POSITION_CODE = 1;
    string public constant ACTION_SET_DCA_POSITION_NAME = "SetDCAPosition";
    bytes32 public constant TYPEHASH_SET_DCA_POSITION = keccak256(
        abi.encodePacked(
            ACTION_SET_DCA_POSITION_NAME,
            "(string message,address torex,int96 flowRate,address distributor,address referrer,uint256 upgradeAmount)"
        )
    );

    constructor() EIP712MacroBase("SuperBoring", "0.0.0") {}

    function _getActions() internal pure override returns (Action[] memory) {
        Action[] memory actions = new Action[](1);
        actions[0] = Action({
            actionCode: ACTION_SET_DCA_POSITION_CODE,
            exists: true,
            buildOperations: _createSetDCAPositionOperations,
            getDigest: _getDigestForSetDCAPosition,
            skipPostCheck: false,
            postCheckHandler: _postCheckSetDCAPosition
        });

        return actions;
    }

    /**
     * @dev Convenience function to get abi encoded parameters to be used
     *     with `MacroForwarder.runMacro(m, macroparams)`.
     * @param lang language code for the message to be constructed.
     * @param params SetDCAPositionParams object containing the following fields:
     *     - torex: address of the Torex contract. The token address is derived from this (inToken).
     *     - flowRate: flowrate to be set for the flow to the Torex contract.
     *         The pre-existing flowrate must be 0 (no flow).
     *     - distributor: address of the distributor, or zero address if none.
     *     - referrer: address of the referrer, or zero address if none.
     *     - upgradeAmount: amount (18 decimals) to upgrade from underlying ERC20 to SuperToken.
     *         - if `type(uint256).max`, the maximum possible amount is upgraded (current allowance).
     *         - otherwise, the specified amount is upgraded. Requires sufficient underlying balance and allowance,
     *           otherwise the transaction will revert.
     * Note that upgradeAmount shall be 0 if inToken has no underlying ERC20 token.
     *
     * @return actionCode The action code for the SetDCAPosition action.
     * @return message The userfacing message in the EIP712 signature.
     * @return actionParams The abi encoded SetDCAPositionParams object which should be included in the macroparams.
     *    @notice See {EIP712MacroBase} for more details.
     * @return digest The digest of the EIP712 payload.
     */
    function encode712SetDCAPosition(bytes32 lang, SetDCAPositionParams memory params)
        public
        view
        returns (uint8 actionCode, string memory message, bytes memory actionParams, bytes32 digest)
    {
        actionCode = ACTION_SET_DCA_POSITION_CODE;
        actionParams = abi.encode(params);

        (message, digest) = _buildMessageAndDigest(lang, params);
    }

    function _getDigestForSetDCAPosition(bytes memory actionParams, bytes32 lang)
        internal
        view
        returns (bytes32 digest)
    {
        SetDCAPositionParams memory params = _decode712SetDCAPosition(actionParams);

        (, digest) = _buildMessageAndDigest(lang, params);
    }

    function _buildMessageAndDigest(bytes32 lang, SetDCAPositionParams memory params)
        private
        view
        returns (string memory message, bytes32 digest)
    {
        (ISuperToken inToken,) = params.torex.getPairedTokens();

        // the message is constructed based on the selected language and action arguments
        if (lang == "en") {
            message = string(
                abi.encodePacked(
                    "Set your DCA position to ", params.flowRate.toFlowRateString(), " ", inToken.symbol(), "/month"
                )
            );
        } else if (lang == "hu") {
            message = string(
                abi.encodePacked(
                    unicode"Allitsd be a DCA poziciodat ",
                    params.flowRate.toFlowRateString(),
                    " ",
                    inToken.symbol(),
                    unicode"/honap"
                )
            );
        } else {
            revert UnsupportedLanguage();
        }

        digest = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    TYPEHASH_SET_DCA_POSITION,
                    keccak256(bytes(message)),
                    params.torex,
                    params.flowRate,
                    params.distributor,
                    params.referrer,
                    params.upgradeAmount
                )
            )
        );
    }

    function _decode712SetDCAPosition(bytes memory actionParams)
        private
        pure
        returns (SetDCAPositionParams memory dcaParams)
    {
        (dcaParams) = abi.decode(actionParams, (SetDCAPositionParams));
    }

    function _createSetDCAPositionOperations(ISuperfluid host, bytes memory actionParams, address msgSender)
        internal
        view
        returns (ISuperfluid.Operation[] memory operations)
    {
        SetDCAPositionParams memory params = _decode712SetDCAPosition(actionParams);

        // get token address from Torex
        (ISuperToken inToken,) = params.torex.getPairedTokens();

        // build batch operations
        operations = new ISuperfluid.Operation[](params.upgradeAmount > 0 ? 4 : 3);
        uint8 opsCnt = 0;

        // op: upgrade
        if (params.upgradeAmount == type(uint256).max) {
            IERC20 underlyingToken = IERC20(inToken.getUnderlyingToken());
            uint256 underlyingUpgradeAmount =
                Math.min(underlyingToken.balanceOf(msgSender), underlyingToken.allowance(msgSender, address(inToken)));
            (params.upgradeAmount,) = _fromUnderlyingAmount(inToken, underlyingUpgradeAmount);
        }

        if (params.upgradeAmount > 0) {
            operations[opsCnt++] = ISuperfluid.Operation({
                operationType: BatchOperation.OPERATION_TYPE_SUPERTOKEN_UPGRADE,
                target: address(inToken),
                data: abi.encode(params.upgradeAmount)
            });
        }

        // op: approve Torex to use SuperToken
        operations[opsCnt++] = ISuperfluid.Operation({
            operationType: BatchOperation.OPERATION_TYPE_ERC20_APPROVE,
            target: address(inToken),
            data: abi.encode(address(params.torex), params.torex.estimateApprovalRequired(params.flowRate))
        });

        // op: create or update flow
        {
            int96 prevFlowRate = inToken.getFlowRate(msgSender, address(params.torex));
            IConstantFlowAgreementV1 cfa = IConstantFlowAgreementV1(
                address(host.getAgreementClass(keccak256("org.superfluid-finance.agreements.ConstantFlowAgreement.v1")))
            );
            operations[opsCnt++] = ISuperfluid.Operation({
                operationType: BatchOperation.OPERATION_TYPE_SUPERFLUID_CALL_AGREEMENT,
                target: address(cfa),
                data: abi.encode(
                    abi.encodeCall(
                        prevFlowRate == 0 ? cfa.createFlow : cfa.updateFlow,
                        (
                            inToken,
                            address(params.torex), // receiver
                            params.flowRate,
                            new bytes(0) // ctx
                        )
                    ), // calldata
                    abi.encode(params.distributor, params.referrer) // userdata
                )
            });
        }

        // op: connect outTokenDistributionPool
        {
            IGeneralDistributionAgreementV1 gda = IGeneralDistributionAgreementV1(
                address(
                    host.getAgreementClass(
                        keccak256("org.superfluid-finance.agreements.GeneralDistributionAgreement.v1")
                    )
                )
            );
            ISuperfluidPool outTokenDistributionPool = params.torex.outTokenDistributionPool();
            operations[opsCnt++] = ISuperfluid.Operation({
                operationType: BatchOperation.OPERATION_TYPE_SUPERFLUID_CALL_AGREEMENT,
                target: address(gda),
                data: abi.encode(
                    abi.encodeCall(
                        gda.connectPool,
                        (
                            outTokenDistributionPool,
                            new bytes(0) // ctx
                        )
                    ), // calldata
                    new bytes(0) // userdata
                )
            });
        }

        return operations;
    }

    function _postCheckSetDCAPosition(ISuperfluid, /*host*/ bytes memory actionParams, address msgSender)
        internal
        view
    {
        SetDCAPositionParams memory dcaParams = _decode712SetDCAPosition(actionParams);

        ITorex torex = dcaParams.torex;

        ISuperfluidPool outTokenDistributionPool = torex.outTokenDistributionPool();

        if (outTokenDistributionPool.getUnits(msgSender) == 0) {
            revert NoOutTokenPoolUnits();
        }
    }

    // this should be in SuperToken.sol
    uint8 private constant _STANDARD_DECIMALS = 18;

    function _fromUnderlyingAmount(ISuperToken superToken, uint256 amount)
        private
        view
        returns (uint256 superTokenAmount, uint256 adjustedAmount)
    {
        uint256 factor;
        uint8 _underlyingDecimals = superToken.getUnderlyingDecimals();
        if (_underlyingDecimals < _STANDARD_DECIMALS) {
            factor = 10 ** (_STANDARD_DECIMALS - _underlyingDecimals);
            superTokenAmount = amount * factor;
            adjustedAmount = amount;
        } else if (_underlyingDecimals > _STANDARD_DECIMALS) {
            factor = 10 ** (_underlyingDecimals - _STANDARD_DECIMALS);
            superTokenAmount = amount / factor;
            adjustedAmount = superTokenAmount * factor;
        } else {
            superTokenAmount = adjustedAmount = amount;
        }
    }
}
```

Key patterns to note in this example:
- **Dynamic operation count**: array size depends on `upgradeAmount > 0`
- **On-chain state reads in buildBatchOperations**: checks `prevFlowRate` to
  decide between `createFlow` and `updateFlow`
- **userData for callbacks**: `abi.encode(distributor, referrer)` passed as
  userData, forwarded to Super App callbacks on the Torex contract
- **postCheck**: verifies the caller received GDA pool units (critical for
  the DCA use case — without units, the caller wouldn't receive output tokens)
