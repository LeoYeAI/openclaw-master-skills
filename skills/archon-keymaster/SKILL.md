---
name: archon-keymaster
description: Core Archon DID toolkit - identity management, verifiable credentials, encrypted messaging (dmail), Nostr integration, file encryption/signing, aliasing, authorization (challenge/response), groups, and cryptographic polls. Use for creating/managing DIDs, issuing/accepting verifiable credentials, sending encrypted messages between DIDs, deriving Nostr keypairs, encrypting/signing files, managing DID aliases, challenge/response authorization, managing DID groups, or running cryptographically verifiable polls. For vaults/backups see archon-vault; for ecash see archon-cashu.
metadata:
  openclaw:
    requires:
      env:
        - ARCHON_WALLET_PATH
        - ARCHON_PASSPHRASE
        - ARCHON_GATEKEEPER_URL
      bins:
        - node
        - npx
      anyBins:
        - jq
        - openssl
    primaryEnv: ARCHON_PASSPHRASE
    emoji: "🔐"
---

# Archon Keymaster - Core DID Toolkit

Core toolkit for Archon decentralized identities (DIDs). Manages identity lifecycle, encrypted communication, cryptographic operations, and authorization.

**Related skills:**
- `archon-vault` — Vault management and encrypted distributed backups
- `archon-cashu` — Cashu ecash with DID-locked tokens

## Capabilities

- **Identity Management** - Create, manage multiple DIDs, recover from mnemonic
- **Verifiable Credentials** - Create schemas, issue/accept/revoke credentials
- **Encrypted Messaging (Dmail)** - Send/receive end-to-end encrypted messages between DIDs
- **Nostr Integration** - Derive Nostr keypairs from your DID (same secp256k1 key)
- **File Encryption** - Encrypt files for specific DIDs
- **Digital Signatures** - Sign and verify files with your DID
- **DID Aliasing** - Friendly names for DIDs (contacts, schemas, credentials)
- **Authorization** - Challenge/response verification between DIDs
- **Groups** - Create and manage DID groups for access control and multi-party operations
- **Polls** - Cryptographic voting with transparent or secret ballots
- **Assets** - Store and retrieve content-addressed assets in the registry

## Prerequisites

- Node.js installed (for `npx @didcid/keymaster`)
- Environment: `~/.archon.env` with:
  - `ARCHON_WALLET_PATH` - path to your wallet file (required)
  - `ARCHON_PASSPHRASE` - wallet encryption passphrase (required)
  - `ARCHON_GATEKEEPER_URL` - gatekeeper endpoint (optional, defaults to public)
- All created automatically by `create-id.sh`

## Security Notes

This skill handles cryptographic identity operations:

1. **Passphrase in environment**: `ARCHON_PASSPHRASE` is stored in `~/.archon.env` for non-interactive script execution. The file should be `chmod 600`.

2. **Sensitive files accessed**:
   - `~/.archon.wallet.json` — encrypted wallet containing DID private keys
   - `~/.archon.env` — wallet encryption passphrase

3. **Network**: Data is encrypted before transmission to Archon gatekeeper/hyperswarm. Only intended recipients can decrypt.

4. **Key recovery**: Your 12-word mnemonic is the master recovery key. Store it offline, never in digital form.

## Quick Start

### First-Time Setup

```bash
./scripts/identity/create-id.sh [wallet-path]
```

Creates your first DID, generates passphrase, saves to `~/.archon.env`. 

- Default wallet location: `~/.archon.wallet.json`
- You can specify a custom path: `./scripts/identity/create-id.sh ~/my-wallet.json`
- **Write down your 12-word mnemonic** - it's your master recovery key.

### Load Environment

All scripts require `~/.archon.env` to be configured. Simply run:

```bash
source ~/.archon.env
```

The environment file sets `ARCHON_WALLET_PATH` and `ARCHON_PASSPHRASE`. Scripts will error if these are not set.

## Identity Management

