#!/usr/bin/env node
/**
 * 批量插入优化工具 Bulk Insert Optimizer
 * 
 * 使用事务和 COPY 协议实现高效批量插入
 */

const { Pool } = require('pg');
const fs = require('fs');

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT) || 5432,
  database: process.env.DB_NAME || 'postgres',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
});

/**
 * 批量插入数据 - 使用 COPY FROM STDIN 实现最高效的插入
 */
async function bulkInsert(tableName, records, options = {}) {
  const batchSize = options.batchSize || 1000;
  
  console.log(`🚀 开始批量插入到 ${tableName}，共 ${records.length} 条记录`);
  console.log(`📦 批处理大小：${batchSize}`);
  
  try {
    let offset = 0;
    const startTime = Date.now();
    
    while (offset < records.length) {
      const batch = records.slice(offset, offset + batchSize);
      
      // 转换为 COPY 格式的字符串数组
      const columns = Object.keys(batch[0]);
      const values = batch.map(r => 
        columns.map(k => {
          const v = r[k];
          if (v === null) return 'NULL';
          if (typeof v === 'boolean') return v ? 'TRUE' : 'FALSE';
          return `'${String(v).replace(/'/g, "''")}'`;
        }).join(', ')
      );
      
      // 使用 COPY 协议批量插入（比 INSERT...VALUES 快 10 倍以上）
      const copySql = `COPY ${tableName} (${columns.join(',')}) FROM STDIN WITH (FORMAT CSV)`;
      
      await pool.query(copySql, [...values]);
      
      offset += batchSize;
    }
    
    const duration = Date.now() - startTime;
    console.log(`✅ 批量插入完成！耗时：${duration}ms，平均每条约 ${(duration/records.length).toFixed(2)}ms`);
    
    return { 
      success: true, 
      inserted: records.length, 
      duration: duration,
      copy: true 
    };
    
  } catch (err) {
    console.error(`❌ 批量插入失败：${err.message}`);
    console.error(err.stack);
    return { success: false, error: err.message };
  }
}

/**
 * 从 JSON 文件或 CSV 读取数据并批量插入
 */
async function loadAndInsert(filePath, tableName) {
  let data;
  
  // 检测文件类型
  const ext = filePath.split('.').pop();
  
  if (ext === 'json') {
    data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    console.log(`📂 从 ${filePath} 读取到 ${typeof data === 'array' ? data.length : Object.keys(data).length} 条记录`);
  } else if (ext === 'csv') {
    // 简单的 CSV 解析（生产环境建议使用 better-promise-fs）
    const content = fs.readFileSync(filePath, 'utf8');
    data = [];
    data.push(Object.values(content.split('\n')[0].split(',')).map(v => v.trim()));
    
    for (const line of content.split('\n').slice(1)) {
      if (!line.trim()) continue;
      const row = line.split(',').map(cell => cell.trim());
      // ... 简单转换逻辑，生产环境需要更完善的处理
    }
  }
  
  return bulkInsert(tableName, data);
}

/**
 * 插入数据并返回受影响行数
 */
async function insertWithCheck(tableName, records, columns) {
  const batchSize = 500;
  let offset = 0;
  
  try {
    while (offset < records.length) {
      const batch = records.slice(offset, offset + batchSize);
      
      // 构建 INSERT 语句
      const values = batch.map(r => 
        Object.keys(r).map(k => `'${String(r[k] || '').replace(/'/g, "''")}'`
      ).join(', '));

      const sql = `INSERT INTO ${tableName} (${columns.join(',')}) VALUES ${values.join('), (' )}`;
      
      const result = await pool.query(sql);
      offset += batchSize;
    }
    
    console.log(`✅ 插入完成，共 ${records.length} 条记录`);
    return { success: true, inserted: records.length };
  } catch (err) {
    console.error(`❌ 插入失败：${err.message}`);
    throw err;
  }
}

// CLI 使用示例
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    console.log(`
批量插入工具 v1.0

用法:
  node insert_bulk.js --table users --file data.json
  node insert_bulk.js --table orders --batch 500
  node insert_bulk.js --copy true --table products

选项:
  --table <name>      目标表名
  --file <path>       JSON/CSV 文件路径（可选，如果通过 stdin 提供数据）
  --batch <n>         批处理大小（默认：1000）
  --copy              使用 COPY 协议（更快）
  --help              显示此帮助信息

环境变量:
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    `);
    process.exit(0);
  }
}

main().catch(console.error);
