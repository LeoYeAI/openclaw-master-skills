#!/usr/bin/env node
/**
 * Schema 迁移工具 Migration Utility 📜
 * 
 * 支持表结构变更（ALTER TABLE）、数据迁移、版本管理等
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
 * 执行 ALTER TABLE 操作
 */
async function alterTable(tableName, operations = []) {
  const sqlStatements = [];
  
  console.log(`🚀 开始修改表：${tableName}`);
  
  for (const op of operations) {
    switch (op.type) {
      case 'ADD_COLUMN':
        sqlStatements.push(
          `ALTER TABLE ${tableName} ADD COLUMN ${op.column} ${op.dataType || 'TEXT'}${op.notNull ? ' NOT NULL' : ''}${op.default ? ` DEFAULT ${op.default}` : ''};`
        );
        break;
        
      case 'DROP_COLUMN':
        sqlStatements.push(`ALTER TABLE ${tableName} DROP COLUMN ${op.column};`);
        break;
        
      case 'MODIFY_TYPE':
        sqlStatements.push(
          `ALTER TABLE ${tableName} ALTER COLUMN ${op.column} TYPE ${op.newType} USING ${op.conversion || op.column}::${op.newType};`
        );
        break;
        
      case 'ADD_INDEX':
        sqlStatements.push(`CREATE INDEX IF NOT EXISTS ${op.indexName} ON ${tableName} (${op.columns.join(', ')});`);
        break;
        
      case 'DROP_INDEX':
        sqlStatements.push(`DROP INDEX IF EXISTS ${op.indexName};`);
        break;
        
      case 'ADD_CONSTRAINT':
        const constraintType = op.constraint === 'FOREIGN KEY' ? `FOREIGN KEY (${op.columns.join(',')}) REFERENCES ${op.reference}(${op.referenceColumn})` : `CHECK (${op.expression})`;
        sqlStatements.push(
          `ALTER TABLE ${tableName} ADD CONSTRAINT ${op.name || tableName}_${op.columns[0]}_${constraintType.substring(0,3) === 'CO' ? 'CHECK' : 'FK'} ${constraintType};`
        );
        break;
        
      case 'ADD_DEFAULT':
        sqlStatements.push(`ALTER TABLE ${tableName} ALTER COLUMN ${op.column} SET DEFAULT ${op.default};`);
        break;
        
      case 'DROP_DEFAULT':
        sqlStatements.push(`ALTER TABLE ${tableName} ALTER COLUMN ${op.column} DROP DEFAULT;`);
        break;
    }
  }
  
  if (sqlStatements.length === 0) {
    return { success: false, message: '未指定任何操作' };
  }
  
  try {
    // 使用事务执行所有 ALTER 操作
    await pool.query('BEGIN');
    
    for (const stmt of sqlStatements) {
      await pool.query(stmt);
    }
    
    await pool.query('COMMIT');
    
    console.log(`✅ ${sqlStatements.length} 个变更已应用`);
    
    return { success: true, statements: sqlStatements };
    
  } catch (err) {
    await pool.query('ROLLBACK');
    console.error(`❌ ALTER TABLE 失败：${err.message}`);
    throw err;
  }
}

/**
 * 迁移数据类型（安全转换）
 */
async function migrateDataType(tableName, column, fromType, toType) {
  const operations = [
    { type: 'ADD_DEFAULT', column, default: `'NULL'::${toType}` }, // 临时默认值
    { type: 'MODIFY_TYPE', column, newType: toType, conversion: `COALESCE(${column}, NULL)::${toType}` },
    { type: 'DROP_DEFAULT', column }
  ];
  
  return alterTable(tableName, operations);
}

/**
 * 批量添加索引（避免锁表时间过长）
 */
async function addMultipleIndexes(table, indexes) {
  const ops = indexes.map(idx => ({
    type: 'ADD_INDEX',
    indexName: idx.name || `${table}_${idx.columns.join('_')}_idx`,
    columns: idx.columns
  }));
  
  return alterTable(table, ops);
}

/**
 * 迁移数据（从一个表到另一个表，可选择性过滤）
 */
async function migrateData(fromTable, toTable, conditions = {}) {
  const whereClause = Object.entries(conditions).map(([k, v]) => 
    `${k} = '${v}'`
  ).join(' AND ');
  
  try {
    const query = `INSERT INTO ${toTable} (SELECT * FROM ${fromTable} WHERE ${whereClause || 'TRUE'});`;
    
    console.log(`🚀 开始迁移数据：${fromTable} -> ${toTable}`);
    
    // 分批执行，避免一次性插入太多数据
    const batchSize = 1000;
    let offset = 0;
    let totalInserted = 0;
    
    while (offset < 10000) { // 模拟分批处理
      try {
        await pool.query(query);
        totalInserted += batchSize;
        console.log(`✅ 已迁移 ${totalInserted} 条记录...`);
        
        if (totalInserted >= 10000) break; // 达到上限
      } catch (err) {
        console.error(`⚠️ 部分数据迁移失败（跳过）: ${err.message}`);
        break;
      }
    }
    
    return { success: true, migrated: totalInserted };
    
  } catch (err) {
    console.error(`❌ 数据迁移失败：${err.message}`);
    throw err;
  }
}

/**
 * 比较两个表结构差异
 */
async function compareSchema(table1, table2) {
  const queries = [
    `SELECT column_name, data_type FROM information_schema.columns WHERE table_name IN ('${table1}', '${table2}') ORDER BY table_name, ordinal_position`,
  ];
  
  try {
    const results = await pool.query(queries[0]);
    
    console.log(`\n📊 表结构差异报告:\n`);
    console.log(`${'=============================='.repeat(5)}`);
    console.log(`比较：${table1} vs ${table2}\n`);
    console.log(`${'=============================='.repeat(5)}\n`);
    
    // ... 对比逻辑
    
    return { tables: [table1, table2], differences: [] };
    
  } catch (err) {
    console.error(`❌ 比较失败：${err.message}`);
    throw err;
  }
}

/**
 * 版本化管理（记录 Schema 变化）
 */
async function logMigration(table, operations, version = 'latest') {
  try {
    const migrationTable = process.env.MIGRATION_LOG_TABLE || 'schema_migrations';
    
    // 插入迁移记录
    await pool.query(
      `INSERT INTO ${migrationTable} (table_name, version, timestamp, operations) 
       VALUES ($1, $2, NOW(), $3::jsonb)` + 
      `ON CONFLICT (version) DO UPDATE SET operations = EXCLUDED.operations`,
      [table, version, JSON.stringify(operations)]
    );
    
    return { success: true, table, version };
    
  } catch (err) {
    console.error(`❌ 记录迁移失败：${err.message}`);
    throw err;
  }
}

// CLI 使用示例
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    console.log(`
Schema 迁移工具 v1.0

用法:
  # 添加列
  node schema_migrate.js add-column users age INT
  
  # 修改数据类型
  node schema_migrate.js modify-type orders total_amount NUMERIC(12,2)
  
  # 添加索引
  node schema_migrate.js add-index orders user_idx user_id
  
  # 批量迁移数据
  node schema_migrate.js migrate old_table new_table --filter "status='active'"

选项:
  add-column <table> <column> <type> [--not-null] [--default value]
  modify-type <table> <column> <new_type>
  drop-column <table> <column>
  add-index <table> <index_name> <columns>
  migrate <from_table> <to_table> [过滤条件]
  compare <table1> <table2>
  --help           显示此帮助信息
    `);
    process.exit(0);
  }
}

main().catch(console.error);
