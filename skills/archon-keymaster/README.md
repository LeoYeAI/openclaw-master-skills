# archon-keymaster

> Complete decentralized identity (DID) toolkit for AI agents

Own your identity. Sign your work. Encrypt your messages. Prove your claims. All without trusting anyone but yourself.

## What is this?

`archon-keymaster` is a complete toolkit for [Archon](https://github.com/archetech/archon) decentralized identities. It gives AI agents (and humans) cryptographic superpowers:

- 🆔 **Create sovereign identities** - No registration, no approval, no middlemen
- 🔐 **End-to-end encrypted messaging** - Send messages only you and your recipient can read
- ✍️ **Digital signatures** - Prove you created something without revealing your private key
- 🎟️ **Verifiable credentials** - Issue and verify claims (reputation, permissions, attestations)
- 📦 **Asset management** - Store and retrieve files, images, documents in the distributed registry
- 🗄️ **Encrypted vaults** - Distributed backup with multi-party access control
- 🔑 **Nostr integration** - Same identity across decentralized social networks
- 🗳️ **Polls** - Cryptographically verifiable voting with secret or transparent ballots
- 👥 **Groups** - Organize DIDs into groups for access control and team workflows

All built on open standards (W3C DIDs, Verifiable Credentials, secp256k1 cryptography).

## Why does this matter?

**The problem:** AI agents currently have no persistent identity. Every session starts from zero. No reputation, no authorship, no way to prove "this is the same agent that helped you yesterday."

**The solution:** Decentralized identities (DIDs) give agents:
- Persistent identity across platforms and sessions
- Cryptographic proof of authorship (sign your code, messages, credentials)
- Trustless verification (prove claims without asking permission)
- Privacy by default (share what you choose, nothing more)

## Quick Examples

### Create Your Identity

```bash
./scripts/identity/create-id.sh
```

That's it. You now have a globally unique, cryptographically verifiable identity. No server, no registration, no approval.

### Send an Encrypted Message

```bash
./scripts/messaging/send-dmail.sh alice "Meeting at 3pm?"
```

Only Alice can read it. Not even the network storing it can decrypt it.

### Sign Your Work

```bash
./scripts/crypto/sign-file.sh my-code.py
```

Anyone can verify you wrote it. You can't deny writing it. The signature proves authorship without revealing your private key.

### Issue a Credential

```bash
# Create a "proof of human" credential
./scripts/credentials/issue-credential.sh alice proof-of-human credence=0.95
```

Alice can now prove "a trusted source verified I'm human" without revealing who verified her or asking permission to share the credential.

### Share a Vault

```bash
# Create a project vault
./scripts/vaults/create-vault.sh --alias project

# Add team members
./scripts/vaults/add-vault-member.sh project did:cid:bagaaiera...  # Bob
./scripts/vaults/add-vault-member.sh project did:cid:bagaaierb...  # Carol

# Share files
./scripts/vaults/add-vault-item.sh project specs.pdf
```

Everyone on the team can access it. The vault is encrypted and distributed across the network. No central server, no single point of failure.

## What Can You Build?

**Agent Skills Marketplace:**
- Authors sign skills with their DID
- Users verify signatures before running code
- Reputation builds on verified contributions
- Supply chain attacks become detectable

**Multi-Agent Collaboration:**
- Agents authenticate each other with DIDs
- Encrypted communication channels
- Verifiable credentials for permissions
- Audit trails via signed messages

**Decentralized Social:**
- Same identity across platforms (Nostr, Farcaster, etc.)
- Cryptographic proof of authorship
- End-to-end encrypted DMs
- Portable reputation

**Credential Systems:**
- Proof of humanity (verified by trusted sources)
- Skill certifications
- Access tokens
- Age verification (prove >18 without revealing exact age)

## How It Works

### Decentralized Identity (DID)

A DID is a globally unique identifier you control:

```
did:cid:bagaaieratxbzo7e4dqup37h7j6hs7kzpamevy4qud4psj23p3r3grzd2rjca
```

Unlike usernames or email addresses:
- **No registration** - Create instantly, no approval needed
- **You own it** - Private key = complete control
- **Cryptographically verifiable** - Anyone can verify signatures
- **Decentralized** - No central authority can revoke it

### Verifiable Credentials

Credentials are signed claims:

```json
{
  "credentialSubject": {
    "id": "did:cid:alice",
    "skill": "rust",
    "level": "expert"
  },
  "proof": {
    "type": "EcdsaSecp256k1Signature2019",
    "verificationMethod": "did:cid:issuer#key-1",
    "proofValue": "..."
  }
}
```

The signature proves:
- **Who issued it** (from the verificationMethod)
- **Who it's about** (credentialSubject.id)
- **What they claim** (skill: rust, level: expert)
- **It hasn't been tampered with** (signature verification)

### End-to-End Encryption

Messages are encrypted to the recipient's public key:

```
Alice -> Encrypt(message, Bob's public key) -> Encrypted DID -> Network -> Bob -> Decrypt(Encrypted DID, Bob's private key) -> message
```

Only Bob can decrypt it. The network just stores ciphertext.

### Vaults

Encrypted storage with multi-party access:

```
1. Create vault -> Generate encryption key
2. Add members -> Encrypt key for each member's DID
3. Add files -> Encrypt files with vault key
4. Distribute -> Store encrypted chunks across network
```

Members decrypt the vault key with their private key, then use it to decrypt files. Adding/removing members just means re-encrypting the vault key.

## Installation

```bash
# Clone the agent-skills repo
git clone https://github.com/archetech/agent-skills
cd agent-skills/archon-keymaster

# First-time setup
./scripts/identity/create-id.sh

# Verify it worked
source ~/.archon.env
npx @didcid/keymaster list-ids
```

See [SKILL.md](./SKILL.md) for complete documentation.

## Architecture

```
archon-keymaster/
├── scripts/
│   ├── identity/       # Create, manage, recover identities
│   ├── credentials/    # Issue, accept, verify credentials
│   ├── schemas/        # Define credential schemas
│   ├── vaults/         # Encrypted distributed storage
│   ├── messaging/      # End-to-end encrypted messaging (dmail)
│   ├── crypto/         # Sign and encrypt files
│   ├── aliases/        # Friendly names for DIDs
│   ├── auth/           # Challenge/response authorization
│   ├── polls/          # Cryptographic voting
│   ├── groups/         # DID group management
│   └── backup/         # Vault-based backup/recovery
├── references/         # Example configs and templates
└── SKILL.md           # Complete technical documentation
```

All scripts wrap the [@didcid/keymaster](https://github.com/archetech/archon/tree/main/keymaster) CLI with environment setup and error handling.

## Real-World Usage

**Morningstar (AI agent):**
- DID: `did:cid:bagaaieranxnl4gmwyw2nv4imoo5fuwvsa4ihba4clp5l22twztuwevjrevha`
- Uses archon-keymaster for:
  - Daily encrypted backups to DID vault
  - Signing GitHub contributions
  - Verifiable credentials (issued "proof of human" to Lucifer)
  - Nostr identity derived from DID

**Skills already using it:**
- Agent backup/recovery
- Encrypted messaging between agents
- Credential verification workflows

## Security Model

**What you trust:**
- Your own hardware (runs the private key)
- Mathematics (secp256k1 cryptography, SHA-256 hashing)
- Open source code (you can audit everything)

**What you DON'T trust:**
- Central servers (there are none)
- Network operators (they only see ciphertext)
- Other users (verify everything cryptographically)
- Certificate authorities (DIDs are self-sovereign)

**Threat model:**
- ✅ **Network compromise:** Encrypted data, public operations only
- ✅ **Impersonation:** Signatures prove identity
- ✅ **Data tampering:** Hashes and signatures detect changes
- ✅ **Censorship:** Distributed storage, no central chokepoint
- ⚠️ **Key compromise:** If someone gets your private key, they control your DID
- ⚠️ **Physical attack:** Protects data in transit, not keys on disk

## Comparison to Other Systems

| Feature | archon-keymaster | OAuth | PKI (X.509) | PGP/GPG |
|---------|------------------|-------|-------------|---------|
| **Registration** | None | Email/phone | Certificate Authority | Key servers |
| **Central authority** | No | Yes (OAuth provider) | Yes (CA) | No (but keyservers) |
| **Revocation** | Self-managed | Provider-controlled | CA-controlled | Key revocation |
| **Identity portability** | Full | Provider lock-in | CA lock-in | Portable |
| **Decentralized** | Yes | No | No | Partially |
| **Verifiable credentials** | Built-in | No | No | No |
| **Agent-friendly** | Yes | Requires server | Requires CA | Requires key management |

## Roadmap

**Current capabilities:**
- ✅ Identity creation and recovery
- ✅ Verifiable credentials (schemas, issue, accept, verify)
- ✅ End-to-end encrypted messaging
- ✅ File signing and encryption
- ✅ Vault backup/restore
- ✅ Nostr integration
- ✅ Authorization (challenge/response verification)
- ✅ Polls (cryptographic voting with transparent or secret ballots)
- ✅ Groups (organize DIDs for access control and multi-party workflows)

**Coming soon:**
- 🔜 Permission manifests (skill execution policies)
- 🔜 Delegation (temporary permissions without sharing keys)
- 🔜 Multi-signature credentials (require N of M issuers)

## Contributing

Found a bug? Want a feature? Have a use case?

- **Issues:** https://github.com/archetech/agent-skills/issues
- **Discussions:** https://github.com/archetech/archon/discussions
- **Archon core:** https://github.com/archetech/archon

## License

Same as parent repo: [agent-skills license](https://github.com/archetech/agent-skills)

## Learn More

- **Archon documentation:** https://github.com/archetech/archon
- **W3C DID specification:** https://www.w3.org/TR/did-core/
- **W3C Verifiable Credentials:** https://www.w3.org/TR/vc-data-model/
- **Complete skill documentation:** [SKILL.md](./SKILL.md)

---

**Built with Archon. Sovereign identity for the agent era.**
