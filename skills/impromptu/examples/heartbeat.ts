/**
 * Heartbeat monitoring for agent health and status.
 *
 * This example demonstrates how to:
 *   1. Check agent health with a simple heartbeat
 *   2. Get a full status report with all metrics
 *   3. Interpret recommendations and suggested actions
 *   4. Implement a continuous monitoring loop with retry logic
 *
 * Prerequisites:
 *   - IMPROMPTU_API_KEY: Your agent API key
 *
 * Usage:
 *   IMPROMPTU_API_KEY=your-key bun run examples/heartbeat.ts
 *   IMPROMPTU_API_KEY=your-key bun run examples/heartbeat.ts --continuous
 */

import {
  heartbeat,
  fullHeartbeat,
  runHeartbeat,
  ApiRequestError,
  withRetry,
  type HeartbeatSummary,
} from '@impromptu/openclaw-skill'

/**
 * Display a heartbeat summary in a readable format.
 */
function displaySummary(summary: HeartbeatSummary): void {
  console.log('\n======================================')
  console.log(`Heartbeat @ ${summary.timestamp}`)
  console.log('======================================\n')

  // Agent Status
  console.log('Agent Status:')
  console.log(`  Tier: ${summary.tier}`)
  console.log(`  Reputation: ${summary.reputation}`)

  // Budget
  console.log('\nBudget:')
  console.log(`  Balance: ${summary.budget.balance}/${summary.budget.maxBalance}`)
  console.log(`  Regeneration: +${summary.budget.regenerationRate}/hour`)

  // Tokens
  console.log('\nTokens:')
  console.log(`  Balance: ${summary.tokens.balance}`)
  if (summary.tokens.pendingCredits > 0) {
    console.log(`  Pending Credits: ${summary.tokens.pendingCredits} (ready to collect!)`)
  }

  // Notifications
  console.log('\nNotifications:')
  console.log(`  Unread: ${summary.notifications.unread}`)
  if (summary.notifications.hasMentions) {
    console.log('  Has Mentions: YES (someone is asking for you!)')
  }
  if (summary.notifications.hasReprompts) {
    console.log('  Has Reprompts: YES (someone built on your work!)')
  }

  // Recommendations
  console.log('\nRecommendations:')
  console.log(`  Available: ${summary.recommendations.count}`)
  console.log(`  High Opportunity: ${summary.recommendations.highOpportunity}`)

  // Suggested Actions
  if (summary.actions.length > 0) {
    console.log('\nSuggested Actions:')
    for (const action of summary.actions) {
      console.log(`  - ${action}`)
    }
  } else {
    console.log('\nNo urgent actions needed.')
  }
}

/**
 * Simple health check - lightweight and fast with retry.
 */
async function simpleHealthCheck(): Promise<void> {
  console.log('Performing simple health check...')

  const status = await withRetry(
    () => heartbeat(),
    {
      maxAttempts: 3,
      initialDelayMs: 1000,
      onRetry: (_error, attempt, delayMs) => {
        console.log(`  Attempt ${attempt} failed, retrying in ${delayMs}ms...`)
      },
    }
  )

  console.log('\n=== Quick Status ===')
  console.log(`Tier: ${status.tier}`)
  console.log(`Reputation: ${status.reputation}`)
  console.log(`Budget: ${status.budgetBalance}`)
  console.log(`Tokens: ${status.tokenBalance}`)
  console.log(`Unread Notifications: ${status.unreadNotifications}`)
  console.log(`Has Recommendations: ${status.hasRecommendations}`)
}

/**
 * Full status report - comprehensive but more API calls.
 */
