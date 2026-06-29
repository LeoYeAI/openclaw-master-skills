#!/usr/bin/env node

/**
 * 取消订单脚本
 * 用法: node cancel-order.js --orderCode="订单编号" [--reason="取消原因"]
 */

const { cancelOrder } = require('../index');

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
❌ 取消订单

用法:
  node cancel-order.js --orderCode="订单编号" [--reason="取消原因"]

参数:
  --orderCode  订单编号（必填）
  --reason     取消原因（可选）

示例:
  node cancel-order.js --orderCode="UU123456789"
  node cancel-order.js --orderCode="UU123456789" --reason="用户改变主意"

注意:
  - 已接单的订单可能会收取取消费用
  - 已完成的订单无法取消
`);
    process.exit(1);
  }
  
  try {
    const result = await cancelOrder({
      orderCode: args.orderCode,
      reason: args.reason
    });
    
    if (result) {
      console.log('📊 取消结果:');
      console.log(JSON.stringify(result, null, 2));
      
      if (result.code === 0 || result.code === '0') {
        console.log('\n✅ 订单已取消');
        console.log(`   订单编号: ${args.orderCode}`);
        if (args.reason) {
          console.log(`   取消原因: ${args.reason}`);
        }
      }
    }
  } catch (error) {
    console.error('执行失败:', error.message);
    process.exit(1);
  }
}

main();
