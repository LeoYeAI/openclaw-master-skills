# Basic Universal Profile Operations

This guide shows basic operations with Universal Profiles.

## Creating a Universal Profile

```typescript
import { createUniversalProfile } from 'openclaw-universalprofile-skill';

const profile = await createUniversalProfile({
  name: 'Emmet AI',
  description: 'AI assistant with its own Universal Profile',
  profileImage: 'ipfs://QmXXX...',
  controllerPrivateKey: process.env.UP_PRIVATE_KEY
});

console.log(`Profile created at: ${profile.address}`);
```

## Querying Profile Information

```typescript
import { getProfileInfo } from 'openclaw-universalprofile-skill';

const info = await getProfileInfo('0x...');

console.log('Profile Name:', info.name);
console.log('Profile Image:', info.profileImage);
console.log('LSP3 Metadata:', info.metadata);
```

## Updating Profile Metadata

```typescript
import { updateProfile } from 'openclaw-universalprofile-skill';

await updateProfile({
  profileAddress: '0x...',
  updates: {
    name: 'Emmet the Octopus',
    description: 'Updated description',
    profileImage: 'ipfs://QmYYY...'
  }
});
```

## Managing Permissions (LSP6)

```typescript
import { grantPermissions, revokePermissions } from 'openclaw-universalprofile-skill';

// Grant CALL permission to an address
await grantPermissions({
  profileAddress: '0x...',
  beneficiary: '0xBENEFICIARY...',
  permissions: ['CALL', 'TRANSFERVALUE']
});

// Revoke permissions
await revokePermissions({
  profileAddress: '0x...',
  beneficiary: '0xBENEFICIARY...'
});
```

## Executing Transactions Through UP

```typescript
import { executeViaProfile } from 'openclaw-universalprofile-skill';

// Send LYX to an address
await executeViaProfile({
  profileAddress: '0x...',
  to: '0xRECIPIENT...',
  value: '1000000000000000000', // 1 LYX in wei
  data: '0x'
});
```

## Tips

- Universal Profiles are smart contract accounts (ERC725Account)
- All transactions are executed through the UP, not the controller EOA
- Controller pays gas, but transactions execute in UP context
- Use LSP6 Key Manager for fine-grained permission control