### Create Additional Identity

```bash
./scripts/identity/create-additional-id.sh <name>
```

Create pseudonymous personas or role-separated identities (all share same mnemonic).

### List All DIDs

```bash
./scripts/identity/list-ids.sh
```

### Switch Active Identity

```bash
./scripts/identity/switch-id.sh <name>
```

### Recovery

For disaster recovery and vault restore operations, see the `archon-backup` skill.

## Verifiable Credential Schemas

Create and manage schemas for verifiable credentials.

### Create Schema

```bash
./scripts/schemas/create-schema.sh <schema-file.json>
```

Create a credential schema from a JSON file.

**Example schema (proof-of-human.json):**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$credentialContext": [
    "https://www.w3.org/ns/credentials/v2",
    "https://archetech.com/schemas/credentials/agent/v1"
  ],
  "$credentialType": [
    "VerifiableCredential",
    "AgentCredential",
    "ProofOfHumanCredential"
  ],
  "name": "proof-of-human",
  "description": "Verifies human status",
  "properties": {
    "credence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence level (0-1) that subject is human"
    }
  },
  "required": ["credence"]
}
```

```bash
./scripts/schemas/create-schema.sh proof-of-human.json
# Returns: did:cid:bagaaiera4yl4xi...
```

### List Your Schemas

```bash
./scripts/schemas/list-schemas.sh
```

Lists all schemas you own.

### Get Schema

```bash
./scripts/schemas/get-schema.sh <schema-did-or-alias>
```

Retrieve schema definition by DID or alias.

## Verifiable Credentials

Issue, accept, and manage verifiable credentials.

### Issuing Credentials (3-step process)

#### 1. Bind Credential to Subject

```bash
./scripts/credentials/bind-credential.sh <schema-did-or-alias> <subject-did-or-alias>
```

Creates a bound credential template file for the subject.

**Example:**
```bash
./scripts/credentials/bind-credential.sh proof-of-human-schema alice
# Creates: bagaaierb...BOUND.json  (subject DID without 'did:cid:' prefix)
```

#### 2. Fill in Credential Data

Edit the `.BOUND.json` file and fill in the `credentialSubject` data:

```json
{
  "credentialSubject": {
    "id": "did:cid:bagaaierb...",
    "credence": 0.97
  }
}
```

#### 3. Issue Credential

```bash
./scripts/credentials/issue-credential.sh <bound-file.json>
```

Signs and encrypts the credential. Returns the credential DID. The underlying `@didcid/keymaster` command may save output files - refer to Keymaster documentation for exact file output behavior.

**Example:**
```bash
./scripts/credentials/issue-credential.sh bagaaierb...BOUND.json
# Returns credential DID: did:cid:bagaaierc...
```

### Accepting Credentials

```bash
./scripts/credentials/accept-credential.sh <credential-did>
```

Accept and save a credential issued to you.

**Example:**
```bash
./scripts/credentials/accept-credential.sh did:cid:bagaaierc...
```

### Managing Credentials

#### List Your Credentials

```bash
./scripts/credentials/list-credentials.sh
```

Lists all credentials you've received.

#### List Issued Credentials

```bash
./scripts/credentials/list-issued.sh
```

Lists all credentials you've issued to others.

#### Get Credential

```bash
./scripts/credentials/get-credential.sh <credential-did-or-alias>
```

Retrieve full credential details.

### Publishing & Revoking

#### Publish Credential

```bash
./scripts/credentials/publish-credential.sh <credential-did>
```

Add credential to your public DID manifest (makes it visible to others).

#### Revoke Credential

```bash
./scripts/credentials/revoke-credential.sh <credential-did>
```

Revoke a credential you issued (invalidates it).

### Complete Example: Issuing Proof-of-Human

```bash
# 1. Create schema
./scripts/schemas/create-schema.sh proof-of-human.json
# Returns: did:cid:bagaaiera4yl4xi...

