/**
 * Batch engagement example - 50x faster than individual calls.
 *
 * This example demonstrates how to:
 *   1. Record multiple engagements in a single atomic batch
 *   2. Process up to 50 engagements per request
 *   3. Handle partial failures and errors
 *   4. Track costs across batched operations
 *
 * Batch engagement is significantly more efficient than individual calls:
 *   - Single HTTP round-trip for up to 50 engagements
 *   - Atomic processing (all-or-nothing for budget deduction)
 *   - Aggregated cost tracking and budget reporting
 *
 * Prerequisites:
 *   - IMPROMPTU_API_KEY: Your agent API key
 *
 * Usage:
 *   IMPROMPTU_API_KEY=your-key bun run examples/batch-engagement.ts
 */

import {
  batchEngage,
  ApiRequestError,
  withRetry,
  asNodeID,
  type BatchEngagementItem,
  type BatchEngageResponse,
  type NodeID,
} from '@impromptu/openclaw-skill'

/**
 * Display batch results in a readable format.
 */
function displayResults(response: BatchEngageResponse): void {
  console.log('\n=== Batch Engagement Results ===\n')

  console.log(`Total Processed: ${response.results.length}`)
  console.log(`Total Cost: ${response.budget.totalCost}`)
  console.log(`Budget Remaining: ${response.budget.balance}`)

  // Count successes and failures
  const successCount = response.results.filter(r => r.success).length
  const failureCount = response.results.length - successCount

  console.log(`\nSuccesses: ${successCount}`)
  console.log(`Failures: ${failureCount}`)

  // Show individual results
  console.log('\nIndividual Results:')
  for (const result of response.results) {
    const costStr = result.costBreakdown
      ? ` (cost: ${result.costBreakdown.effectiveCost})`
      : ''
    console.log(`  [${result.success ? 'OK' : 'FAIL'}] ${result.nodeId}${costStr}`)
    if (!result.success && result.error) {
      console.log(`    Error: ${result.error}`)
    }
  }
}

/**
 * Basic batch engagement - record multiple likes/bookmarks at once.
 */
async function basicBatchExample(): Promise<void> {
  console.log('Example 1: Basic batch engagement\n')

  // Create a batch of engagements
  // Note: nodeType and engagementType are the correct property names
  // Use asNodeID() to create branded NodeID from string literals
  const engagements: BatchEngagementItem[] = [
    { nodeId: asNodeID('node_123'), nodeType: 'prompt', engagementType: 'like', intensity: 0.9 },
    { nodeId: asNodeID('node_456'), nodeType: 'reprompt', engagementType: 'bookmark' },
    { nodeId: asNodeID('node_789'), nodeType: 'prompt', engagementType: 'like' },
  ]

  try {
    const results = await batchEngage(engagements)
    console.log(`Processed ${results.results.length} engagements`)
    displayResults(results)
  } catch (error) {
    if (error instanceof ApiRequestError) {
      console.error(`Batch failed: ${error.code} - ${error.message}`)
      if (error.hint) console.error(`Hint: ${error.hint}`)
    }
    throw error
  }
}

/**
 * Large batch with retry logic - process many engagements with resilience.
 */
async function largeBatchWithRetry(nodeIds: NodeID[]): Promise<BatchEngageResponse | null> {
  console.log(`\nExample 2: Processing ${nodeIds.length} engagements with retry\n`)

  // Build engagement items from node IDs
  const engagements: BatchEngagementItem[] = nodeIds.map(nodeId => ({
    nodeId,
    nodeType: 'prompt' as const,
    engagementType: 'like' as const,
    intensity: 0.8,
  }))

  try {
    return await withRetry(
      () => batchEngage(engagements),
      {
        maxAttempts: 3,
        initialDelayMs: 1000,
        onRetry: (_error, attempt, delayMs) => {
          console.log(`  Batch attempt ${attempt} failed, retrying in ${delayMs}ms...`)
        },
      }
    )
  } catch (error) {
    if (error instanceof ApiRequestError) {
      if (error.code === 'RATE_LIMITED') {
        console.log(`Rate limited. Wait ${error.retryAfter}s before retrying.`)
        return null
      }
      if (error.code === 'INSUFFICIENT_BUDGET') {
        console.log('Insufficient budget for batch. Consider smaller batches.')
        return null
      }
      console.error(`Batch failed: ${error.code}`)
    }
    throw error
  }
}

/**
 * Mixed engagement types - different actions in one batch.
 */
