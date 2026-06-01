# 🔐 SecretCodex

Generate creative code names and encode/decode secret messages with classic and sophisticated ciphers. Blends nostalgic decoder ring fun with modern cryptographic techniques.

## What This Skill Does

SecretCodex brings back the magic of decoder rings, but with serious cryptographic sophistication:

- 🏷️ **Generate creative code names** for operations, team members, and locations
- 🔒 **Encode secret messages** using 10+ cipher methods (Caesar, Vigenère, Playfair, Rail Fence, OTP, and more)
- 🔓 **Decode messages** from friends/family (with the key they share)
- 🎓 **Learn cryptography** through hands-on examples
- 🎮 **Create puzzles** for scavenger hunts and games
- 🔑 **Master key management** (the real secret to security)

## Installation

### Via ClawHub CLI (Recommended)

```bash
# Search for the skill
clawhub search secretcodex

# Install
clawhub install secretcodex
```

### Manual Installation

```bash
mkdir -p ~/.openclaw/skills/secretcodex
cp SKILL.md ~/.openclaw/skills/secretcodex/
openclaw reload-skills
```

## Quick Start Examples

### Example 1: Generate a Code Name

```
You: Generate a code name for our Q2 product launch. Tone: professional but exciting.

AI: CODE NAME OPTIONS:

1. Operation Silver Dawn
   - Silver: Premium, valuable
   - Dawn: New beginning, fresh start
   - Phonetic: SILVER DON

2. Project Velocity Edge
   - Velocity: Speed, momentum
   - Edge: Cutting-edge, advantage
   
3. Operation Horizon Shift
   - Horizon: Future vision
   - Shift: Transformation

Recommendation: "Operation Silver Dawn" - professional, aspirational, memorable.
```

### Example 2: Encode a Secret Message

```
You: I want to send a secret message to my friend: "MEET ME AT THE LIBRARY AT NOON". 
What's a good cipher?

AI: For casual secret-keeping, I recommend Vigenère cipher:

METHOD: Vigenère Cipher
KEY: Choose a keyword you and your friend know (e.g., "FORTRESS")

ENCODING:
Plaintext: MEET ME AT THE LIBRARY AT NOON
Keyword: FORTRESSFORTRESSFORTRE SSFO RT
Ciphertext: RXJG ZR UG GUR VPYKEXI UG ATTR

HOW TO SHARE:
1. Send encrypted message: "RXJG ZR UG GUR VPYKEXI UG ATTR"
2. Share key separately: Tell friend "FORTRESS" in person or via different channel
3. Friend uses keyword to decrypt

DECODING (for your friend):
[Provides step-by-step Vigenère decryption process]
```

### Example 3: Decode a Received Message

```
You: My friend sent me this: "WKLV LV D VHFUHW". They said to use shift 3.

AI: This is a Caesar Cipher with shift 3!

DECODING:
Ciphertext: WKLV LV D VHFUHW
Shift backward by 3:

W → T (shift -3)
K → H (shift -3)
L → I (shift -3)
V → S (shift -3)
...

Plaintext: THIS IS A SECRET

Your friend's message says: "THIS IS A SECRET"
```

### Example 4: Create a Scavenger Hunt

```
You: I'm creating a scavenger hunt. I need 3 encoded clues, progressively harder.

AI: Here's your progressive cipher challenge:

CLUE 1 (Easy - Caesar Shift 5):
Plaintext: LOOK UNDER THE OAK TREE
Ciphertext: QTTP ZSIJW YMJ TPF YWJJ
Key: "Shift 5 forward"

CLUE 2 (Medium - Rail Fence 3 rails):
Plaintext: CHECK THE GARDEN SHED
Ciphertext: CHC TEADE HE GRN SHED
Key: "3 rails, zigzag"

CLUE 3 (Hard - Vigenère):
Plaintext: FINAL PRIZE IN THE MAILBOX
Keyword: TREASURE
Ciphertext: YRLVM TZRLX RL GMX TTRVEBK
Key: "TREASURE"

Participants solve each to get the next key!
```

### Example 5: Layered Security (Hybrid)

```
You: I need maximum security for a message. How do I layer ciphers?

AI: For strong security, use DOUBLE ENCRYPTION:

MESSAGE: "ATTACK AT DAWN"

STEP 1: Vigenère with keyword "FORTRESS"
Result: "FMMPBK PY KPDS"

STEP 2: Rail Fence with 4 rails
Input: FMMPBKPYKPDS
Output: FKYPB MDPMK S

FINAL CIPHERTEXT: "FKYPB MDPMK S"

TO DECODE:
1. Friend reverses Rail Fence (4 rails) → gets "FMMPBKPYKPDS"
2. Friend decrypts Vigenère ("FORTRESS") → gets "ATTACK AT DAWN"

Key sharing: "FORTRESS, then 4 rails" (share in person!)
```

## Key Features

### 🏷️ Code Name Generation