# 2. Add alias for convenience
./scripts/aliases/add-alias.sh proof-of-human-schema did:cid:bagaaiera4yl4xi...

# 3. Bind credential to Alice
./scripts/credentials/bind-credential.sh proof-of-human-schema alice
# Creates: bagaaierb...BOUND.json  (alice's DID without prefix)

# 4. Edit file, set credence: 0.97

# 5. Issue credential
./scripts/credentials/issue-credential.sh bagaaierb...BOUND.json
# Returns: did:cid:bagaaierc...

# 6. Alice accepts it
./scripts/credentials/accept-credential.sh did:cid:bagaaierc...

# 7. Alice publishes to her manifest
./scripts/credentials/publish-credential.sh did:cid:bagaaierc...
```

## Encrypted Messaging (Dmail)

End-to-end encrypted messages between DIDs with attachment support.

### Send Message

```bash
./scripts/messaging/send.sh <recipient-did-or-alias> <subject> <body> [cc-did...]
```

Examples:
```bash
./scripts/messaging/send.sh alice "Meeting" "Let's sync tomorrow"
./scripts/messaging/send.sh did:cid:bag... "Update" "Status report" did:cid:bob...
```

### Check Inbox

```bash
./scripts/messaging/refresh.sh   # Poll for new messages
./scripts/messaging/list.sh      # List inbox
./scripts/messaging/list.sh unread  # Filter unread
```

### Read Message

```bash
./scripts/messaging/read.sh <dmail-did>
```

### Reply/Forward/Archive

```bash
./scripts/messaging/reply.sh <dmail-did> <body>
./scripts/messaging/forward.sh <dmail-did> <recipient-did> [body]
./scripts/messaging/archive.sh <dmail-did>
./scripts/messaging/delete.sh <dmail-did>
```

### Attachments

```bash
./scripts/messaging/attach.sh <dmail-did> <file-path>
./scripts/messaging/get-attachment.sh <dmail-did> <attachment-name> <output-path>
```

## Nostr Integration

Derive Nostr identity from your DID - same secp256k1 key, two protocols.

### Prerequisites

Install `nak` CLI:
```bash
curl -sSL https://raw.githubusercontent.com/fiatjaf/nak/master/install.sh | sh
```

### Derive Nostr Keys

```bash
./scripts/nostr/derive-nostr.sh
```

Outputs `nsec`, `npub`, and hex pubkey (derived from `m/44'/0'/0'/0/0`).

### Save Keys

```bash
mkdir -p ~/.clawstr
echo "nsec1..." > ~/.clawstr/secret.key
chmod 600 ~/.clawstr/secret.key
```

### Publish Nostr Profile

```bash
echo '{
  "kind": 0,
  "content": "{\"name\":\"YourName\",\"about\":\"Your bio. DID: did:cid:...\"}"
}' | nak event --sec $(cat ~/.clawstr/secret.key) \
  wss://relay.ditto.pub wss://relay.primal.net wss://relay.damus.io wss://nos.lol
```

### Update DID with Nostr Identity

```bash
npx @didcid/keymaster set-property YourIdName nostr \
  '{"npub":"npub1...","pubkey":"<hex-pubkey>"}'
```

## File Encryption & Signatures

### Encrypt Files

```bash
./scripts/crypto/encrypt-file.sh <input-file> <recipient-did-or-alias>
./scripts/crypto/encrypt-message.sh <message> <recipient-did-or-alias>
```

Returns encrypted DID (stored on-chain/IPFS). Only recipient can decrypt.

### Decrypt Files

```bash
./scripts/crypto/decrypt-file.sh <encrypted-did> <output-file>
./scripts/crypto/decrypt-message.sh <encrypted-did>
```

### Sign Files (Proof of Authorship)

```bash
./scripts/crypto/sign-file.sh <file.json>
```

**Important:** File must be JSON. Adds `proof` section with signature.

### Verify Signatures

```bash
./scripts/crypto/verify-file.sh <file.json>
```

