#!/usr/bin/env node
/**
 * 查询优化工具 Query Optimizer
 * 
 * 分析查询性能、生成执行计划、提供优化建议
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
 * 获取查询执行计划并分析性能瓶颈
 */
async function analyzeQuery(query) {
  const startTime = Date.now();
  
  try {
    // 执行 EXPLAIN (ANALYZE, BUFFERS) 获取详细执行计划
    const explainQuery = `EXPLAIN (ANALYZE, BUFFERS, VERBOSE) ${query}`;
    const result = await pool.query(explainQuery);
    
    const plan = JSON.parse(result.rows[0].plan);
    const duration = Date.now() - startTime;
    
    console.log(`\n🔍 查询执行计划分析\n`);
    console.log('==================');
    console.log('\n查询耗时:', plan.total_plan_time + 'ms');
    console.log('实际耗时:', plan.actual_total_time + 'ms (包括查询本身)');
    console.log('行数扫描:', plan.rows_scanned || plan.total_rows);
    
    // 输出执行计划树形结构
    console.log('\n执行计划树:');
    printExecutionPlan(plan.plan_tree, 0);
    
    // 生成优化建议
    const suggestions = generateSuggestions(plan, duration);
    
    console.log('\n🔧 优化建议:');
    suggestions.forEach((s, i) => {
      console.log(`${i + 1}. ${s}`);
    });
    
    return { plan, analysis: { duration, suggestions } };
    
  } catch (err) {
    console.error(`❌ 分析失败：${err.message}`);
    throw err;
  }
}

/**
 * 打印执行计划树形结构（递归）
 */
function printExecutionPlan(node, depth = 0) {
  const indent = '  '.repeat(depth);
  
  if (node && typeof node === 'object') {
    console.log(`${indent}└── ${JSON.stringify(node)}`); // 简单打印，生产环境需要更复杂的解析
    
    for (const child of Object.values(node)) {
      printExecutionPlan(child, depth + 1);
    }
  }
}

/**
 * 生成优化建议
 */
function generateSuggestions(plan, duration) {
  const suggestions = [];
  
  if (duration > 1000) {
    suggestions.push('⚠️ 查询耗时超过 1 秒，需要优化');
  }
  
  // 检查是否使用了 Sequential Scan 而不是 Index Scan
  if (plan.plan_type === 'Seq Scan' && plan.rows_scanned > 10000) {
    suggestions.push(`⚠️ 在大表上进行了顺序扫描（${plan.rows_scanned} 行），考虑为 WHERE 条件字段创建索引`);
  }
  
  // 检查嵌套循环连接
  if (plan.join_type === 'Nested Loop' && plan.rows_scanned > 100) {
    suggestions.push('⚠️ 使用了 Nested Loop Join，在大表上可能效率低，考虑改为 Hash Join');
  }
  
  // 检查是否选择了不必要的列
  if (plan.columns_count && plan.columns_count > 5) {
    suggestions.push(`💡 只选择需要的列，避免 SELECT *（当前选择了 ${plan.columns_count} 列）`);
  }
  
  // 检查 WHERE 条件
  if (plan.where_clause && !plan.index_name) {
    const field = Object.keys(plan.where_condition)[0];
    suggestions.push(`💡 为 ${field} 字段创建索引可能提升查询性能`);
  }
  
  return suggestions;
}

/**
 * 生成索引推荐报告
 */
async function generateIndexReport(tableName) {
  try {
    const query = `
      SELECT 
        indexname,
        indexdef,
        pg_size_pretty(pg_relation_size(indexrelid)) as index_size
      FROM pg_indexes
      WHERE schemaname = 'public' AND tablename = '${tableName}'
      ORDER BY pg_relation_size(indexrelid) DESC;
    `;
    
    const result = await pool.query(query);
    
    console.log(`\n📊 表 ${tableName} 的现有索引:`);
    if (result.rows.length === 0) {
      console.log('⚠️ 暂无索引');
    } else {
      result.rows.forEach(row => {
        console.log(`├── ${row.indexname}: ${row.indexdef}`);
        console.log(`    大小：${row.index_size}`);
      });
    }
    
    // 推荐新索引
    console.log('\n💡 建议:');
    console.log('- 为经常用于 WHERE 条件的列创建索引');
    console.log('- 为外键列创建索引（如果还没创建）');
    console.log('- 避免在低基数列上创建索引');
    
    return { existing: result.rows };
    
  } catch (err) {
    console.error(`❌ 分析失败：${err.message}`);
    throw err;
  }
}

/**
 * 批量查询性能测试
 */
async function benchmarkQuery(query, iterations = 10) {
  const results = [];
  
  for (let i = 0; i < iterations; i++) {
    const startTime = Date.now();
    await pool.query(query); // 执行一次，忽略结果
    const duration = Date.now() - startTime;
    results.push(duration);
  }
  
  const totalDuration = results.reduce((a, b) => a + b, 0);
  const avgDuration = totalDuration / iterations;
  const maxDuration = Math.max(...results);
  
  console.log(`\n📈 ${iterations} 次性能测试结果:`);
  console.log(`平均耗时：${avgDuration.toFixed(2)}ms`);
  console.log(`最大耗时：${maxDuration}ms`);
  console.log(`最小耗时：${Math.min(...results)}ms`);
  
  return { results, avg: avgDuration, max: maxDuration };
}

// CLI 使用示例
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    console.log(`
查询优化工具 v1.0

用法:
  node query_optimizer.js --analyze "SELECT * FROM users WHERE status='active'"
  node query_optimizer.js --index users
  node query_optimizer.js --benchmark "SELECT count(*) FROM orders"

选项:
  --analyze <sql>    分析查询性能并给出建议
  --index <table>    生成表的索引报告和推荐
  --benchmark <sql>  多次执行查询并测试性能
  --help             显示此帮助信息
    `);
    process.exit(0);
  }
}

main().catch(console.error);
