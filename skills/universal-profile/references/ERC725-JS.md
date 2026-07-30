# ERC725.js — Complete Reference

**Package:** `@erc725/erc725.js`
**Purpose:** Read, encode, and decode data from ERC725Y smart contracts using LSP2 JSON Schemas
**NPM:** https://npmjs.com/package/@erc725/erc725.js
**GitHub:** https://github.com/ERC725Alliance/erc725.js
**Inspect Tool:** https://erc725-inspect.lukso.tech/?network=lukso+mainnet
**Updated:** 2026-03-18

## Installation

```bash
npm install @erc725/erc725.js
# Backend also needs:
npm install isomorphic-fetch
```

## Three Ways to Use

### 1. Schema-only (encoding/decoding)
```js
import ERC725 from '@erc725/erc725.js';
const erc725 = new ERC725(schemas);
```

### 2. Connected to contract (fetch + decode)
```js
import ERC725 from '@erc725/erc725.js';
const erc725 = new ERC725(schemas, contractAddress, RPC_URL, {
  ipfsGateway: 'https://api.universalprofile.cloud/ipfs/',
  gas: 20_000_000,
});
```

### 3. Static/individual functions
```js
import { encodeValueType, decodeDataSourceWithHash } from '@erc725/erc725.js';
```

## LUKSO RPC Endpoints
- **Mainnet:** `https://rpc.lukso.gateway.fm` or `https://42.rpc.thirdweb.com`
- **Testnet:** `https://rpc.testnet.lukso.network`

---

## Standard LSP Schemas (built-in)

```js
import {
  LSP1Schema,   // UniversalReceiverDelegate
  LSP3Schema,   // Profile Metadata
  LSP4Schema,   // Digital Asset Metadata
  LSP5Schema,   // Received Assets
  LSP6Schema,   // Key Manager (Permissions)
  LSP8Schema,   // Identifiable Digital Asset (NFT)
  LSP9Schema,   // Vault
  LSP10Schema,  // Received Vaults
  LSP12Schema,  // Issued Assets
  LSP17Schema,  // Contract Extension
} from '@erc725/erc725.js/schemas';
```

### Schema Structure
```js
{
  name: 'LSP3Profile',
  key: '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5',
  keyType: 'Singleton',   // Singleton | Array | Mapping | MappingWithGrouping
  valueType: 'bytes',     // bytes | address | uint256 | bool | string | bytes32 | (tuple)
  valueContent: 'VerifiableURI', // Address | String | Number | Boolean | VerifiableURI | URL | BytesN | BitArray
}
```

---

## Core Methods

### Reading Data

#### `getData(keyName)` — Read raw data from contract
```js
await erc725.getData('LSP3Profile');
// { name: 'LSP3Profile', key: '0x5ef...', value: { verification: {...}, url: 'ipfs://...' } }

await erc725.getData(['LSP3Profile', 'LSP1UniversalReceiverDelegate']);
// Returns array of decoded values
```

#### `fetchData(keyName)` — Read + download + verify linked content
```js
await erc725.fetchData('LSP3Profile');
// Downloads the IPFS JSON, verifies hash, returns full profile object
```

#### `getOwner()` — Get contract owner
```js
await erc725.getOwner();
// '0x28D25E70819140daF65b724158D00c373D1a18ee'
```

### Encoding

#### `encodeData(data)` — Encode data for writing to contract
Returns `{ keys: string[], values: string[] }` ready for `setData()`/`setDataBatch()`.

```js
// Singleton
erc725.encodeData([{
  keyName: 'LSP1UniversalReceiverDelegate',
  value: '0x1183790f29BE3cDfD0A102862fEA1a4a30b3AdAb',
}]);

// VerifiableURI (pass JSON + URL, auto-hashes)
erc725.encodeData([{
  keyName: 'LSP3Profile',
  value: { json: profileJson, url: 'ipfs://Qm...' },
}]);

// Array
erc725.encodeData([{
  keyName: 'LSP12IssuedAssets[]',
  value: ['0xD943...', '0xDaea...'],
}]);

// Array length only
erc725.encodeData([{ keyName: 'LSP12IssuedAssets[]', value: 5 }]);

// Array subset (important for appending!)
erc725.encodeData([{
  keyName: 'AddressPermissions[]',
  value: ['0x983a...', '0x56ec...'],
  totalArrayLength: 23,  // total AFTER operation
  startingIndex: 21,     // where to start writing
}]);

// Dynamic keys (Mapping)
erc725.encodeData([{
  keyName: 'LSP12IssuedAssetsMap:<address>',
  dynamicKeyParts: ['0xbedbedbed...'],
  value: '0xcafecafe...',
}]);

// Tuples
erc725.encodeData([{
  keyName: 'LSP4CreatorsMap:<address>',
  dynamicKeyParts: '0xcafecafe...',
  value: ['0x24871b3d', '11'],  // (bytes4, uint128)
}]);

// CompactBytesArray tuples (AllowedCalls)
erc725.encodeData([{
  keyName: 'AddressPermissions:AllowedCalls:<address>',
  dynamicKeyParts: '0xcafecafe...',
  value: [
    ['0x00000003', '0xCA41e4ea...', '0x3e89ad98', '0xffffffff'],
    ['0x00000002', '0xF70Ce3b5...', '0xffffffff', '0x760d9bba'],
  ],
}]);
```

#### `encodeKeyName(keyName, dynamicParts?)` — Hash a key name
```js
ERC725.encodeKeyName('LSP3Profile');
// '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5'

ERC725.encodeKeyName('AddressPermissions:Permissions:cafecafe...');
// '0x4b80742de2bf82acb3630000cafecafe...'
```