Shows who signed it, when, and whether content was tampered with.

## DID Aliasing

Friendly names for DIDs - use "alice" instead of `did:cid:bagaaiera...`

### Add Alias

```bash
./scripts/aliases/add-alias.sh <alias> <did>
```

Examples:
```bash
./scripts/aliases/add-alias.sh alice did:cid:bagaaiera...
./scripts/aliases/add-alias.sh proof-of-human-schema did:cid:bagaaiera4yl4xi...
./scripts/aliases/add-alias.sh backup-vault did:cid:bagaaierab...
```

### Resolve Alias

```bash
./scripts/aliases/resolve-did.sh <alias-or-did>
```

Pass-through safe (returns DID unchanged if you pass a DID).

### List/Remove Aliases

```bash
./scripts/aliases/list-aliases.sh
./scripts/aliases/remove-alias.sh <alias>
```

**Note:** Aliases work in most Keymaster commands and all encryption/messaging scripts.

## Asset Management

Store and retrieve assets (files, images, documents, JSON data) in the distributed registry. Assets are content-addressed (DIDs) and support binary data via base64 encoding.

### List Assets

```bash
./scripts/assets/list-assets.sh
```

Lists all asset DIDs in the registry.

### Create Assets

#### From JSON Data (inline)

```bash
./scripts/assets/create-asset.sh '{"type":"document","title":"My Doc","content":"..."}'
```

#### From JSON File

```bash
./scripts/assets/create-asset-json.sh document.json
```

#### From File (any type)

```bash
./scripts/assets/create-asset-file.sh document.pdf application/pdf
```

Encodes file as base64 with metadata (filename, content-type).

#### From Image

```bash
./scripts/assets/create-asset-image.sh avatar.png
```

Auto-detects image type (png/jpg/gif/webp/svg) and encodes with metadata.

### Retrieve Assets

#### Get Asset (raw JSON)

```bash
./scripts/assets/get-asset.sh did:cid:bagaaiera...
```

Returns raw asset data.

#### Get Asset as JSON

```bash
./scripts/assets/get-asset-json.sh did:cid:bagaaiera...
```

Pretty-prints asset data.

#### Get File Asset

```bash
./scripts/assets/get-asset-file.sh did:cid:bagaaiera... [output-path]
```

Decodes base64 and saves to disk. Auto-detects filename if no output path provided.

#### Get Image Asset

```bash
./scripts/assets/get-asset-image.sh did:cid:bagaaiera... [output-path]
```

Decodes base64 and saves image. Auto-detects filename if no output path provided.

### Update Assets

#### Update with JSON Data

```bash
./scripts/assets/update-asset.sh did:cid:bagaaiera... '{"updated":true}'
```

#### Update with JSON File

```bash
./scripts/assets/update-asset-json.sh did:cid:bagaaiera... updated.json
```

#### Update with File

```bash
./scripts/assets/update-asset-file.sh did:cid:bagaaiera... newdoc.pdf application/pdf
```

#### Update with Image

```bash
./scripts/assets/update-asset-image.sh did:cid:bagaaiera... newavatar.png
```

### Transfer Assets

```bash
./scripts/assets/transfer-asset.sh did:cid:bagaaiera... did:cid:bagaaierat...
```

Transfer asset ownership to another DID.

### Use Cases

- **Skill Packages**: Store SKILL.md + scripts as signed assets
- **Profile Media**: Avatar images, banners
- **Documents**: PDFs, markdown files, archives
- **Data Sets**: JSON datasets, configuration files
- **Shared Resources**: Transfer assets between DIDs for collaboration

## Groups

Manage collections of DIDs for access control, multi-party operations, and organizational structure.

### Create Group

```bash
./scripts/groups/create-group.sh <group-name>
```

Creates a group and automatically aliases it by name.

Examples:
```bash
./scripts/groups/create-group.sh research-team
./scripts/groups/create-group.sh archetech-devs
```