**Types:**
- Operation names (Silver Dawn, Crimson Falcon)
- Personal codenames (Phoenix, Atlas, Cipher)
- Location codes (Raven's Point, Glacier Station)

**Styles:**
- Professional/Serious
- Playful/Fun
- Technical/Precise
- Mysterious/Covert

### 🔒 Classic Ciphers (Decoder Ring Era)

- **Caesar Cipher**: Shift alphabet (⭐☆☆☆☆)
- **ROT13**: Fixed shift by 13 (⭐☆☆☆☆)
- **Atbash**: Reverse alphabet (⭐☆☆☆☆)
- **Pigpen**: Symbol substitution (⭐⭐☆☆☆)

### 🔐 Intermediate Ciphers

- **Polybius Square**: Grid coordinates (⭐⭐☆☆☆)
- **Vigenère**: Keyword-based shift (⭐⭐⭐☆☆)
- **Rail Fence**: Zigzag transposition (⭐⭐☆☆☆)

### 🛡️ Advanced Ciphers

- **Playfair**: Digraph substitution (⭐⭐⭐⭐☆)
- **Columnar Transposition**: Keyword ordering (⭐⭐⭐☆☆)
- **One-Time Pad**: Theoretically unbreakable (⭐⭐⭐⭐⭐)

### 🔗 Hybrid Methods

- **Double Encryption**: Layer two ciphers
- **Polybius + Vigenère**: Numbers + keyword
- **Custom combinations**: Mix and match

### 🔑 Key Management

- Key generation strategies
- Secure sharing methods (in-person, separate channels)
- Key rotation best practices
- Security rules and warnings

## Cipher Selection Guide

### By Use Case

| Use Case | Recommended Cipher | Why |
|----------|-------------------|-----|
| Quick note to friend | Caesar, ROT13 | Fast, easy |
| Scavenger hunt | Pigpen, Rail Fence | Visual fun |
| Casual secret | Vigenère | Keyword-based |
| Strong privacy | Playfair, Hybrid | Resists attacks |
| Maximum security | One-Time Pad | Perfect (if done right) |

### By Difficulty

| Skill Level | Cipher | Time to Learn |
|-------------|--------|--------------|
| Beginner | Caesar, Atbash | 5 minutes |
| Intermediate | Vigenère, Polybius | 15 minutes |
| Advanced | Playfair, OTP | 30+ minutes |

## What Makes This Unique

Unlike online cipher tools, SecretCodex:

1. **Teaches you HOW** - Not just "paste and encrypt"
2. **Generates code names** - Creative operation naming
3. **Emphasizes key management** - The real security
4. **Nostalgic but sophisticated** - Decoder rings meet modern crypto
5. **Educational** - Learn the math and logic
6. **Flexible** - Mix techniques for custom strength

## Requirements

- **OpenClaw**: Compatible with OpenClaw 2.0+
- **Dependencies**: None - pure knowledge skill
- **API Keys**: Not required
- **External Tools**: Not required

## Use Cases

### For Friends & Family
- Secret messages between kids
- Surprise party coordination
- Private notes to loved ones

### For Games & Puzzles
- Scavenger hunt clues
- Escape room puzzles
- Mystery games
- ARG (Alternate Reality Games)

### For Learning
- Understanding cryptography
- Teaching security concepts
- Historical ciphers
- Key management practice

### For Teams
- Code names for projects
- Light obfuscation (not sensitive data!)
- Fun team building

## Important Security Notes

### SecretCodex IS:
✅ Educational and fun
✅ Good for casual messages
✅ Great for learning crypto
✅ Perfect for games and puzzles

### SecretCodex IS NOT:
❌ Not for truly sensitive data
❌ Not a replacement for AES/RSA
❌ Not protection against determined attackers
❌ Not for financial/medical/legal info

### For Real Security, Use:
- **Modern encryption**: AES-256, RSA-2048
- **Encrypted apps**: Signal, WhatsApp (end-to-end)
- **Password managers**: 1Password, Bitwarden
- **VPNs**: For network security

**SecretCodex is for fun, learning, and casual privacy—not bank passwords!**

## Educational Value

SecretCodex teaches:
- **Cryptographic thinking**: How to obscure information
- **Key management**: The hardest part of security
- **Attack vectors**: How ciphers can be broken
- **Historical context**: Evolution of cryptography
- **Practical skills**: Encoding/decoding by hand

## Tips for Success

1. **Start simple** - Master Caesar before attempting Playfair
2. **Practice key sharing** - Security is only as strong as key management
3. **Don't skip steps** - Understand the math, not just the result
4. **Try breaking ciphers** - Learn by attempting to crack them
5. **Layer for strength** - Hybrid methods resist attacks better
6. **Have fun!** - Cryptography should be enjoyable

## Version History

- **v1.0.0** (February 2026): Initial release
  - Code name generation
  - 10+ cipher methods
  - Key management guidance
  - Educational challenges
  - Hybrid encryption techniques

## Contributing

Found a cool cipher to add? Contributions welcome!

1. Fork the repository
2. Add new cipher with examples
3. Submit a pull request

## License

MIT License - Use, modify, and share freely!

## Author

Created by AM for the OpenClaw community.

## Acknowledgments

Inspired by decoder rings, historical cryptographers, and the joy of secret messages.

---

**"The best cipher is one your friend can decode, but nobody else can crack!"** 🔐

*Remember: Share keys wisely, change them often, and keep the fun alive!*
