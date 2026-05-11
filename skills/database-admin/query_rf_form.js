const { Pool } = require('pg');

async function queryRfForm() {
  const pool = new Pool({
    host: '192.168.1.136',
    port: 35438,
    user: 'postgres',
    database: 'roadflow',
    password: 'Hxkj510510'
  });

  try {
    // 查看列定义
    const colResult = await pool.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'rf_form' 
      ORDER BY ordinal_position
    `);

    console.log('📋 rf_form 表的列定义:');
    colResult.rows.forEach(row => {
      console.log(' -', row.column_name.padEnd(20), '|', row.data_type);
    });

    // 查看现有记录数
    const countResult = await pool.query("SELECT COUNT(*) as cnt FROM rf_form");
    console.log('\n📊 rf_form 表当前记录数:', countResult.rows[0].cnt);

    // 显示所有现有表单
    const forms = await pool.query(`
      SELECT id, name, createtime 
      FROM rf_form 
      ORDER BY createtime DESC 
      LIMIT 15
    `);

    if (forms.rows && forms.rows.length > 0) {
      console.log('\n📋 现有的表单记录:');
      forms.rows.forEach(row => {
        console.log('  ID:', row.id, '|', row.name);
      });
    } else {
      console.log('  ⚠️  rf_form 表暂无数据');
    }

    // 显示完整的一条记录示例
    const sample = await pool.query(`
      SELECT * FROM rf_form 
      ORDER BY createtime DESC 
      LIMIT 1
    `);

    if (sample.rows && sample.rows.length > 0) {
      console.log('\n📝 最近一条记录的完整内容:');
      console.table(sample.rows[0]);
    }

  } catch (error) {
    console.error('\n❌ 错误:', error.message);
  } finally {
    await pool.end();
  }
}

queryRfForm();