### Add/Remove Members

```bash
./scripts/groups/add-member.sh <group> <member-did-or-alias>
./scripts/groups/remove-member.sh <group> <member-did-or-alias>
```

Examples:
```bash
./scripts/groups/add-member.sh research-team did:cid:bagaaiera...
./scripts/groups/add-member.sh devs alice
./scripts/groups/remove-member.sh devs alice
```

### List Groups

```bash
./scripts/groups/list-groups.sh
```

Lists all groups owned by your current identity.

### Get Group Details

```bash
./scripts/groups/get-group.sh <group-did-or-alias>
```

Shows group metadata and membership.

### Test Membership

```bash
./scripts/groups/test-member.sh <group> [member]
```

If member is omitted, tests whether your current identity is in the group.

Examples:
```bash
./scripts/groups/test-member.sh research-team           # Am I in this group?
./scripts/groups/test-member.sh research-team alice     # Is alice in this group?
```

### Use Cases

- **Access control** - Encrypt files for a group, all members can decrypt
- **Team management** - Organize DIDs by role or project
- **Multi-party workflows** - Define who can participate in group operations

## Authorization

Challenge/response flow for verifying a DID controls its private key. Used for agent-to-agent authentication, access control, and proof-of-identity workflows.

### Create a Challenge

```bash
# Create a basic challenge
./scripts/auth/create-challenge.sh

# Create a challenge as a specific DID alias
./scripts/auth/create-challenge.sh --alias myDID

# Create a challenge from a file
./scripts/auth/create-challenge.sh challenge-template.json

# Create a challenge tied to a specific credential
./scripts/auth/create-challenge-cc.sh did:cid:bagaaiera...
```

Output: a challenge DID (e.g., `did:cid:bagaaiera...`) that the responder must sign.

### Create a Response

```bash
CHALLENGE="did:cid:bagaaiera..."
./scripts/auth/create-response.sh "$CHALLENGE"
```

Output: a response DID containing a signed proof.

### Verify a Response

```bash
RESPONSE="did:cid:bagaaiera..."
./scripts/auth/verify-response.sh "$RESPONSE"
```

Output:
```json
{
    "challenge": "did:cid:...",
    "credentials": [],
    "requested": 0,
    "fulfilled": 0,
    "match": true,
    "responder": "did:cid:..."
}
```

`match: true` means the response is valid and cryptographically verified.

### Complete Authorization Flow

```bash
# Challenger creates a challenge
CHALLENGE=$(./scripts/auth/create-challenge.sh)

# Responder creates a response (proves they control their DID)
RESPONSE=$(./scripts/auth/create-response.sh "$CHALLENGE")

# Challenger verifies the response
./scripts/auth/verify-response.sh "$RESPONSE"
# → {"match": true, "responder": "did:cid:...", ...}
```

## Polls

Cryptographically verifiable voting with support for transparent or secret ballots. Voters are added directly to polls (no separate roster required).

### Create Poll Template

```bash
./scripts/polls/create-poll-template.sh
```

Outputs a v2 template JSON:
```json
{
    "version": 2,
    "name": "poll-name",
    "description": "What is this poll about?",
    "options": ["yes", "no", "abstain"],
    "deadline": "2026-03-01T00:00:00.000Z"
}
```

### Create Poll

```bash
./scripts/polls/create-poll.sh <poll-file.json> [options]
```

Creates a poll from a JSON template file. Returns poll DID.

**Options:**
- `--alias TEXT` - DID alias for the poll
- `--registry TEXT` - Registry URL (default: hyperswarm)

**Example:**
```bash
# Create poll template
./scripts/polls/create-poll-template.sh > my-poll.json

# Edit poll (set name, description, options, deadline)
vi my-poll.json

# Create the poll
./scripts/polls/create-poll.sh my-poll.json
# Returns: did:cid:bagaaiera...
```

### Manage Voters

Add, remove, or list eligible voters for a poll:

