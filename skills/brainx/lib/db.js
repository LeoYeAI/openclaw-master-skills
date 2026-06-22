const { Pool } = require('pg');

// Load env from .env file if present
try {
  const dotenv = require('dotenv');
  const path = process.env.BRAINX_ENV || require('path').join(__dirname, '..', '.env');
  dotenv.configDotenv({ path });
} catch (_) {}

// Support shared env file for all agents (fallback)
if (!process.env.DATABASE_URL && process.env.BRAINX_ENV) {
  try {
    require('dotenv').config({ path: process.env.BRAINX_ENV });
  } catch (_) {}
}

const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL) {
  throw new Error('DATABASE_URL is required');
}

const pool = new Pool({ connectionString: DATABASE_URL });

async function query(text, params) {
  return pool.query(text, params);
}

async function withClient(fn) {
  const client = await pool.connect();
  try {
    return await fn(client);
  } finally {
    client.release();
  }
}

async function health() {
  const r = await query('select 1 as ok');
  return r.rows?.[0]?.ok === 1;
}

module.exports = { pool, query, withClient, health };
