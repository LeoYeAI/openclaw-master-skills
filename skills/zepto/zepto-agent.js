#!/usr/bin/env node

/**
 * Zepto Agent - Autonomous Task Executor
 * 
 * Not a parser. An agent that DOES things.
 * Takes commands, executes them, verifies results.
 * 
 * Usage:
 *   node zepto-agent.js clear-cart [--verify]
 *   node zepto-agent.js add-item "milk" [--confirm]
 *   node zepto-agent.js get-cart
 *   node zepto-agent.js shop "milk, bread, honey"
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// ==================== CONFIG ====================
const BROWSER_PROFILE = 'openclaw';
const ZEPTO_URL = 'https://www.zepto.com';
const MAX_RETRIES = 3;
const SNAPSHOT_DELAY_MS = 1500;

// ==================== UTILITIES ====================

/**
 * Run OpenClaw browser command and return parsed result
 */
async function browserCmd(action, params = {}) {
  return new Promise((resolve, reject) => {
    const args = ['browser', '--profile', BROWSER_PROFILE];
    
    // Handle positional arguments
    if (action === 'open' && params.url) {
      args.push(action, params.url);
      delete params.url;
    } else if (action === 'click' && params.ref) {
      args.push(action, params.ref);
      delete params.ref;
    } else if (action === 'evaluate' && params.fn) {
      args.push(action);
      args.push('--fn', params.fn);
      delete params.fn;
    } else {
      args.push(action);
    }
    
    // Add remaining parameters  
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null) {
        // Boolean flags: just add the flag if true, skip if false
        if (typeof val === 'boolean') {
          if (val === true) {
            args.push(`--${key}`);
          }
        } else {
          args.push(`--${key}`, String(val));
        }
      }
    });

    const proc = spawn('openclaw', args, { stdio: ['pipe', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => { stdout += data; });
    proc.stderr.on('data', (data) => { stderr += data; });

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Browser command failed: ${stderr}`));
      } else {
        try {
          resolve(JSON.parse(stdout));
        } catch (e) {
          resolve({ raw: stdout });
        }
      }
    });
  });
}

/**
 * Get snapshot and parse with zepto-parser.js
 */
async function getSnapshot(command = 'refs', maxLimit = 500) {
  // Get browser snapshot - using AI format with interactive flag
  const snap = await browserCmd('snapshot', { 
    interactive: true,
    limit: maxLimit 
  });

  // DEBUG: Log what we got
  console.error('DEBUG snap keys:', Object.keys(snap));
  console.error('DEBUG snap:', JSON.stringify(snap).substring(0, 200));

  // New format: snap has { interactive: [...] } directly
  if (!snap.interactive && !snap.snapshot && !snap.aria) {
    throw new Error(`No snapshot data received. Got keys: ${Object.keys(snap).join(', ')}`);
  }

  // If we have interactive array, return it with raw text version
  if (snap.interactive) {
    const snapshotText = JSON.stringify(snap.interactive, null, 2);
    
    // Parse with zepto-parser.js
    return new Promise((resolve, reject) => {
      const parserPath = path.join(__dirname, 'zepto-parser.js');
      const proc = spawn('node', [parserPath, command], { stdio: ['pipe', 'pipe', 'pipe'] });
      
      let stdout = '';
      let stderr = '';

      proc.stdin.write(snapshotText);
      proc.stdin.end();

      proc.stdout.on('data', (data) => { stdout += data; });
      proc.stderr.on('data', (data) => { stderr += data; });

      proc.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Parser failed: ${stderr}`));
        } else {
          try {
            resolve({ 
              raw: snapshotText, 
              parsed: JSON.parse(stdout),
              interactive: snap.interactive 
            });
          } catch (e) {
            resolve({ 
              raw: snapshotText, 
              parsed: stdout.trim(),
              interactive: snap.interactive 
            });
          }
        }
      });
    });
  }

  // Fallback to old format
  const snapshotText = snap.snapshot || snap.aria || '';

  // Parse with zepto-parser.js
  return new Promise((resolve, reject) => {
    const parserPath = path.join(__dirname, 'zepto-parser.js');
    const proc = spawn('node', [parserPath, command], { stdio: ['pipe', 'pipe', 'pipe'] });
    
    let stdout = '';
    let stderr = '';

    proc.stdin.write(snapshotText);
    proc.stdin.end();

    proc.stdout.on('data', (data) => { stdout += data; });
    proc.stderr.on('data', (data) => { stderr += data; });

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Parser failed: ${stderr}`));
      } else {
        try {
          resolve({ raw: snapshotText, parsed: JSON.parse(stdout) });
        } catch (e) {
          resolve({ raw: snapshotText, parsed: stdout.trim() });
        }
      }
    });
  });
}

/**
 * Click a ref and wait
 */
async function click(ref, delayMs = 500) {
  await browserCmd('act', { request: JSON.stringify({ kind: 'click', ref }) });
  await sleep(delayMs);
}

/**
 * Type text into a ref
 */
async function type(ref, text, delayMs = 500) {
  await browserCmd('act', { request: JSON.stringify({ kind: 'type', ref, text }) });
  await sleep(delayMs);
}

/**
 * Sleep utility
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Log with timestamp
 */
function log(msg, level = 'info') {
  const timestamp = new Date().toISOString();
  const prefix = level === 'error' ? '❌' : level === 'success' ? '✅' : 'ℹ️';
  console.error(`${prefix} [${timestamp}] ${msg}`);
}

// ==================== CORE OPERATIONS ====================

/**
 * Open Zepto homepage
 */
async function openZepto() {
  log('Opening Zepto...');
  await browserCmd('open', { url: ZEPTO_URL });
  await sleep(SNAPSHOT_DELAY_MS);
  log('Zepto opened', 'success');
}

/**
 * Get cart state (items, total, checkout ref)
 */
async function getCart() {
  log('Getting cart state...');
  
  // First get refs to find cart button
  const homepage = await getSnapshot('refs', 1000);
  const cartRef = homepage.parsed.cart;
  
  if (!cartRef) {
    throw new Error('Cart button not found on homepage');
  }

  // Click cart
  await click(cartRef, SNAPSHOT_DELAY_MS);

  // Get cart snapshot
  const cartSnap = await getSnapshot('cart', 3000);
  
  log(`Cart state: ${JSON.stringify(cartSnap.parsed)}`, 'success');
  return cartSnap;
}

/**
 * Clear cart completely (with verification)
 */
async function clearCart(options = {}) {
  const verify = options.verify !== false; // Default true
  
  log('Clearing cart...');
  
  let retries = 0;
  while (retries < MAX_RETRIES) {
    try {
      // Get current cart state
      const cartState = await getCart();
      
      // Check if already empty
      if (cartState.parsed.total === 0 || cartState.parsed.total === null) {
        log('Cart already empty', 'success');
        return { status: 'empty', items: 0 };
      }

      // Extract remove button refs from raw snapshot
      const removeRefs = extractRemoveRefs(cartState.raw);
      
      if (removeRefs.length === 0) {
        log('No remove buttons found, but cart not empty - retrying...', 'error');
        retries++;
        await sleep(1000);
        continue;
      }

      log(`Found ${removeRefs.length} items to remove`);

      // Click all remove buttons
      for (const ref of removeRefs) {
        log(`Removing item ${ref}...`);
        await click(ref, 300);
      }

      // Wait for removals to process
      await sleep(1000);

      // Verify if requested
      if (verify) {
        const verifyState = await getCart();
        if (verifyState.parsed.total === 0 || verifyState.parsed.total === null) {
          log('Cart cleared and verified empty', 'success');
          return { status: 'cleared', items: removeRefs.length };
        } else {
          log(`Verification failed: cart still has items (total: ₹${verifyState.parsed.total})`, 'error');
          retries++;
          continue;
        }
      } else {
        log('Cart cleared (not verified)', 'success');
        return { status: 'cleared', items: removeRefs.length, verified: false };
      }

    } catch (err) {
      log(`Clear cart attempt ${retries + 1} failed: ${err.message}`, 'error');
      retries++;
      if (retries >= MAX_RETRIES) throw err;
      await sleep(1000);
    }
  }

  throw new Error('Failed to clear cart after max retries');
}

/**
 * Extract remove button refs from cart snapshot
 */
function extractRemoveRefs(snapshotText) {
  const lines = snapshotText.split('\n');
  const removeRefs = [];
  
  for (const line of lines) {
    // Match: button "Remove" [ref=eXX]
    if (line.includes('button "Remove"') && line.includes('[ref=')) {
      const match = line.match(/\[ref=(e\d+)\]/);
      if (match) {
        removeRefs.push(match[1]);
      }
    }
  }
  
  return removeRefs;
}

/**
 * Check if item is already in cart by searching for it in results
 * Returns { inCart: boolean, productRef: string, addRef: string }
 */
async function checkItemInCart(query) {
  log(`Checking if "${query}" is already in cart...`);
  
  // Get search ref
  const homepage = await getSnapshot('refs', 1000);
  const searchRef = homepage.parsed.search;
  
  if (!searchRef) {
    throw new Error('Search button not found');
  }

  // Click search
  await click(searchRef, 500);

  // Type query
  await type(searchRef, query, 1500);

  // Get search results with full snapshot
  const results = await getSnapshot(`product ${query}`, 6000);
  
  if (!results.parsed || !results.parsed.ref) {
    throw new Error(`No product found for query: ${query}`);
  }

  const product = results.parsed;
  
  // Check if raw snapshot contains quantity controls for this product
  // Pattern: "Decrease quantity 1 Increase quantity" near the product ref
  const inCart = results.raw.includes('Decrease quantity') && 
                 results.raw.includes('Increase quantity');
  
  if (inCart) {
    log(`✓ "${product.name}" is ALREADY in cart`, 'success');
  } else {
    log(`✗ "${product.name}" is NOT in cart`);
  }

  const addRef = product.ref.replace(/e(\d+)/, (_, num) => `e${parseInt(num) + 1}`);

  return {
    inCart,
    product,
    productRef: product.ref,
    addRef
  };
}

/**
 * Search and add item (ONLY if not already in cart)
 */
async function addItem(query, options = {}) {
  const confirm = options.confirm !== false; // Default true
  const force = options.force === true; // Force add even if in cart
  
  log(`Adding item: "${query}"...`);

  // CRITICAL: Check if already in cart FIRST
  const check = await checkItemInCart(query);
  
  if (check.inCart && !force) {
    log(`SKIPPED: ${check.product.name} already in cart`, 'success');
    return { ...check.product, skipped: true, reason: 'already_in_cart' };
  }

  log(`Found: ${check.product.name} - ₹${check.product.price} [${check.productRef}]`);

  if (confirm) {
    // Click ADD button
    await click(check.addRef, 1000);
    log(`Added ${check.product.name}`, 'success');
  }

  return check.product;
}

/**
 * Get cart total
 */
async function getCartTotal() {
  const cartState = await getCart();
  console.log(JSON.stringify({
    total: cartState.parsed.total,
    checkout_ref: cartState.parsed.checkout
  }, null, 2));
  return cartState.parsed;
}

/**
 * Shop for multiple items (legacy - requires empty cart)
 */
async function shop(itemsStr, options = {}) {
  const items = itemsStr.split(',').map(s => s.trim());
  
  log(`Shopping for ${items.length} items: ${items.join(', ')}`);

  // Pre-flight: verify cart is empty
  const preCart = await getCart();
  if (preCart.parsed.total > 0) {
    log(`Cart not empty (₹${preCart.parsed.total}). Clear first!`, 'error');
    throw new Error('Cart must be empty before shopping');
  }

  const added = [];
  const failed = [];

  for (const item of items) {
    try {
      const product = await addItem(item, { confirm: true });
      added.push(product);
      await sleep(500);
    } catch (err) {
      log(`Failed to add ${item}: ${err.message}`, 'error');
      failed.push({ item, error: err.message });
    }
  }

  // Get final cart
  const finalCart = await getCart();

  log(`Shopping complete: ${added.length} added, ${failed.length} failed`, added.length === items.length ? 'success' : 'error');

  console.log(JSON.stringify({
    added: added.map(p => ({ name: p.name, price: p.price })),
    failed,
    cart_total: finalCart.parsed.total
  }, null, 2));

  return { added, failed, total: finalCart.parsed.total };
}

/**
 * Smart shop: Check cart first, remove unwanted, add missing
 */
async function smartShop(itemsStr, options = {}) {
  const targetItems = itemsStr.split(',').map(s => s.trim());
  const clearUnwanted = options.clearUnwanted !== false; // Default true
  
  log(`🧠 Smart shopping for: ${targetItems.join(', ')}`);

  // STEP 1: Check current cart state
  const cartState = await getCart();
  log(`Current cart total: ₹${cartState.parsed.total || 0}`);

  // STEP 2: If cart has items and clearUnwanted is true, clear it
  if (cartState.parsed.total > 0) {
    if (clearUnwanted) {
      log('Clearing existing cart items...');
      await clearCart({ verify: true });
    } else {
      log('Warning: Cart has existing items, will add on top');
    }
  }

  // STEP 3: Add items (with duplicate checking)
  const added = [];
  const skipped = [];
  const failed = [];

  for (const item of targetItems) {
    try {
      const result = await addItem(item, { confirm: true, force: false });
      
      if (result.skipped) {
        skipped.push(result);
      } else {
        added.push(result);
      }
      
      await sleep(500);
    } catch (err) {
      log(`Failed to add ${item}: ${err.message}`, 'error');
      failed.push({ item, error: err.message });
    }
  }

  // STEP 4: Get final cart state
  const finalCart = await getCart();

  log(`✅ Smart shop complete: ${added.length} added, ${skipped.length} skipped, ${failed.length} failed`, 'success');

  const result = {
    added: added.map(p => ({ name: p.name, price: p.price })),
    skipped: skipped.map(p => ({ name: p.name, reason: p.reason })),
    failed,
    cart_total: finalCart.parsed.total
  };

  console.log(JSON.stringify(result, null, 2));
  return result;
}

/**
 * Get list of available saved addresses
 * Returns array of address names
 */
/**
 * Get list of available saved addresses  
 * Opens modal using JavaScript and extracts address names
 */
async function getAvailableAddresses() {
  log('📋 Fetching available addresses...');
  
  // Step 1: Get current page snapshot  
  const snap = await browserCmd('snapshot', {});
  const snapshotText = snap.snapshot || snap.raw || JSON.stringify(snap);
  
  // Find address button in header
  const addrMatch = snapshotText.match(/button "([^"]*(?:blr|Home|Nagar)[^"]*)"\s*\[ref=(e\d+)\]/i);
  if (!addrMatch) {
    throw new Error('Address button not found in header');
  }
  
  const buttonRef = addrMatch[2];
  log(`Found address button: ${buttonRef}`);
  
  // Step 2: Click to open modal
  await browserCmd('click', { ref: buttonRef });
  await sleep(2000);
  
  // Step 3: Extract addresses using JavaScript
  const jsCode = `(() => {
    const input = document.querySelector('input[placeholder*="address"]');
    if (!input) return { error: 'Modal not found' };
    
    let modal = input;
    for (let i = 0; i < 15; i++) {
      if (!modal.parentElement) break;
      modal = modal.parentElement;
      if (window.getComputedStyle(modal).position === 'fixed') break;
    }
    
    // Find all divs in modal that look like address entries
    // Pattern: starts with capital letter + contains full address text
    const divs = Array.from(modal.querySelectorAll('div'));
    const addresses = [];
    const seen = new Set();
    
    for (const div of divs) {
      const text = div.textContent;
      if (!text) continue;
      
      // Look for patterns like "New HomeD-1001..." or "Sanskar BlrA-301..."
      const match = text.match(/^([A-Z][a-zA-Z\\s]+(?:Blr|Home|Nagar|Nivas))[A-Z\\d]/);
      if (match) {
        const name = match[1].trim();
        if (name.length > 3 && !seen.has(name.toLowerCase())) {
          addresses.push(name);
          seen.add(name.toLowerCase());
        }
      }
    }
    
    // Close modal
    document.dispatchEvent(new KeyboardEvent("keydown", { 
      key: "Escape", code: "Escape", keyCode: 27, bubbles: true 
    }));
    
    return { addresses };
  })()`;
  
  const result = await browserCmd('evaluate', { fn: jsCode });
  
  if (result.error || result.result?.error) {
    throw new Error(result.error || result.result.error);
  }
  
  const addresses = result.result?.addresses || result.addresses || [];
  
  if (addresses.length === 0) {
    throw new Error('No addresses found in modal');
  }
  
  log(`Found ${addresses.length} saved addresses: ${addresses.join(', ')}`);
  return addresses;
}

/**
 * Fuzzy match address name
 * Returns { exactMatch: string | null, partialMatches: string[] }
 */
function fuzzyMatchAddress(input, availableAddresses) {
  const inputLower = input.toLowerCase().trim();
  
  // Exact match (case-insensitive)
  const exact = availableAddresses.find(addr => 
    addr.toLowerCase() === inputLower
  );
  
  if (exact) {
    return { exactMatch: exact, partialMatches: [] };
  }
  
  // Partial matches (contains or is contained)
  const partial = availableAddresses.filter(addr => {
    const addrLower = addr.toLowerCase();
    return addrLower.includes(inputLower) || inputLower.includes(addrLower);
  });
  
  return { exactMatch: null, partialMatches: partial };
}

/**
 * Select a saved address by name (with optional fuzzy matching)
 * Simplified version: tries to click the address directly
 * 
 * @param {string} addressQuery - Address name or partial match (e.g., "sanskar", "New Home", "kundu")
 * @returns {Promise<{success: boolean, address: string}>}
 */
async function selectAddress(addressQuery) {
  log(`📍 Selecting address: "${addressQuery}"`);
  
  // Step 1: Get current address from header
  const snap1 = await browserCmd('snapshot', {});
  const snapshotText = snap1.snapshot || snap1.raw || JSON.stringify(snap1);
  const currentMatch = snapshotText.match(/button "([^"]*(?:blr|Home|Nagar)[^"]*)"\s*\[ref=(e\d+)\]/i);
  
  if (!currentMatch) {
    throw new Error('Address button not found in header');
  }
  
  const currentAddress = currentMatch[1];
  const buttonRef = currentMatch[2];
  
  log(`Current: ${currentAddress}`);
  
  // If query matches current (case-insensitive, partial), skip
  if (currentAddress.toLowerCase().includes(addressQuery.toLowerCase())) {
    log(`✅ Already at "${currentAddress}"`, 'success');
    return { success: true, address: currentAddress, alreadySelected: true };
  }
  
  // Step 2: Click address button to open modal
  await browserCmd('click', { ref: buttonRef });
  await sleep(1500);
  
  // Step 3: JavaScript click on target address (try exact match first, then fuzzy)
  const jsCode = `(() => {
    const query = ${JSON.stringify(addressQuery)};
    const input = document.querySelector('input[placeholder*="address"]');
    if (!input) return { error: 'Modal not found' };
    
    let modal = input;
    for (let i = 0; i < 15; i++) {
      if (!modal.parentElement) break;
      modal = modal.parentElement;
      if (window.getComputedStyle(modal).position === 'fixed') break;
    }
    
    const divs = Array.from(modal.querySelectorAll('div'));
    
    // Try exact match first (case-insensitive)
    let match = divs.find(d => {
      const text = d.textContent?.trim() || '';
      return text.toLowerCase().startsWith(query.toLowerCase());
    });
    
    // If not found, try fuzzy (contains)
    if (!match) {
      match = divs.find(d => {
        const text = d.textContent?.trim() || '';
        return text.toLowerCase().includes(query.toLowerCase());
      });
    }
    
    if (!match) return { error: 'Address not found: ' + query };
    
    // Find clickable parent
    let p = match;
    for (let i = 0; i < 10; i++) {
      if (!p) break;
      const s = window.getComputedStyle(p);
      if (p.onclick || p.getAttribute('onClick') || s.cursor === 'pointer') {
        p.scrollIntoView({ block: 'center' });
        const start = Date.now();
        while (Date.now() - start < 300) {}
        p.click();
        return { clicked: true, text: match.textContent.substring(0, 100) };
      }
      p = p.parentElement;
    }
    
    return { error: 'No clickable parent' };
  })()`;
  
  const result = await browserCmd('evaluate', { fn: jsCode });
  
  if (result.error || result.result?.error) {
    throw new Error(result.error || result.result.error);
  }
  
  const clickedText = result.clicked ? result.text : result.result?.text;
  log(`✅ Clicked: ${clickedText}`);
  
  // Step 4: Verify address change
  await sleep(2000);
  const snap2 = await browserCmd('snapshot', {});
  const snapshotText2 = snap2.snapshot || snap2.raw || JSON.stringify(snap2);
  const newMatch = snapshotText2.match(/button "([^"]*(?:blr|Home|Nagar)[^"]*)"\s*\[ref=(e\d+)\]/i);
  
  if (newMatch) {
    log(`🎉 Address changed to: ${newMatch[1]}`, 'success');
    return { success: true, address: newMatch[1] };
  }
  
  throw new Error('Could not verify address change');
}

/**
 * List all saved addresses
 */
async function listAddresses() {
  const addresses = await getAvailableAddresses();
  console.log(JSON.stringify({ addresses }, null, 2));
  return addresses;
}

// ==================== CLI ====================

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('Usage: zepto-agent.js <command> [options]');
    console.error('');
    console.error('Commands:');
    console.error('  clear-cart [--verify]           Clear cart (default: verify)');
    console.error('  add-item <query> [--force]      Add item (skips if in cart, use --force to add anyway)');
    console.error('  get-cart                        Get cart state');
    console.error('  get-cart-total                  Get cart total only');
    console.error('  shop "<item1>, <item2>"         Add items (requires empty cart)');
    console.error('  smart-shop "<item1>, <item2>"   Smart shop: clear unwanted, add missing');
    console.error('  select-address "<name>"         Select saved address (fuzzy match)');
    console.error('');
    console.error('Examples:');
    console.error('  zepto-agent.js clear-cart');
    console.error('  zepto-agent.js add-item "milk"');
    console.error('  zepto-agent.js smart-shop "milk, bread, eggs"  # RECOMMENDED');
    console.error('  zepto-agent.js shop "milk, bread, honey"       # legacy, needs empty cart');
    console.error('  zepto-agent.js select-address "sanskar"        # fuzzy match works!');
    process.exit(1);
  }

  const command = args[0];
  const options = {};

  // Parse flags
  for (let i = 1; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const flag = args[i].slice(2);
      options[flag] = true;
    }
  }

  try {
    await openZepto();

    switch (command) {
      case 'clear-cart':
        await clearCart({ verify: options.verify !== undefined ? options.verify : true });
        break;

      case 'add-item':
        if (args.length < 2) {
          throw new Error('Usage: add-item <query> [--force]');
        }
        await addItem(args[1], { 
          confirm: true,
          force: options.force === true
        });
        break;

      case 'get-cart':
        await getCart();
        break;

      case 'get-cart-total':
        await getCartTotal();
        break;

      case 'shop':
        if (args.length < 2) {
          throw new Error('Usage: shop "<item1>, <item2>, ..."');
        }
        await shop(args[1], options);
        break;

      case 'smart-shop':
        if (args.length < 2) {
          throw new Error('Usage: smart-shop "<item1>, <item2>, ..."');
        }
        await smartShop(args[1], options);
        break;

      case 'select-address':
        if (args.length < 2) {
          throw new Error('Usage: select-address "<address name or partial match>"');
        }
        await selectAddress(args[1]);
        break;

      default:
        throw new Error(`Unknown command: ${command}`);
    }

    process.exit(0);
  } catch (err) {
    log(err.message, 'error');
    log(err.stack, 'error');
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { 
  clearCart, 
  addItem, 
  checkItemInCart,
  getCart, 
  shop, 
  smartShop,
  selectAddress,
  listAddresses,
  getAvailableAddresses,
  fuzzyMatchAddress,
  getCartTotal 
};