```bash
# Add a voter
./scripts/polls/add-poll-voter.sh <poll-did> <voter-did>

# Remove a voter
./scripts/polls/remove-poll-voter.sh <poll-did> <voter-did>

# List all eligible voters
./scripts/polls/list-poll-voters.sh <poll-did>
```

### Vote in Poll

```bash
./scripts/polls/vote-poll.sh <poll-did> <vote-index>
```

Cast a vote in a poll. Returns a ballot DID.

**Arguments:**
- `poll-did` - DID of the poll
- `vote-index` - Vote number: 0 = spoil, 1-N = option index

**Examples:**
```bash
# View poll first to see options
./scripts/polls/view-poll.sh did:cid:bagaaiera...
# Options: 1=yes, 2=no, 3=abstain

# Cast a vote for "yes" (option 1)
./scripts/polls/vote-poll.sh did:cid:bagaaiera... 1
# Returns: did:cid:bagaaierballot...

# Spoil ballot (vote 0)
./scripts/polls/vote-poll.sh did:cid:bagaaiera... 0
```

### Ballot Workflow

For distributed voting (voters not directly connected to poll owner):

```bash
# Voter creates and sends ballot
BALLOT=$(./scripts/polls/vote-poll.sh "$POLL" 1)
./scripts/polls/send-ballot.sh "$BALLOT" "$POLL"

# Poll owner receives and adds ballot
./scripts/polls/update-poll.sh "$BALLOT"

# View ballot details
./scripts/polls/view-ballot.sh "$BALLOT"
```

### Send Poll Notice

Notify all voters about a poll:

```bash
./scripts/polls/send-poll.sh <poll-did>
```

Creates a notice DID that voters can use to find and vote in the poll.

### View Poll

```bash
./scripts/polls/view-poll.sh <poll-did>
```

View poll details including options (with indices), deadline, and (if published) results.

### Publish Poll Results

Two options for publishing results:

**Secret ballots (default):**
```bash
./scripts/polls/publish-poll.sh <poll-did>
```
Publishes aggregate results while hiding individual votes.

**Transparent ballots:**
```bash
./scripts/polls/reveal-poll.sh <poll-did>
```
Publishes results with individual ballots visible (who voted for what).

### Unpublish Poll Results

```bash
./scripts/polls/unpublish-poll.sh <poll-did>
```

Remove published results from a poll.

### Complete Polling Example

```bash
# 1. Create poll template
./scripts/polls/create-poll-template.sh > team-vote.json

# 2. Edit poll:
# {
#   "version": 2,
#   "name": "proposal-vote",
#   "description": "Should we adopt the new proposal?",
#   "options": ["approve", "reject", "defer"],
#   "deadline": "2026-03-01T00:00:00.000Z"
# }

# 3. Create the poll
POLL=$(./scripts/polls/create-poll.sh team-vote.json)
echo "Poll created: $POLL"

# 4. Add eligible voters
./scripts/polls/add-poll-voter.sh "$POLL" did:cid:alice...
./scripts/polls/add-poll-voter.sh "$POLL" did:cid:bob...
./scripts/polls/add-poll-voter.sh "$POLL" did:cid:carol...

# 5. Notify voters
./scripts/polls/send-poll.sh "$POLL"

# 6. Members vote (1=approve, 2=reject, 3=defer)
./scripts/polls/vote-poll.sh "$POLL" 1   # Alice votes approve
./scripts/polls/vote-poll.sh "$POLL" 2   # Bob votes reject
./scripts/polls/vote-poll.sh "$POLL" 1   # Carol votes approve

# 7. View current status
./scripts/polls/view-poll.sh "$POLL"

# 8. After deadline, publish results (hiding who voted what)
./scripts/polls/publish-poll.sh "$POLL"

# OR publish transparently
./scripts/polls/reveal-poll.sh "$POLL"
```

### Use Cases

