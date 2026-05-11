#!/usr/bin/env node

/**
 * zepto-ops.js - Zepto Operations Library
 * 
 * Atomic operations with built-in verification and retry logic.
 * Uses OpenClaw browser tool API directly (no CLI spawning).
 * 
 * All operations follow the pattern:
 * 1. Pre-flight check (verify current state)
 * 2. Execute action
 * 3. Verify result (retry if failed)
 * 4. Return structured result
 */

const { spawnSync } = require('child_process');
const path = require('path');

// ==================== CONFIG ====================
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;
const PARSER_PATH = path.join(__dirname, 'zepto-parser.js');

// ==================== UTILITIES ====================

/**
 * Sleep utility
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Parse snapshot with zepto-parser.js
 */
function parseWithParser(snapshot, command, ...args) {
  const proc = spawnSync('node', [PARSER_PATH, command, ...args], {
    input: snapshot,
    encoding: 'utf8',
    timeout: 5000
  });

  if (proc.status !== 0) {
    throw new Error(`Parser failed: ${proc.stderr || proc.error}`);
  }

  const output = proc.stdout.trim();
  try {
    return JSON.parse(output);
  } catch (e) {
    // Some commands return plain text
    return output;
  }
}

// ==================== BROWSER HELPERS ====================

/**
 * Get snapshot from browser
 */
async function snapshot(browserTool, targetId, limitNodes = 600) {
  const result = await browserTool({
    action: 'snapshot',
    targetId,
    interactive: true,
    limit: limitNodes
  });
  
  if (!result.snapshot && !result.aria) {
    throw new Error('No snapshot data received');
  }
  
  return result.snapshot || result.aria || '';
}

/**
 * Click a ref
 */
async function click(browserTool, targetId, ref, delayMs = 500) {
  await browserTool({
    action: 'act',
    targetId,
    request: { kind: 'click', ref }
  });
  await sleep(delayMs);
}

/**
 * Type text into a ref
 */
async function type(browserTool, targetId, ref, text, delayMs = 500) {
  await browserTool({
    action: 'act',
    targetId,
    request: { kind: 'type', ref, text }
  });
  await sleep(delayMs);
}

// ==================== PARSERS ====================

/**
 * Parse refs (search, cart, checkout buttons)
 */
function parseRefs(snapshot) {
  return parseWithParser(snapshot, 'refs');
}

/**
 * Parse cart (total, checkout ref)
 */
function parseCart(snapshot) {
  return parseWithParser(snapshot, 'cart');
}

/**
 * Parse product search result
 */
function parseProduct(snapshot, query) {
  const result = parseWithParser(snapshot, 'product', query);
  return result && result.name ? result : null;
}

/**
 * Extract remove button refs from cart snapshot
 */
function extractRemoveRefs(snapshot) {
  const lines = snapshot.split('\n');
  const removeRefs = [];
  
  for (const line of lines) {
    // Match: button "Remove" [ref=eXX]
    if (line.includes('button "Remove"') && line.includes('[ref=')) {
      const match = line.match(/\[ref=(e\d+)\]/);
      if (match && !removeRefs.includes(match[1])) {
        removeRefs.push(match[1]);
      }
    }
  }
  
  return removeRefs;
}

/**
 * Count items in cart (count "Remove" buttons)
 */
function countCartItems(snapshot) {
  return extractRemoveRefs(snapshot).length;
}

// ==================== CORE OPERATIONS ====================

/**
 * Get current cart state
 * Returns: { items: number, total: number, checkout_ref: string|null, raw_snapshot: string }
 */
async function getCartState(browserTool, targetId) {
  // Get homepage to find cart button
  const homeSnap = await snapshot(browserTool, targetId, 200);
  const refs = parseRefs(homeSnap);
  
  if (!refs.cart) {
    throw new Error('Cart button not found on homepage');
  }

  // Click cart
  await click(browserTool, targetId, refs.cart, 1500);

  // Get cart snapshot
  const cartSnap = await snapshot(browserTool, targetId, 600);
  
  // Parse cart
  const parsed = parseCart(cartSnap);
  const itemCount = countCartItems(cartSnap);

  return {
    items: itemCount,
    total: parsed.total || 0,
    checkout_ref: parsed.checkout || null,
    raw_snapshot: cartSnap
  };
}

/**
 * Clear cart completely (with verification)
 * Returns: { status: 'empty'|'cleared'|'failed', items_removed: number, attempts: number }
 */