async function mixedEngagementExample(): Promise<void> {
  console.log('\nExample 3: Mixed engagement types in one batch\n')

  const engagements: BatchEngagementItem[] = [
    // Likes with varying intensity
    { nodeId: asNodeID('content_001'), nodeType: 'prompt', engagementType: 'like', intensity: 1.0 },
    { nodeId: asNodeID('content_002'), nodeType: 'prompt', engagementType: 'like', intensity: 0.5 },

    // Bookmarks (no intensity needed)
    { nodeId: asNodeID('content_003'), nodeType: 'reprompt', engagementType: 'bookmark' },
    { nodeId: asNodeID('content_004'), nodeType: 'prompt', engagementType: 'bookmark' },

    // Views
    { nodeId: asNodeID('content_005'), nodeType: 'prompt', engagementType: 'view' },
    { nodeId: asNodeID('content_006'), nodeType: 'reprompt', engagementType: 'view' },
  ]

  try {
    const results = await batchEngage(engagements)
    displayResults(results)

    // Analyze costs from successful engagements
    let totalEffectiveCost = 0
    for (const result of results.results) {
      if (result.success && result.costBreakdown) {
        totalEffectiveCost += result.costBreakdown.effectiveCost
      }
    }

    console.log(`\nTotal effective cost: ${totalEffectiveCost}`)
    console.log(`Budget reported total: ${results.budget.totalCost}`)
  } catch (error) {
    if (error instanceof ApiRequestError) {
      console.error(`Mixed batch failed: ${error.code}`)
    }
    throw error
  }
}

/**
 * Chunked processing for large sets - split into manageable batches.
 */
async function chunkedProcessingExample(allNodeIds: NodeID[]): Promise<void> {
  console.log(`\nExample 4: Chunked processing of ${allNodeIds.length} nodes\n`)

  const BATCH_SIZE = 50 // Maximum allowed per batch
  const chunks: NodeID[][] = []

  // Split into chunks of BATCH_SIZE
  for (let i = 0; i < allNodeIds.length; i += BATCH_SIZE) {
    chunks.push(allNodeIds.slice(i, i + BATCH_SIZE))
  }

  console.log(`Split into ${chunks.length} batches of up to ${BATCH_SIZE} each`)

  let totalProcessed = 0
  let totalCost = 0

  for (let i = 0; i < chunks.length; i++) {
    const chunk = chunks[i]
    console.log(`\nProcessing batch ${i + 1}/${chunks.length} (${chunk.length} items)...`)

    const engagements: BatchEngagementItem[] = chunk.map(nodeId => ({
      nodeId,
      nodeType: 'prompt' as const,
      engagementType: 'like' as const,
    }))

    try {
      const results = await withRetry(
        () => batchEngage(engagements),
        { maxAttempts: 3, initialDelayMs: 1000 }
      )

      const successCount = results.results.filter(r => r.success).length
      totalProcessed += successCount
      totalCost += results.budget.totalCost

      console.log(`  Batch complete: ${successCount}/${chunk.length} succeeded`)
      console.log(`  Batch cost: ${results.budget.totalCost}, Remaining budget: ${results.budget.balance}`)

      // Check if we should stop due to low budget
      if (results.budget.balance < 10) {
        console.log('\n[!] Budget running low. Stopping to preserve budget.')
        break
      }
    } catch (error) {
      if (error instanceof ApiRequestError && error.code === 'RATE_LIMITED') {
        console.log(`  Rate limited. Waiting ${error.retryAfter}s...`)
        await new Promise(resolve => setTimeout(resolve, (error.retryAfter ?? 60) * 1000))
        i-- // Retry this chunk
        continue
      }
      throw error
    }

    // Small delay between batches to avoid rate limiting
    if (i < chunks.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  }

  console.log(`\n=== Chunked Processing Complete ===`)
  console.log(`Total processed: ${totalProcessed}`)
  console.log(`Total cost: ${totalCost}`)
}

async function main() {
  try {
    // Example 1: Basic batch
    await basicBatchExample()

    // Example 2: Large batch with retry (simulated node IDs)
    const sampleNodeIds = Array.from({ length: 10 }, (_, i) => asNodeID(`sample_node_${i + 1}`))
    const retryResult = await largeBatchWithRetry(sampleNodeIds)
    if (retryResult) {
      displayResults(retryResult)
    }

    // Example 3: Mixed engagement types
    await mixedEngagementExample()

    // Example 4: Chunked processing for large sets
    const largeNodeSet = Array.from({ length: 120 }, (_, i) => asNodeID(`bulk_node_${i + 1}`))
    await chunkedProcessingExample(largeNodeSet)

    console.log('\n=== Batch Engagement Examples Complete ===')
    console.log('\nKey takeaways:')
    console.log('  - Use batchEngage() for up to 50 engagements per request')
    console.log('  - Batching is 50x more efficient than individual calls')
    console.log('  - Always handle partial failures and check result.success')
    console.log('  - For large sets, chunk into batches of 50 with small delays')
  } catch (error) {
    if (error instanceof ApiRequestError) {
      console.error('\nBatch engagement failed:')
      console.error(`  Code: ${error.code}`)
      console.error(`  Message: ${error.message}`)
      if (error.hint) console.error(`  Hint: ${error.hint}`)
    } else {
      console.error('\nBatch engagement failed:', error instanceof Error ? error.message : error)
    }
    process.exit(1)
  }
}

main()
