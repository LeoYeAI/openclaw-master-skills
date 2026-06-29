#!/usr/bin/env node

/**
 * 订单询价脚本
 * 用法: node order-price.js --fromAddress="起始地址" --toAddress="目的地址" [--cityName="城市名"]
 */

const { orderPrice, formatPrice } = require('../index');

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
  
  if (!args.fromAddress || !args.toAddress) {
    console.log(`
🚚 订单询价

用法:
  node order-price.js --fromAddress="起始地址" --toAddress="目的地址" [--cityName="城市名"]

参数:
  --fromAddress  起始地址（必填，要求完整地址信息）
  --toAddress    目的地址（必填，要求完整地址信息）
  --cityName     城市名称（可选，默认郑州市，需要带"市"字）

示例:
  node order-price.js --fromAddress="郑州市金水区农业路经三路交叉口" --toAddress="郑州市二七区德化街100号"
  node order-price.js --fromAddress="北京市朝阳区三里屯" --toAddress="北京市海淀区中关村" --cityName="北京市"
`);
    process.exit(1);
  }
  
  try {
    const result = await orderPrice({
      fromAddress: args.fromAddress,
      toAddress: args.toAddress,
      cityName: args.cityName
    });
    
    if (result) {
      console.log('📊 询价结果:');
      console.log(JSON.stringify(result, null, 2));
      
      // 如果有价格信息，格式化显示
      if (result.data && result.data.priceInfo) {
        console.log('\n💰 价格摘要:');
        console.log(`   预估费用: ${formatPrice(result.data.priceInfo.totalPrice || 0)} 元`);
        if (result.data.priceToken) {
          console.log(`   priceToken: ${result.data.priceToken}`);
          console.log('\n💡 提示: 使用此 priceToken 创建订单');
        }
      }
    }
  } catch (error) {
    console.error('执行失败:', error.message);
    process.exit(1);
  }
}

main();
