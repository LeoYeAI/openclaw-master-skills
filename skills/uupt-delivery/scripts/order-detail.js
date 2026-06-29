#!/usr/bin/env node

/**
 * 查询订单详情脚本
 * 用法: node order-detail.js --orderCode="订单编号"
 */

const { orderDetail, formatPrice } = require('../index');

// 解析命令行参数
function parseArgs() {
  const args = {};
  process.argv.slice(2).forEach(arg => {
    const match = arg.match(/^--(\w+)=(.+)$/);
    if (match) {
      args[match[1]] = match[2].replace(/^["']|["']$/g, '');
    }
  });
  return args;
}

async function main() {
  const args = parseArgs();
  
  if (!args.orderCode) {
    console.log(`
📋 查询订单详情

用法:
  node order-detail.js --orderCode="订单编号"

参数:
  --orderCode  订单编号（必填）

示例:
  node order-detail.js --orderCode="UU123456789"
`);
    process.exit(1);
  }
  
  try {
    const result = await orderDetail({
      orderCode: args.orderCode
    });
    
    if (result) {
      console.log('📊 订单详情:');
      console.log(JSON.stringify(result, null, 2));
      
      if (result.data) {
        const data = result.data;
        console.log('\n📋 订单摘要:');
        console.log(`   订单编号: ${data.order_code || args.orderCode}`);
        console.log(`   订单状态: ${data.order_status || '-'}`);
        if (data.price) {
          console.log(`   配送费用: ${formatPrice(data.price)} 元`);
        }
        if (data.driver_name) {
          console.log(`   骑手姓名: ${data.driver_name}`);
          console.log(`   骑手电话: ${data.driver_phone || '-'}`);
        }
      }
    }
  } catch (error) {
    console.error('执行失败:', error.message);
    process.exit(1);
  }
}

main();