#### `encodeArrayKey(key, index)` — Get array element key
```js
import { encodeArrayKey } from '@erc725/erc725.js';
encodeArrayKey('0x7c8c3416d6cda87cd42c71ea1843df28...', 2);
// '0x7c8c3416d6cda87cd42c71ea1843df2800000000000000000000000000000002'
```

#### `encodeValueType(type, value)` — Low-level type encoding
```js
ERC725.encodeValueType('uint256', 5);
ERC725.encodeValueType('bool', true);
ERC725.encodeValueType('bytes4', '0xcafe');  // right-pads: 0xcafe0000
ERC725.encodeValueType('uint256[CompactBytesArray]', [1, 2, 3]);
```

#### `encodeValueContent(valueContent, value)` — Content encoding
```js
import { encodeValueContent } from '@erc725/erc725.js';
encodeValueContent('String', 'hello');
encodeValueContent('Address', '0xa29a...');
encodeValueContent('VerifiableURI', { verification: {...}, url: '...' });
encodeValueContent('Boolean', true);
```

### Decoding

#### `decodeData(data)` — Decode raw contract data
```js
erc725.decodeData([{
  keyName: 'LSP3Profile',
  value: '0x6f357c6a820464ddfac1bec...',
}]);
// [{ name: 'LSP3Profile', key: '0x5ef...', value: { verification: {...}, url: 'ipfs://...' } }]

// Single object input returns single object output
erc725.decodeData({
  keyName: 'LSP3Profile',
  value: '0x6f357c6a...',
});
```

#### `decodeValueType(type, data)` — Low-level type decoding
```js
ERC725.decodeValueType('uint128', '0x0000000000000000000000000000000a'); // 10
ERC725.decodeValueType('bool', '0x01'); // true
ERC725.decodeValueType('string', '0x48656c6c6f21'); // 'Hello!'
```

#### `decodeValueContent(valueContent, value)` — Content decoding
```js
import { decodeValueContent } from '@erc725/erc725.js';
decodeValueContent('VerifiableURI', '0x00006f357c6a...');
// { verification: { method: 'keccak256(utf8)', data: '0x...' }, url: '...' }
decodeValueContent('Address', '0xa29afb8f...');  // Returns checksummed
decodeValueContent('Number', '0x00...0a');  // 10
```

#### `decodeMappingKey(keyHash, keyNameOrSchema)` — Decode dynamic key parts
```js
ERC725.decodeMappingKey(
  '0x35e6950bc8d21a1699e50000cafecafecafecafecafecafecafecafecafecafe',
  'MyKeyName:<address>'
);
// [{ type: 'address', value: '0xCAfEcAfeCAfECaFeCaFecaFecaFECafECafeCaFe' }]
```

#### `getSchema(keys)` — Look up schema by hashed key
```js
erc725.getSchema('0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5');
// { name: 'LSP3Profile', keyType: 'Singleton', ... }
```

### Utility

#### `isDynamicKeyName(keyName)` — Check for dynamic parts
```js
import { isDynamicKeyName } from '@erc725/erc725.js';
isDynamicKeyName('LSP3Profile');  // false
isDynamicKeyName('LSP5ReceivedAssetsMap:<address>');  // true
```

---

## Common Patterns for LUKSO Development

### Read a Universal Profile
```js
import ERC725 from '@erc725/erc725.js';
import { LSP3Schema } from '@erc725/erc725.js/schemas';

const erc725 = new ERC725(LSP3Schema, profileAddress, 'https://rpc.lukso.gateway.fm', {
  ipfsGateway: 'https://api.universalprofile.cloud/ipfs/',
});

const profile = await erc725.fetchData('LSP3Profile');
```

### Read Permissions
```js
import { LSP6Schema } from '@erc725/erc725.js/schemas';
const erc725 = new ERC725(LSP6Schema, upAddress, RPC_URL);

const permissions = await erc725.getData('AddressPermissions[]');
// All addresses with permissions

const specificPerms = await erc725.getData({
  keyName: 'AddressPermissions:Permissions:<address>',
  dynamicKeyParts: [controllerAddress],
});
```

### Encode Data for setData Transaction
```js
const { keys, values } = erc725.encodeData([{
  keyName: 'LSP3Profile',
  value: { json: myProfileJSON, url: 'ipfs://QmNew...' },
}]);

// Use with ethers/viem to call setDataBatch(keys, values) on the UP contract
```

### Read Received Assets
```js
import { LSP5Schema } from '@erc725/erc725.js/schemas';
const erc725 = new ERC725(LSP5Schema, upAddress, RPC_URL);
const assets = await erc725.getData('LSP5ReceivedAssets[]');
```

### Read Issued Assets
```js
import { LSP12Schema } from '@erc725/erc725.js/schemas';
const erc725 = new ERC725(LSP12Schema, upAddress, RPC_URL);
const issued = await erc725.getData('LSP12IssuedAssets[]');
```

---

## Important Notes

- **Array encoding:** When modifying arrays, always set `totalArrayLength` correctly to avoid corrupting the array length in the contract
- **Dynamic keys:** Use `dynamicKeyParts` for Mapping/MappingWithGrouping key types
- **VerifiableURI:** Can pass `{ json, url }` for auto-hashing, or `{ verification: { method, data }, url }` for pre-computed hashes
- **Backend usage:** Install `isomorphic-fetch` alongside the package
- **ES6 in Node.js:** Use `.mjs` extension or configure project for ES modules
- **Options are mutable:** `erc725.options.address`, `erc725.options.ipfsGateway`, `erc725.options.schema` can be changed after instantiation
- **Provider cannot be changed** after instantiation
