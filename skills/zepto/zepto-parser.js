#!/usr/bin/env node

/**
 * zepto-parser.js - Intelligent snapshot parser for Zepto.com
 * Extracts only meaningful data from verbose browser snapshots
 * 
 * Usage:
 *   echo "$SNAPSHOT" | node zepto-parser.js refs
 *   echo "$SNAPSHOT" | node zepto-parser.js product "milk"
 *   echo "$SNAPSHOT" | node zepto-parser.js cart
 */

const readline = require('readline');

// Simple fuzzy matching (no deps)
function fuzzyMatch(str, pattern) {
  const strLower = str.toLowerCase();
  const patternLower = pattern.toLowerCase();
  
  // Exact substring match = best
  if (strLower.includes(patternLower)) {
    return 1.0;
  }
  
  // Simple character overlap ratio
  const strChars = new Set(strLower);
  const patternChars = patternLower.split('');
  const overlap = patternChars.filter(c => strChars.has(c)).length;
  return overlap / patternLower.length;
}

function extractRef(line) {
  const match = line.match(/\[ref=([^\]]+)\]/);
  return match ? match[1] : null;
}

function extractPrice(text) {
  const match = text.match(/₹(\d+)/);
  return match ? parseInt(match[1]) : null;
}

function parseProductLine(line) {
  // Format: link "ProductName ADD ... ₹X ... [details]" [ref=eXX]
  if (!line.includes('link "') || !line.includes('ADD')) {
    return null;
  }
  
  const ref = extractRef(line);
  if (!ref) return null;
  
  // Extract product name (before "ADD")
  const linkMatch = line.match(/link "([^"]+)"/);
  if (!linkMatch) return null;
  
  const fullText = linkMatch[1];
  const addIndex = fullText.indexOf(' ADD');
  if (addIndex === -1) return null;
  
  const name = fullText.substring(0, addIndex).trim();
  
  // Extract price
  const price = extractPrice(fullText);
  
  // Check for "Buy Again"
  const buyAgain = fullText.includes('Buy Again');
  
  return { name, ref, price, buyAgain };
}

function parseSnapshot(lines) {
  const data = {
    searchRef: null,
    cartRef: null,
    products: [],
    checkoutRef: null,
    cartTotal: null
  };
  
  for (const line of lines) {
    // Search bar (can be combobox or link)
    if ((line.includes('combobox') || line.includes('link')) && line.includes('Search')) {
      data.searchRef = extractRef(line);
    }
    
    // Cart button
    else if (line.includes('button') && line.includes('Cart') && !line.includes('Add to')) {
      const ref = extractRef(line);
      // Skip if it's a complex cart description (delivery address)
      if (ref && line.split('"').length < 6) {
        data.cartRef = ref;
      }
    }
    
    // Checkout button
    else if (line.includes('Click to Pay ₹')) {
      data.checkoutRef = extractRef(line);
      data.cartTotal = extractPrice(line);
    }
    
    // Product listings
    else if (line.includes('link "') && line.includes('ADD')) {
      const product = parseProductLine(line);
      if (product) {
        data.products.push(product);
      }
    }
    
    // ADD buttons (standalone) - find the one right after product
    else if (line.includes('button "ADD"')) {
      const ref = extractRef(line);
      if (ref && data.products.length > 0) {
        const lastProduct = data.products[data.products.length - 1];
        // If product doesn't have a ref yet, use this button's ref
        if (!lastProduct.addButtonRef) {
          lastProduct.addButtonRef = ref;
        }
      }
    }
  }
  
  return data;
}

function findProduct(data, query) {
  let bestMatch = null;
  let bestScore = 0;
  
  for (const product of data.products) {
    let score = fuzzyMatch(product.name, query);
    
    // Boost for "Buy Again"
    if (product.buyAgain) {
      score += 0.3;
    }
    
    // Boost for exact price match (if provided)
    // Future: Could pass expected price as param
    
    if (score > bestScore) {
      bestScore = score;
      bestMatch = product;
    }
  }
  
  // Require at least 50% match
  return bestScore > 0.5 ? { ...bestMatch, matchScore: bestScore } : null;
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === '--help') {
    console.log('Usage:');
    console.log('  zepto-parser.js refs              - Extract UI refs (search, cart, checkout)');
    console.log('  zepto-parser.js product <query>   - Find product matching query');
    console.log('  zepto-parser.js cart              - Extract cart summary');
    console.log('  zepto-parser.js products [limit]  - List all products (optional limit)');
    console.log('');
    console.log('Input: Browser snapshot via stdin');
    console.log('Output: JSON to stdout');
    process.exit(0);
  }
  
  // Read snapshot from stdin
  const rl = readline.createInterface({
    input: process.stdin,
    crlfDelay: Infinity
  });
  
  const lines = [];
  for await (const line of rl) {
    lines.push(line);
  }
  
  const data = parseSnapshot(lines);
  
  // Execute command
  switch (command) {
    case 'refs':
      console.log(JSON.stringify({
        search: data.searchRef,
        cart: data.cartRef,
        checkout: data.checkoutRef
      }, null, 2));
      break;
      
    case 'product': {
      const query = args.slice(1).join(' ');
      if (!query) {
        console.error('Error: Missing product query');
        process.exit(1);
      }
      const match = findProduct(data, query);
      if (match) {
        console.log(JSON.stringify(match, null, 2));
      } else {
        console.log(JSON.stringify({ error: 'No matching product found' }));
        process.exit(1);
      }
      break;
    }
    
    case 'cart':
      console.log(JSON.stringify({
        checkout: data.checkoutRef,
        total: data.cartTotal
      }, null, 2));
      break;
      
    case 'products': {
      const limit = parseInt(args[1]) || data.products.length;
      const products = data.products.slice(0, limit).map(p => ({
        name: p.name,
        price: p.price,
        ref: p.ref,
        buyAgain: p.buyAgain || false
      }));
      console.log(JSON.stringify(products, null, 2));
      break;
    }
    
    default:
      console.error(`Error: Unknown command '${command}'`);
      console.error('Run with --help for usage');
      process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
