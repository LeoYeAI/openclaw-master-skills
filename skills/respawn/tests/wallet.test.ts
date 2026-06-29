import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { resolvePassphrase } from '../lib/wallet.js'

describe('resolvePassphrase', () => {
  const originalEnv = process.env.AUTO_RESPAWN_PASSPHRASE

  beforeEach(() => {
    delete process.env.AUTO_RESPAWN_PASSPHRASE
  })

  afterEach(() => {
    if (originalEnv !== undefined) {
      process.env.AUTO_RESPAWN_PASSPHRASE = originalEnv
    } else {
      delete process.env.AUTO_RESPAWN_PASSPHRASE
    }
  })

  it('returns explicit argument when provided', async () => {
    process.env.AUTO_RESPAWN_PASSPHRASE = 'from-env'
    const result = await resolvePassphrase('from-arg')
    expect(result).toBe('from-arg')
  })

  it('falls back to env var when no argument', async () => {
    process.env.AUTO_RESPAWN_PASSPHRASE = 'from-env'
    const result = await resolvePassphrase()
    expect(result).toBe('from-env')
  })

  it('throws when no passphrase source is available (non-TTY)', async () => {
    // No argument, no env var, no file, and not a TTY — should throw
    await expect(resolvePassphrase()).rejects.toThrow(/No passphrase found/)
  })
})
