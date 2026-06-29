#!/usr/bin/env node

/**
 * 创建订单脚本
 * 用法: node create-order.js --priceToken="询价token" --receiverPhone="收件人电话"
 */

const { createOrder, formatPrice } = require('../index');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const os = require('os');

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
  
  if (!args.priceToken || !args.receiverPhone) {
    console.log(`
📦 创建订单

用法:
  node create-order.js --priceToken="询价token" --receiverPhone="收件人电话"

参数:
  --priceToken     询价接口返回的 token（必填）
  --receiverPhone  收件人手机号（必填）

示例:
  node create-order.js --priceToken="abc123xyz" --receiverPhone="13800138000"

注意:
  - priceToken 有时效性，请在询价后尽快创建订单
  - 如账户余额不足，将返回支付宝支付链接
`);
    process.exit(1);
  }
  
  try {
    const result = await createOrder({
      priceToken: args.priceToken,
      receiverPhone: args.receiverPhone
    });
    
    if (result) {
      console.log('📊 创建结果:');
      console.log(JSON.stringify(result, null, 2));
      
      if (result.data && result.data.order_code) {
        // 检查是否需要支付（余额不足）
        if (result.data.orderUrl) {
          const paymentUrl = result.data.orderUrl;
          const orderCode = result.data.order_code;
          
          // 检测是否为微信支付 URL
          const isWechatPay = paymentUrl.startsWith('weixin://');
          
          console.log('\n⚠️  账户余额不足，需要完成支付');
          console.log(`   订单编号: ${orderCode}`);
          
          if (isWechatPay) {
            // 微信支付：下载二维码图片到本地
            const qrcodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(paymentUrl)}`;
            
            console.log('\n💳 微信支付');
            console.log('   正在生成支付二维码...');
            
            try {
              // 下载二维码图片到本地临时目录
              const tempDir = os.tmpdir();
              const qrFileName = `wechat_pay_${orderCode}.png`;
              const qrFilePath = path.join(tempDir, qrFileName);
              
              const response = await axios.get(qrcodeUrl, { responseType: 'arraybuffer', timeout: 10000 });
              fs.writeFileSync(qrFilePath, response.data);
              
              console.log('   二维码已生成！');
              console.log(`   请使用微信扫码支付`);
              
              // 输出特殊标记，供 Agent 识别
              console.log('\n[PAYMENT_REQUIRED]');
              console.log('[WECHAT_PAY_QRCODE]');
              console.log(`ORDER_CODE=${orderCode}`);
              console.log(`PAYMENT_URL=${paymentUrl}`);
              console.log(`QRCODE_FILE=${qrFilePath}`);
              console.log(`QRCODE_URL=${qrcodeUrl}`);
            } catch (downloadErr) {
              console.error('   下载二维码失败:', downloadErr.message);
              console.log(`   请手动访问二维码链接: ${qrcodeUrl}`);
              
              console.log('\n[PAYMENT_REQUIRED]');
              console.log('[WECHAT_PAY_QRCODE]');
              console.log(`ORDER_CODE=${orderCode}`);
              console.log(`PAYMENT_URL=${paymentUrl}`);
              console.log(`QRCODE_URL=${qrcodeUrl}`);
            }
          } else {
            // 非微信支付（如支付宝）：直接输出链接
            console.log('\n💳 请点击以下链接完成支付：');
            console.log(`   支付链接: ${paymentUrl}`);
            
            // 输出特殊标记，供 Agent 识别
            console.log('\n[PAYMENT_REQUIRED]');
            console.log(`ORDER_CODE=${orderCode}`);
            console.log(`PAYMENT_URL=${paymentUrl}`);
          }
          
          console.log('\n   支付完成后，订单将自动生效');
        } else {
          console.log('\n✅ 订单创建成功!');
          console.log(`   订单编号: ${result.data.order_code}`);
          console.log('\n💡 提示: 使用订单编号可查询订单详情或跟踪跑男位置');
        }
      }
    }
  } catch (error) {
    console.error('执行失败:', error.message);
    process.exit(1);
  }
}

main();
