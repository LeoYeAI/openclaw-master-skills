#!/usr/bin/env node
/**
 * JSONB 数据处理工具 JSONB Handler 📜
 * 
 * 用于 JSONB 字段的查询、转换、索引优化等
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
 * 在 JSONB 字段中搜索关键字
 */
async function searchJsonbField(table, jsonbColumn, keyword) {
  const query = `
    SELECT id, data 
    FROM ${table} 
    WHERE data @> '${JSON.stringify({ [jsonbColumn]: keyword })}'
    LIMIT 100;
  `;
  
  try {
    const result = await pool.query(query);
    console.log(`🔍 在 ${table}.${jsonbColumn} 中搜索 "${keyword}"，找到 ${result.rows.length} 条记录`);
    
    return { success: true, results: result.rows };
    
  } catch (err) {
    console.error(`❌ 搜索失败：${err.message}`);
    throw err;
  }
}

/**
 * 提取 JSONB 中的特定字段
 */
async function extractJsonbField(table, jsonbColumn, path) {
  const query = `
    SELECT id, (data->>'${path}') AS value
    FROM ${table}
  `;
  
  try {
    const result = await pool.query(query);
    
    console.log(`📦 提取字段：${path}\n`);
    
    return { success: true, values: result.rows };
    
  } catch (err) {
    console.error(`❌ 提取失败：${err.message}`);
    throw err;
  }
}

/**
 * 将 JSONB 字段转换为关系表（反规范化）
 */
async function expandJsonb(table, jsonbColumn, targetTable = null) {
  const query = `
    SELECT 
      id, 
      data->>'key1' AS key1,
      data->>'key2' AS key2,
      data->>'key3' AS key3
    FROM ${table}
    LIMIT 10;
  `;
  
  try {
    console.log(`🚀 JSONB 字段展开（反规范化）`);
    
    // ... 实际实现会将 JSONB 扁平化插入到新表
    
    return { success: true, message: 'JSONB 展开示例完成' };
    
  } catch (err) {
    console.error(`❌ 展开失败：${err.message}`);
    throw err;
  }
}

/**
 * 为 JSONB 字段创建 GIN 索引（提升数组/对象查询性能）
 */
async function createGinIndex(table, jsonbColumn) {
  const query = `
    CREATE INDEX IF NOT EXISTS ${table}_${jsonbColumn}_gin_idx 
    ON ${table} USING GIN (data);
  `;
  
  try {
    await pool.query(query);
    
    console.log(`✅ 创建 GIN 索引：${table}.${jsonbColumn}`);
    console.log('💡 现在可以高效查询 JSONB 数组和对象字段');
    
    return { success: true, query };
    
  } catch (err) {
    if (err.code === '42701') { // missing column
      console.error(`❌ 列不存在：${table}.${jsonbColumn}`);
    } else {
      console.error(`❌ 索引创建失败：${err.message}`);
    }
    throw err;
  }
}

/**
 * 验证 JSONB 数据格式
 */
async function validateJsonb(table, jsonbColumn) {
  const query = `
    SELECT 
      COUNT(*) AS total_rows,
      COUNT(data IS NOT NULL) AS not_null_count,
      SUM(data @> '{}'::jsonb) AS valid_json_count
    FROM ${table}
    WHERE data IS NOT NULL;
  `;
  
  try {
    const result = await pool.query(query);
    
    console.log(`🔍 JSONB 数据验证结果:`);
    console.log(`总行数：${result.rows[0].total_rows}`);
    console.log(`非空值：${result.rows[0].not_null_count}`);
    console.log(`有效 JSON: ${result.rows[0].valid_json_count}`);
    
    return { success: true, stats: result.rows[0] };
    
  } catch (err) {
    console.error(`❌ 验证失败：${err.message}`);
    throw err;
  }
}

/**
 * JSONB 聚合查询（统计字段出现次数）
 */
async function countJsonbKeys(table, jsonbColumn) {
  const query = `
    SELECT 
      data->>'key' AS key_name,
      COUNT(*) AS occurrences
    FROM ${table}
    WHERE data ? 'key'
    GROUP BY data->>'key'
    ORDER BY occurrences DESC;
  `;
  
  try {
    const result = await pool.query(query);
    
    console.log(`📊 ${jsonbColumn} 字段统计:`);
    result.rows.forEach(row => {
      console.log(`${row.key_name}: ${row.occurrences}次`);
    });
    
    return { success: true, stats: result.rows };
    
  } catch (err) {
    console.error(`❌ 统计失败：${err.message}`);
    throw err;
  }
}

/**
 * 将 JSONB 数组转换为关系表（JOIN 优化）
 */
async function joinJsonbArray(table, jsonbColumn, linkTable) {
  const query = `
    SELECT 
      t.id AS parent_id,
      a.item ->> 'name' AS item_name,
      COUNT(*) AS occurrences
    FROM ${table} t
    CROSS LATERAL JSONB_ARRAY_ELEMENTS(t.${jsonbColumn}) AS a(item)
    LEFT JOIN link_table lt ON lt.name = a.item
    GROUP BY t.id, a.item;
  `;
  
  try {
    const result = await pool.query(query);
    
    return { success: true, results: result.rows };
    
  } catch (err) {
    console.error(`❌ JOIN 失败：${err.message}`);
    throw err;
  }
}

/**
 * JSONB 数据转换（从文本到 JSONB）
 */
async function convertToJsonb(table, textColumn, jsonbColumn) {
  const query = `
    UPDATE ${table}
    SET ${jsonbColumn} = TO_JSONB(
      CASE 
        WHEN data IS NULL THEN '{}'::jsonb
        ELSE TO_JSONB(JSON_PARSE(data))
      END
    )
    WHERE ${textColumn} IS NOT NULL;
  `;
  
  try {
    const result = await pool.query(query);
    
    console.log(`✅ 数据转换完成：${result.rowCount} 条记录已更新`);
    
    return { success: true, updated: result.rowCount };
    
  } catch (err) {
    console.error(`❌ 转换失败：${err.message}`);
    throw err;
  }
}

// CLI 使用示例
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    console.log(`
JSONB 处理工具 v1.0

用法:
  # 在 JSONB 字段中搜索
  node jsonb_handler.js --search users profile 'age' 30
  
  # 为 JSONB 创建 GIN 索引
  node jsonb_handler.js --index users data
  
  # 提取字段值
  node jsonb_handler.js --extract products data '.category'
  
  # 统计 JSONB 键出现次数
  node jsonb_handler.js --count products data

选项:
  --search <table> <column> <key>  [limit]     搜索 JSONB 字段
  --index <table> <column>          创建 GIN 索引
  --extract <table> <column> <path>  提取指定路径的值
  --count <table> <column>          统计键出现次数
  --validate <table> <column>       验证 JSONB 数据格式
  --convert <table> <text_col> <jsonb_col> 转换文本到JSONB
  --help                            显示此帮助信息
    `);
    process.exit(0);
  }
}

main().catch(console.error);
