#!/usr/bin/env node

/**
 * 跑男实时追踪脚本
 * 用法: node driver-track.js --orderCode="订单编号"
 */

const { driverTrack } = require('../index');

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
🏃 跑男实时追踪

用法:
  node driver-track.js --orderCode="订单编号"

参数:
  --orderCode  订单编号（必填）

示例:
  node driver-track.js --orderCode="UU123456789"

说明:
  - 返回跑男的实时位置和状态信息
  - 需要订单已被接单才能查看跑男信息
`);
    process.exit(1);
  }
  
  try {
    const result = await driverTrack({
      orderCode: args.orderCode
    });
    
    if (result) {
      console.log('📊 跑男信息:');
      console.log(JSON.stringify(result, null, 2));
      
      if (result.data) {
        const data = result.data;
        console.log('\n🏃 跑男摘要:');
        if (data.driver_name) {
          console.log(`   骑手姓名: ${data.driver_name}`);
          console.log(`   联系电话: ${data.driver_phone || '-'}`);
        }
        if (data.longitude && data.latitude) {
          console.log(`   当前位置: ${data.longitude}, ${data.latitude}`);
        }
        if (data.distance) {
          console.log(`   距离目的地: ${data.distance} 米`);
        }
      }
    }
  } catch (error) {
    console.error('执行失败:', error.message);
    process.exit(1);
  }
}

main();