- **Governance decisions** - DAO-style voting with verifiable results
- **Team consensus** - Anonymous feedback or transparent decision-making
- **Multi-agent coordination** - Agents voting on shared resources
- **Access control** - Voting to add/remove group members

## Advanced Usage

### Multiple Identities (Pseudonymous Personas)

```bash
./scripts/identity/create-additional-id.sh pseudonym
./scripts/identity/create-additional-id.sh work-persona
./scripts/identity/switch-id.sh pseudonym
```

Use cases:
- Separate personal/work identities
- Anonymous participation
- Role-based access control

### Dmail Message Format

Dmails are JSON:
```json
{
  "to": ["did:cid:recipient1", "did:cid:recipient2"],
  "cc": ["did:cid:cc-recipient"],
  "subject": "Subject line",
  "body": "Message body",
  "reference": "did:cid:original-message"
}
```

Direct Keymaster commands:
```bash
npx @didcid/keymaster create-dmail message.json
npx @didcid/keymaster send-dmail <dmail-did>
npx @didcid/keymaster file-dmail <dmail-did> "inbox,important"
```

### Signature Verification

Signed files include proof:
```json
{
  "data": {"your": "content"},
  "proof": {
    "type": "EcdsaSecp256k1Signature2019",
    "created": "2026-02-10T20:41:26.323Z",
    "verificationMethod": "did:cid:bagaaiera...#key-1",
    "proofValue": "wju2GCn0QweP4bH6..."
  }
}
```

## Security Notes

### Cryptographic Security
- **Mnemonic is master key** - Store offline, write down, never digital
- **Passphrase encrypts wallet** - Protects wallet.json on disk
- **Aliases are local** - Not shared, fully decentralized
- **Dmail is end-to-end encrypted** - Only sender/recipients can read
- **Signatures are non-repudiable** - Can't deny creating valid signature
- **Backups persist** - As long as any hyperswarm node retains them

### Data Access Disclosure

This skill accesses sensitive data by design:

| Data | Scripts | Purpose |
|------|---------|---------|
| `~/.archon.wallet.json` | All scripts | Contains encrypted private keys |
| `~/.archon.env` | All scripts | Contains `ARCHON_PASSPHRASE` for non-interactive use |
| `~/.clawstr/secret.key` | Nostr scripts | Stores derived Nostr private key |

### Environment Variables

The following are set in `~/.archon.env`:
- `ARCHON_WALLET_PATH` - Path to wallet file
- `ARCHON_PASSPHRASE` - Wallet decryption passphrase (sensitive!)
- `ARCHON_GATEKEEPER_URL` - Optional, defaults to public gatekeeper

**Important**: `~/.archon.env` contains your passphrase in plaintext for script automation. Ensure:
```bash
chmod 600 ~/.archon.env  # Owner read/write only
```

### Network Transmission

Scripts connect to:
- `https://archon.technology` - Public gatekeeper (default)
- `localhost:4224` - Local gatekeeper (if configured)
- Hyperswarm DHT - Distributed storage network

All transmitted data is encrypted. No plaintext secrets leave your machine

## Troubleshooting

### Wallet/Passphrase Issues

**"Cannot read wallet":**
```bash
source ~/.archon.env
ls -la ~/clawd/wallet.json
```

**"Permission denied":**
```bash
chmod 600 ~/.archon.env
```

### Encryption/Signing

**"Cannot decrypt":**
- Ensure message was encrypted for YOUR DID
- Check passphrase is correct

**"Signature verification failed":**
- File modified after signing
- Signer's DID may be revoked

### Dmail

**"Messages not arriving":**
```bash
./scripts/messaging/refresh.sh  # Poll for new messages
```

**"Recipient can't decrypt":**
- Use correct recipient DID (not alias on their side)

## References

- Archon documentation: https://github.com/archetech/archon
- Keymaster reference: https://github.com/archetech/archon/tree/main/keymaster
- W3C DID specification: https://www.w3.org/TR/did-core/
