const { Pool } = require('pg');

async function queryKaoqinForms() {
  const pool = new Pool({
    host: '192.168.1.136',
    port: 35438,
    user: 'postgres',
    database: 'roadflow',
    password: 'Hxkj510510'
  });

  try {
    // 查询与考勤相关的表单
    const query = `
      SELECT id, name, type 
      FROM rf_form 
      WHERE LOWER(name) LIKE '%考勤%' 
         OR LOWER(name) LIKE '%请假%' 
         OR LOWER(name) LIKE '%出勤%' 
         OR LOWER(name) LIKE '%人事%' 
         OR LOWER(name) LIKE '%工资%'
      ORDER BY LENGTH(name)-LENGTH(REPLACE(name,' ','')) ASC 
      LIMIT 10
    `;

    console.log('🔍 查询与考勤/人事相关的表单...\n');
    const result = await pool.query(query);

    if (result.rows && result.rows.length > 0) {
      console.log(`找到 ${result.rows.length} 条记录:\n`);
      for (let i = 0; i < result.rows.length; i++) {
        const row = result.rows[i];
        console.log(`${i + 1}. ID: ${row.id}`);
        console.log('   名称：' + row.name);
        console.log('   类型：' + row.type + '\n');
        
        // 显示该表单的完整内容
        const full = await pool.query("SELECT * FROM rf_form WHERE id = " + row.id);
        if (full.rows && full.rows.length > 0) {
          console.log('   完整内容:\n');
          const rec = full.rows[0];
          for (const key of Object.keys(rec)) {
            const val = rec[key];
            const display = typeof val === 'string' ? (val.substring(0, 100) + (val.length > 100 ? '...' : '')) : val;
            console.log(`   ${key}:`, display);
          }
          console.log('');
        }
      }

      // 获取最大 ID 用于生成新表单
      const maxIdResult = await pool.query("SELECT MAX(id)+1 as new_id FROM rf_form");
      if (maxIdResult.rows && maxIdResult.rows[0]) {
        console.log('\n🆕 新生成的表单 ID:', maxIdResult.rows[0].new_id);
      }

    } else {
      console.log('⚠️  未找到相关记录');
    }

  } catch (error) {
    console.error('\n❌ 错误:', error.message);
  } finally {
    await pool.end();
  }
}

queryKaoqinForms();
