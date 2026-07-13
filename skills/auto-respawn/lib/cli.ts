/**
 * CLI argument parsing and validation utilities.
 *
 * Extracted from auto-respawn.ts so they can be tested independently.
 */

export const COMMANDS_WITH_SUBCOMMANDS = new Set(['wallet'])

export function parseArgs(argv: string[]): {
  command: string
  subcommand?: string
  flags: Record<string, string>
  positional: string[]
} {
  const args = argv.slice(2)
  const command = args[0] || ''
  const hasSubcommand = COMMANDS_WITH_SUBCOMMANDS.has(command)
  const subcommand = hasSubcommand && args[1] && !args[1].startsWith('--') ? args[1] : undefined
  const flags: Record<string, string> = {}
  const positional: string[] = []

  let i = subcommand ? 2 : 1
  while (i < args.length) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2)
      const next = args[i + 1]
      if (next && !next.startsWith('--')) {
        flags[key] = next
        i += 2
      } else {
        flags[key] = 'true'
        i++
      }
    } else {
      positional.push(args[i])
      i++
    }
  }

  return { command, subcommand, flags, positional }
}

/**
 * Validate that an amount string is a positive number.
 * Throws on invalid input so callers can handle the error.
 */
export function validateAmount(amount: string, minimum?: number): void {
  const n = Number(amount)
  if (!Number.isFinite(n) || n <= 0) {
    throw new Error(`Invalid amount: "${amount}". Must be a positive number (e.g. "1.5").`)
  }
  if (minimum != null && n < minimum) {
    throw new Error(
      `Amount ${amount} is below the minimum of ${minimum}. Cross-domain transfers require at least ${minimum} AI3/tAI3.`,
    )
  }
}