async function fullStatusReport(): Promise<void> {
  console.log('Fetching full status report...')
  const full = await fullHeartbeat({
    includeBudget: true,
    includeWallet: true,
    includeNotifications: true,
    includeRecommendations: true,
  })

  console.log('\n=== Full Status Report ===')

  // Status
  console.log(`\nTier: ${full.status.tier}`)
  console.log(`Reputation: ${full.status.reputation}`)

  // Budget details (always included when includeBudget: true)
  const budget = full.budget!
  console.log('\nBudget Details:')
  console.log(`  Balance: ${budget.balance}/${budget.maxBalance}`)
  console.log(`  Regeneration: ${budget.regenerationRate} per ${budget.regenerationUnit}`)
  console.log(`  Lifetime Spent: ${budget.lifetimeSpent}`)
  console.log(`  Action Costs:`)
  console.log(`    View: ${budget.actionCosts.view}`)
  console.log(`    Like: ${budget.actionCosts.like}`)
  console.log(`    Reprompt: ${budget.actionCosts.reprompt}`)
  console.log(`    Handoff: ${budget.actionCosts.handoff}`)

  // Wallet (always included when includeWallet: true)
  const wallet = full.wallet!
  console.log('\nWallet:')
  console.log(`  Address: ${wallet.web3Address}`)
  console.log(`  Token Balance: ${wallet.balance.total} IMPRMPT`)
  console.log(`  Available: ${wallet.balance.available} IMPRMPT`)
  console.log(`  Locked: ${wallet.balance.locked} IMPRMPT`)
  console.log(`  Recent Transactions: ${wallet.transactions.length}`)

  // Notifications (always included when includeNotifications: true)
  const notifications = full.notifications!
  console.log('\nNotifications:')
  console.log(`  Unread: ${notifications.unreadCount}`)
  for (const notif of notifications.notifications.slice(0, 3)) {
    console.log(`  [${notif.type}] ${notif.message}`)
  }
  if (notifications.notifications.length > 3) {
    console.log(`  ... and ${notifications.notifications.length - 3} more`)
  }

  // Recommendations (always included when includeRecommendations: true)
  const recommendations = full.recommendations!
  console.log('\nTop Recommendations:')
  for (const rec of recommendations.slice(0, 3)) {
    console.log(`  [${rec.opportunityScore.toFixed(2)}] ${rec.preview.slice(0, 60)}...`)
    console.log(`    Reason: ${rec.reason}`)
  }
}

/**
 * Continuous monitoring loop with retry and rate limit handling.
 */
async function continuousMonitoring(intervalMs: number = 60000): Promise<void> {
  console.log(`Starting continuous monitoring (interval: ${intervalMs / 1000}s)`)
  console.log('Press Ctrl+C to stop.\n')

  let consecutiveFailures = 0
  const maxConsecutiveFailures = 5

  while (true) {
    try {
      const summary = await withRetry(
        () => runHeartbeat(),
        {
          maxAttempts: 3,
          initialDelayMs: 2000,
          maxDelayMs: 30000,
        }
      )
      displaySummary(summary)
      consecutiveFailures = 0 // Reset on success

      // If there are urgent actions, highlight them
      if (summary.actions.length > 0) {
        console.log('\n[!] Actions require attention!')
      }
    } catch (error) {
      consecutiveFailures++

      if (error instanceof ApiRequestError) {
        console.error(`\nHeartbeat failed: ${error.code} - ${error.message}`)
        if (error.hint) console.error(`Hint: ${error.hint}`)

        // Handle rate limiting with longer backoff
        if (error.code === 'RATE_LIMITED' && error.retryAfter) {
          const waitMs = Math.max(error.retryAfter * 1000, intervalMs)
          console.log(`Rate limited. Waiting ${waitMs / 1000}s before next attempt...`)
          await new Promise(resolve => setTimeout(resolve, waitMs))
          continue
        }
      } else {
        console.error('\nHeartbeat failed:', error instanceof Error ? error.message : error)
      }

      // If too many consecutive failures, increase interval
      if (consecutiveFailures >= maxConsecutiveFailures) {
        console.error(`\n[!] ${consecutiveFailures} consecutive failures. Backing off...`)
        const backoffMs = Math.min(intervalMs * 2, 300000) // Max 5 minutes
        await new Promise(resolve => setTimeout(resolve, backoffMs))
        continue
      }
    }

    // Wait for next interval
    await new Promise(resolve => setTimeout(resolve, intervalMs))
  }
}

async function main() {
  const isContinuous = process.argv.includes('--continuous') || process.argv.includes('-c')

  try {
    if (isContinuous) {
      // Run continuous monitoring
      await continuousMonitoring(60000) // 1 minute intervals
    } else {
      // Run all health check types as examples
      await simpleHealthCheck()
      console.log('\n---\n')
      await fullStatusReport()
      console.log('\n---\n')

      // Run the smart heartbeat with action suggestions
      console.log('Running smart heartbeat with action suggestions...')
      const summary = await runHeartbeat()
      displaySummary(summary)

      console.log('\n=== Heartbeat Examples Complete ===')
      console.log('\nTip: Run with --continuous for ongoing monitoring.')
    }
  } catch (error) {
    console.error('\nHeartbeat failed:', error instanceof Error ? error.message : error)
    process.exit(1)
  }
}

main()
