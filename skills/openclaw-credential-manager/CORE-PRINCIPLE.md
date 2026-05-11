# Core Principle: Centralized Credential Management

## This Is Not Optional

`.env` credential consolidation is a **mandatory security foundation** for OpenClaw deployments.

## Why This Matters

### Security Risk: Scattered Credentials

When credentials live in multiple locations:
```
~/.config/x/credentials.json          (mode 644 - WORLD READABLE!)
~/.config/service/api_keys.json       (no git protection)
~/project/.env                         (accidentally committed)
~/.bashrc                              (exported in shell history)
```

**Result:** Attack surface grows. One mistake compromises everything.

### The Foundation: Single Source of Truth

```
~/.openclaw/.env (mode 600)
```

**One file. One permission. One location to secure.**

## Non-Negotiable Requirements

### 1. File Permissions
```bash
chmod 600 ~/.openclaw/.env
```
Owner read/write ONLY. No group. No world.

### 2. Git Protection
```gitignore
.env
*.env
!.env.example
```
Never commit credentials. Ever.

### 3. Backup Strategy
Encrypted backups only. Or no backups.

### 4. Access Control
Minimize who/what can read `.env`:
- Your user account
- Processes you explicitly run
- Nothing else

## Why OpenClaw Enforces This

**Agent systems are privileged by design.**

An AI agent needs credentials to:
- Post on your behalf
- Execute transactions
- Access private data
- Control infrastructure

**If credentials leak, the agent becomes a weapon.**

## The Trade-Off

**Convenience vs Security:** We choose security.

Yes, scattered JSON files are "easier" to set up initially. But they're harder to:
- Audit
- Rotate
- Protect
- Monitor

`.env` is harder upfront, safer forever.

## Implementation Requirements

Every OpenClaw skill that needs credentials MUST:

1. ✅ Load from `~/.openclaw/.env`
2. ✅ Validate file permissions on load
3. ✅ Never log full credentials
4. ✅ Provide clear error if `.env` missing
5. ❌ Never accept credentials from CLI args
6. ❌ Never accept credentials from environment variables set in shell
7. ❌ Never create credential files outside `.env`

## Migration Is Mandatory

If you find credentials elsewhere:
1. Stop
2. Run credential-manager skill
3. Consolidate into `.env`
4. Validate security
5. Delete old files

**Do not proceed until credentials are properly secured.**

## The Standard

This isn't just best practice — it's the OpenClaw standard.

If a skill stores credentials anywhere other than `~/.openclaw/.env`, it's **non-compliant** and should not be used.

## Audit Checklist

Before deploying OpenClaw to production:

- [ ] All credentials in `~/.openclaw/.env`
- [ ] File mode is 600
- [ ] `.env` is in `.gitignore`
- [ ] No credentials in code
- [ ] No credentials in logs
- [ ] No credentials in shell history
- [ ] Backups are encrypted (or excluded)
- [ ] Team knows not to share `.env`

If any box is unchecked, **you're not ready**.

## Exception: None

There are no exceptions to this principle.

"But what about...":
- **Docker?** Mount `.env` securely
- **CI/CD?** Use secret managers, inject at runtime
- **Multiple environments?** `.env.dev`, `.env.prod` — same pattern
- **Team collaboration?** Share `.env.example`, not `.env`
- **Quick testing?** Still use `.env`

Every scenario has a secure solution. Use it.

## Why We're Strict

AI agents are powerful. With great power comes:
1. Greater responsibility
2. Bigger attack surface
3. More tempting target

**Scattered credentials + powerful agent = disaster waiting to happen.**

## The Foundation

Think of `.env` like:
- SSL/TLS for web servers (non-negotiable)
- Encryption for databases (mandatory)
- Authentication for APIs (required)

It's not a feature. It's the foundation everything else builds on.

---

**Bottom line:** If your credentials aren't in `~/.openclaw/.env` with mode 600, stop what you're doing and fix it first. Everything else can wait.

This is the hill we die on. 📺
