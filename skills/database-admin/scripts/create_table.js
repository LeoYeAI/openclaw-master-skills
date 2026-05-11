#!/usr/bin/env node
/**
 * 表创建工具 - 用于快速创建数据库表结构
 * 
 * 用法: node create_table.js --help
 * 
 * 示例:
 *   node create_table.js table_name column1:type,column2:type ... --index col1
 */

const { Pool } = require('pg');

// 连接配置 - 主任可根据需要修改
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT) || 5432,
  database: process.env.DB_NAME || 'postgres',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
});

/**
 * 解析列定义字符串 "name:type,index_name"
 */
function parseColumns(columnsStr) {
  return columnsStr.split(',').map(col => {
    const parts = col.trim().split(':');
    const name = parts[0].trim();
    let type = parts[1]?.trim() || 'TEXT';
    
    // 处理索引
    const indexMatch = parts[2]?.match(/^(.+?)(?:\s+(primary|unique|index|fulltext)?(?:\([^)]+\))?)?$/i);
    const indexName = indexMatch ? indexMatch[1] : undefined;
    const indexType = indexMatch ? (indexMatch[2] || 'index') : undefined;

    return { name, type, index: indexName };
  });
}

/**
 * 格式化 SQL CREATE TABLE 语句
 */
function formatCreateTable(tableName, columns) {
  const pkColumn = columns.find(c => c.name.toUpperCase() === 'ID'); // 默认 id 为主键
  
  let sql = `CREATE TABLE IF NOT EXISTS ${tableName} (\n`;
  const colDefs = columns.map((col, idx) => {
    let def = `${col.name}${col.type}`;
    
    if (idx === 0 && !pkColumn) {
      def += ' PRIMARY KEY'; // 第一列自动为主键（如果表中没有专门的 id）
    } else if (pkColumn && col.name.toUpperCase() !== 'ID') {
      def += ` DEFAULT ${col.type}::${col.type}`;
    }

    return `${def}${col.index ? ` [索引：${col.index}]` : ''}`;
  }).join(',\n');

  const idxDefs = columns.filter(c => c.index).map(col => 
    `CREATE INDEX IF NOT EXISTS ${col.name}_idx ON ${tableName} (${col.index || col.name});`
  ).join('\n');

  return `${sql}${colDefs}\n);${idxDefs}`;
}

/**
 * 执行建表操作
 */
async function createTable(tableName, columns) {
  const sql = formatCreateTable(tableName, columns);
  
  try {
    await pool.query(sql);
    console.log(`✅ 表 ${tableName} 创建成功`);
    return { success: true, table: tableName };
  } catch (err) {
    console.error(`❌ 建表失败：${err.message}`);
    return { success: false, error: err.message };
  }
}

/**
 * 插入数据到已有表
 */
async function insertData(tableName, records) {
  const batchSize = 1000;
  let offset = 0;
  
  try {
    while (offset < records.length) {
      const batch = records.slice(offset, offset + batchSize);
      
      // 转换为 JSON 字符串用于批量插入
      const values = batch.map(r => 
        Object.keys(r).map(k => `'${r[k]}'`).join(', ')
      );

      const sql = `INSERT INTO ${tableName} (VALUES ${values.join('), (')})`;
      
      await pool.query(sql);
      console.log(`✅ 已插入 ${batch.length} 条记录...`);
      offset += batchSize;
    }
    
    return { success: true, inserted: records.length };
  } catch (err) {
    console.error(`❌ 插入失败：${err.message}`);
    return { success: false, error: err.message };
  }
}

// CLI 解析
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    console.log(`
数据库管理工具 v1.0

用法示例：

# 创建表
node create_table.js users id:SERIAL PRIMARY KEY,email:VARCHAR(100) UNIQUE,username:TEXT --index email

# 插入数据
node create_table.js users '[{"email":"a@b.com","username":"alice"},{"email":"c@d.com","username":"bob"}]' --insert

# 帮助信息
--help

连接配置请设置环境变量：
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=postgres
DB_PASSWORD=your_password
    `);
    process.exit(0);
  }
  
  // ... 其他实现逻辑
}

main().catch(console.error);
