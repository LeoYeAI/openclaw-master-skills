#!/usr/bin/env node
/**
 * 查询辅助工具 - 用于快速编写和执行 SQL 查询
 */

const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT) || 5432,
  database: process.env.DB_NAME || 'postgres',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
});

/**
 * 执行 SELECT 查询并格式化输出
 */
async function executeQuery(sql, params = []) {
  try {
    const result = await pool.query(sql, params);
    
    // 格式化为表格显示
    if (result.rows.length > 0) {
      const headers = Object.keys(result.rows[0]);
      console.log(headers.join('\t'));
      result.rows.forEach(row => {
        console.log(Object.values(row).map(v => String(v)).join('\t'));
      });
    } else {
      console.log('无数据');
    }
    
    return result;
  } catch (err) {
    console.error(`查询错误：${err.message}`);
    throw err;
  }
}

/**
 * 聚合统计查询生成器
 */
function generateStatsQuery(table, fields = [], where = {}, groupBy = []) {
  const conditions = Object.entries(where).map(([k, v]) => 
    `WHERE ${k} = '${v}'`
  ).join(' AND ');

  const groupSql = groupBy.length ? `GROUP BY ${groupBy.join(', ')}` : '';
  
  return `SELECT ${fields.join(', ')} FROM ${table} ${conditions} ${groupBy ? groupSql : ''}`;
}

/**
 * 分页查询生成器
 */
function generatePagedQuery(table, selectClause = '*', where = {}, page = 1, pageSize = 10) {
  const offset = (page - 1) * pageSize;
  
  return `SELECT ${selectClause || '*'} FROM (${generateStatsQuery(table, where)}) AS subquery LIMIT ${pageSize} OFFSET ${offset}`;
}

// CLI
async function main() {
  // ... 查询解析和执行逻辑
}

main().catch(console.error);