async function clearCart(browserTool, targetId) {
  // Pre-flight: check current state
  let state = await getCartState(browserTool, targetId);
  
  if (state.items === 0) {
    return { status: 'empty', items_removed: 0, attempts: 0 };
  }

  const initialItems = state.items;
  let attempts = 0;

  while (attempts < MAX_RETRIES) {
    attempts++;

    // Extract remove refs
    const removeRefs = extractRemoveRefs(state.raw_snapshot);
    
    if (removeRefs.length === 0) {
      // No remove buttons but items exist - cart might be in weird state
      await sleep(RETRY_DELAY_MS);
      state = await getCartState(browserTool, targetId);
      continue;
    }

    // Click all remove buttons
    for (const ref of removeRefs) {
      await click(browserTool, targetId, ref, 300);
    }

    // Wait for UI to update
    await sleep(1000);

    // Verify cart is empty
    state = await getCartState(browserTool, targetId);
    
    if (state.items === 0) {
      return {
        status: 'cleared',
        items_removed: initialItems,
        attempts
      };
    }

    // Still has items, retry
    if (attempts < MAX_RETRIES) {
      await sleep(RETRY_DELAY_MS);
    }
  }

  // Failed after max retries
  return {
    status: 'failed',
    items_removed: initialItems - state.items,
    items_remaining: state.items,
    attempts
  };
}

/**
 * Search for a product
 * Returns: { name: string, price: number, ref: string, score: number } | null
 */
async function searchProduct(browserTool, targetId, query) {
  // Get search button ref
  const homeSnap = await snapshot(browserTool, targetId, 200);
  const refs = parseRefs(homeSnap);
  
  if (!refs.search) {
    throw new Error('Search button not found');
  }

  // Click search
  await click(browserTool, targetId, refs.search, 500);

  // Type query
  await type(browserTool, targetId, refs.search, query, 1500);

  // Get search results
  const resultsSnap = await snapshot(browserTool, targetId, 1200);
  
  // Parse product
  const product = parseProduct(resultsSnap, query);
  
  return product; // { name, price, ref, score } or null
}

/**
 * Add item to cart
 * Returns: { status: 'added'|'not_found'|'failed', product: object, in_cart: boolean, attempts: number }
 */
async function addItem(browserTool, targetId, query) {
  let attempts = 0;

  while (attempts < MAX_RETRIES) {
    attempts++;

    try {
      // Search for product
      const product = await searchProduct(browserTool, targetId, query);
      
      if (!product) {
        return {
          status: 'not_found',
          query,
          product: null,
          in_cart: false,
          attempts
        };
      }

      // Calculate ADD button ref (usually product ref + 1)
      const refNum = parseInt(product.ref.replace('e', ''));
      const addRef = `e${refNum + 1}`;

      // Click ADD
      await click(browserTool, targetId, addRef, 1000);

      // Verify item was added to cart
      const cartState = await getCartState(browserTool, targetId);
      
      // Check if cart increased
      if (cartState.items > 0) {
        return {
          status: 'added',
          product: { name: product.name, price: product.price },
          in_cart: true,
          attempts
        };
      }

      // Cart didn't increase, retry
      if (attempts < MAX_RETRIES) {
        await sleep(RETRY_DELAY_MS);
      }

    } catch (err) {
      if (attempts >= MAX_RETRIES) {
        return {
          status: 'failed',
          query,
          error: err.message,
          in_cart: false,
          attempts
        };
      }
      await sleep(RETRY_DELAY_MS);
    }
  }

  return {
    status: 'failed',
    query,
    error: 'Max retries exceeded',
    in_cart: false,
    attempts
  };
}

/**
 * Shop for multiple items
 * Returns: { added: array, failed: array, cart_total: number }
 */
async function shop(browserTool, targetId, items) {
  // Pre-flight: verify cart is empty
  const preState = await getCartState(browserTool, targetId);
  if (preState.items > 0) {
    throw new Error(`Cart not empty: ${preState.items} items (total: ₹${preState.total}). Clear first!`);
  }

  const added = [];
  const failed = [];

  for (const item of items) {
    const result = await addItem(browserTool, targetId, item);
    
    if (result.status === 'added') {
      added.push({ ...result.product, query: item });
    } else {
      failed.push({ query: item, reason: result.status, error: result.error });
    }

    // Small delay between items
    await sleep(500);
  }

  // Get final cart state
  const finalState = await getCartState(browserTool, targetId);

  return {
    added,
    failed,
    cart_total: finalState.total,
    cart_items: finalState.items
  };
}

// ==================== EXPORTS ====================

module.exports = {
  // Core operations
  getCartState,
  clearCart,
  searchProduct,
  addItem,
  shop,
  
  // Helpers (for advanced usage)
  snapshot,
  click,
  type,
  parseRefs,
  parseCart,
  parseProduct,
  extractRemoveRefs,
  countCartItems
};
