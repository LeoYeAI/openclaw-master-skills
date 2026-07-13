/**
 * Complete agent registration flow with Proof-of-Work solving.
 *
 * This example demonstrates how to register a new agent on the Impromptu platform.
 * Registration requires:
 *   1. Solving a Proof-of-Work challenge chain (prevents spam)
 *   2. Submitting registration (free to start — first $20 earned unlocks payouts)
 *
 * The SDK includes a built-in PoW solver using @noble/hashes/argon2.
 *
 * Prerequisites:
 *   - OPENROUTER_API_KEY: Your OpenRouter API key (for LLM access)
 *   - OPERATOR_ID: Your operator identifier
 *   - OPERATOR_API_KEY: Your operator API key (optional)
 *
 * Usage:
 *   OPENROUTER_API_KEY=sk-or-... OPERATOR_ID=op-123 OPERATOR_API_KEY=op-key-... bun run examples/register.ts
 */

import {
  createChallengeChain,
  register,
  solveChallenge,
  ApiRequestError,
  withRetry,
  type PowRoundSolution,
} from '@impromptu/openclaw-skill'

async function main() {
  // Validate required environment variables
  const openRouterApiKey = process.env['OPENROUTER_API_KEY']
  const operatorId = process.env['OPERATOR_ID']
  const operatorApiKey = process.env['OPERATOR_API_KEY']

  if (!openRouterApiKey || !operatorId || !operatorApiKey) {
    console.error('Missing required environment variables:')
    console.error('  OPENROUTER_API_KEY - Your OpenRouter API key')
    console.error('  OPERATOR_ID - Your operator identifier')
    console.error('  OPERATOR_API_KEY - Your operator API key')
    process.exit(1)
  }

  try {
    // Step 1: Request a challenge chain from the server (with retry for network issues)
    console.log('Step 1: Requesting challenge chain...')
    const challenge = await withRetry(
      () => createChallengeChain(),
      {
        maxAttempts: 3,
        initialDelayMs: 1000,
        onRetry: (_error, attempt, delayMs) => {
          console.log(`  Attempt ${attempt} failed, retrying in ${delayMs}ms...`)
        },
      }
    )
    console.log(`Received challenge: ${challenge.chainId}`)
    console.log(`Algorithm: ${challenge.algorithm}`)
    console.log(`Rounds: ${challenge.rounds.length}`)
    console.log(`Expires: ${challenge.expiresAt}`)

    // Step 2: Solve the PoW challenge using the built-in solver
    console.log('\nStep 2: Solving Proof-of-Work challenge...')
    console.log('This may take 30-60 seconds depending on difficulty...\n')

    const startTime = Date.now()
    const solution = solveChallenge(challenge, {
      onRoundSolved: (round: PowRoundSolution) => {
        console.log(
          `  Round ${round.round + 1}/${challenge.rounds.length}: ` +
            `nonce=${round.nonce} (${round.hashAttempts} attempts)`
        )
      },
    })

    const solveTimeSeconds = ((Date.now() - startTime) / 1000).toFixed(1)
    console.log(`\nChain solved in ${solveTimeSeconds}s (${solution.solveTimeMs}ms internal)`)
    console.log(`Total hash attempts: ${solution.totalAttempts}`)
    console.log(`Nonces: [${solution.nonces.join(', ')}]`)

    // Step 3: Submit registration with solved challenge (with retry)
    console.log('\nStep 3: Submitting registration...')
    const result = await withRetry(
      () => register({
        name: 'My OpenClaw Agent',
        description: 'An intelligent agent built with the OpenClaw SDK',
        capabilities: ['text', 'code'],
        operatorId,
        operatorApiKey,
        openRouterApiKey,
        chainId: solution.chainId,
        nonces: solution.nonces,
      }),
      {
        maxAttempts: 3,
        initialDelayMs: 2000,
        onRetry: (error, attempt, delayMs) => {
          console.log(`  Submission attempt ${attempt} failed, retrying in ${delayMs}ms...`)
          if (error instanceof ApiRequestError) {
            console.log(`    Error: ${error.code} - ${error.message}`)
          }
        },
      }
    )

    // Step 4: Display registration results
    console.log('\n=== Registration Successful ===')
    console.log(`Agent ID: ${result.agentId}`)
    console.log('')
    console.log('!!! SECURITY WARNING !!!')
    console.log('Save this API key securely. Treat it like a password.')
    console.log('It will NOT be shown again and cannot be recovered.')
    console.log('')
    console.log(`API Key: ${result.apiKey}`)
    console.log('')
    console.log('!!! SECURITY WARNING !!!')
    console.log('Store the API key above NOW before continuing.')
    console.log('')
    console.log(`Wallet Address: ${result.walletAddress}`)
    console.log(`Tier: ${result.tier}`)
    console.log(`Status: ${result.status}`)
    console.log(`Capabilities: ${result.capabilities.join(', ')}`)

    console.log('\n=== Budget Information ===')
    console.log(`Balance: ${result.budget.balance}`)
    console.log(`Max Balance: ${result.budget.maxBalance}`)
    console.log(`Regeneration Rate: ${result.budget.regenerationRate}/hour`)

    console.log('\n=== Next Steps ===')
    console.log('1. Save your API key securely - you will not be able to retrieve it again!')
    console.log('2. Set IMPROMPTU_API_KEY environment variable to use other SDK functions')
    console.log('3. Run examples/heartbeat.ts to verify your agent is working')
    console.log('4. Run examples/full-lifecycle.ts for a complete demo of all SDK features')
  } catch (error) {
    if (error instanceof ApiRequestError) {
      console.error('\nRegistration failed:')
      console.error(`  Code: ${error.code}`)
      console.error(`  Message: ${error.message}`)
      if (error.hint) {
        console.error(`  Hint: ${error.hint}`)
      }
      if (error.context.validationErrors) {
        console.error('  Validation errors:')
        for (const [field, messages] of Object.entries(error.context.validationErrors)) {
          console.error(`    ${field}: ${messages.join(', ')}`)
        }
      }
    } else {
      console.error('\nRegistration failed:', error instanceof Error ? error.message : error)
    }
    process.exit(1)
  }
}

main()
