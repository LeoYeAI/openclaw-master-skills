#!/usr/bin/env node
/**
 * Query Universal Profile assets via LUKSO Indexer (Envio GraphQL)
 * 
 * Usage:
 *   node query-assets.js <up-address>
 * 
 * Returns: JSON array of assets held by the UP
 */

const INDEXER_ENDPOINT = 'https://envio.lukso-mainnet.universal.tech/v1/graphql';

export async function queryAssets(upAddress) {
  // Validate address format to prevent GraphQL injection
  if (!upAddress || !/^0x[a-fA-F0-9]{40}$/.test(upAddress)) {
    throw new Error('Invalid address format. Expected 0x followed by 40 hex characters.');
  }

  const query = `{
    Hold(where: { profile_id: { _ilike: "${upAddress.toLowerCase()}" } }) {
      asset_id
      balance
      asset {
        id
        name
        description
      }
    }
  }`;

  try {
    const response = await fetch(INDEXER_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });

    const result = await response.json();
    
    if (result.errors) {
      throw new Error(`GraphQL errors: ${JSON.stringify(result.errors)}`);
    }

    return result.data.Hold;
  } catch (error) {
    throw new Error(`Failed to query assets: ${error.message}`);
  }
}

// CLI execution
if (import.meta.url === `file://${process.argv[1]}`) {
  const upAddress = process.argv[2];
  
  if (!upAddress) {
    console.error('Usage: node query-assets.js <up-address>');
    process.exit(1);
  }

  queryAssets(upAddress)
    .then(assets => {
      console.log(JSON.stringify(assets, null, 2));
    })
    .catch(error => {
      console.error('Error:', error.message);
      process.exit(1);
    });
}
