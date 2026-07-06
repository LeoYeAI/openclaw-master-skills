#!/usr/bin/env node
/**
 * drpy源验证脚本
 * 验证drpy源的基本格式和必需属性
 */

const fs = require('fs');
const path = require('path');

function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 1) {
    console.log('用法: node validate_drpy.js <drpy源文件>');
    console.log('示例:');
    console.log('  node validate_drpy.js ./my-source.js');
    process.exit(1);
  }
  
  const inputFile = args[0];
  
  if (!fs.existsSync(inputFile)) {
    console.error(`错误: 文件不存在 ${inputFile}`);
    process.exit(1);
  }
  
  console.log(`验证文件: ${inputFile}`);
  
  try {
    const content = fs.readFileSync(inputFile, 'utf8');
    const result = validateDrpySource(content);
    
    printValidationResult(result);
    
    if (!result.isValid) {
      process.exit(1);
    }
    
  } catch (error) {
    console.error('验证失败:', error.message);
    process.exit(1);
  }
}

function validateDrpySource(content) {
  const result = {
    isValid: true,
    warnings: [],
    errors: [],
    properties: {},
    suggestions: []
  };
  
  // 检查基本结构
  if (!content.includes('var rule =')) {
    result.errors.push('缺少 "var rule =" 定义');
    result.isValid = false;
  }
  
  // 提取属性（简单正则匹配）
  const properties = extractProperties(content);
  result.properties = properties;
  
  // 检查必需属性
  const requiredProps = ['title', 'host'];
  for (const prop of requiredProps) {
    if (!properties[prop]) {
      result.errors.push(`缺少必需属性: ${prop}`);
      result.isValid = false;
    }
  }
  
  // 检查重要属性
  const importantProps = ['类型', 'url', 'searchUrl', 'class_name', 'class_url'];
  for (const prop of importantProps) {
    if (!properties[prop]) {
      result.warnings.push(`建议添加属性: ${prop}`);
    }
  }
  
  // 检查函数定义
  const requiredFunctions = ['推荐', '一级', '二级', '搜索'];
  for (const func of requiredFunctions) {
    if (!content.includes(`${func}:`)) {
      result.warnings.push(`建议定义函数: ${func}`);
    }
  }
  
  // 检查常见问题
  if (content.includes('fyclass') && !content.includes('class_name')) {
    result.warnings.push('使用了fyclass但未定义class_name和class_url');
  }
  
  if (content.includes('**') && !content.includes('searchUrl')) {
    result.warnings.push('使用了搜索占位符**但未定义searchUrl');
  }
  
  // 检查模板继承
  if (content.includes('Object.assign')) {
    result.properties.templateInheritance = 'Object.assign方式';
  } else if (content.includes('模板:')) {
    result.properties.templateInheritance = '模板属性方式';
  }
  
  // 分析可能的问题
  analyzePotentialIssues(content, result);
  
  return result;
}

function extractProperties(content) {
  const props = {};
  const lines = content.split('\n');
  
  // 简单提取属性（基于冒号分隔）
  for (const line of lines) {
    const trimmed = line.trim();
    
    // 跳过空行和注释
    if (!trimmed || trimmed.startsWith('//')) {
      continue;
    }
    
    // 匹配属性: 值
    const propMatch = trimmed.match(/^([\w\u4e00-\u9fa5]+)\s*:/);
    if (propMatch) {
      const propName = propMatch[1];
      
      // 提取值（简单版本）
      const valueMatch = trimmed.match(/:\s*(.+)$/);
      if (valueMatch) {
        let value = valueMatch[1].trim();
        
        // 清理尾随逗号
        if (value.endsWith(',')) {
          value = value.slice(0, -1);
        }
        
        // 清理字符串引号
        if (value.startsWith("'") && value.endsWith("'") ||
            value.startsWith('"') && value.endsWith('"')) {
          value = value.slice(1, -1);
        }
        
        props[propName] = value;
      }
    }
  }
  
  return props;
}

function analyzePotentialIssues(content, result) {
  // 检查URL模板
  if (result.properties.url) {
    const url = result.properties.url;
    
    if (!url.includes('fyclass') && !url.includes('fypage')) {
      result.warnings.push('url模板可能缺少fyclass或fypage占位符');
    }
  }
  
  if (result.properties.searchUrl) {
    const searchUrl = result.properties.searchUrl;
    
    if (!searchUrl.includes('**')) {
      result.warnings.push('searchUrl模板可能缺少**搜索词占位符');
    }
  }
  
  // 检查编码问题
  if (content.includes('gbk') || content.includes('GBK')) {
    if (!result.properties.编码 && !result.properties.搜索编码) {
      result.suggestions.push('检测到可能使用GBK编码的网站，建议设置编码或搜索编码属性');
    }
  }
  
  // 检查可能的反爬措施需要
  if (content.includes('403') || content.includes('反爬')) {
    result.suggestions.push('网站可能有反爬措施，建议设置合适的headers和Referer');
  }
  
  // 检查play_parse设置
  if (content.includes('play_parse')) {
    if (content.includes('play_parse: false') || content.includes('play_parse:0')) {
      result.warnings.push('play_parse设置为false可能影响播放解析');
    }
  }
}

function printValidationResult(result) {
  console.log('\n=== drpy源验证报告 ===\n');
  
  // 基本信息
  console.log('基本状态:');
  console.log(`  ✓ 格式${result.isValid ? '有效' : '无效'}`);
  
  if (result.properties.templateInheritance) {
    console.log(`  ✓ 模板继承: ${result.properties.templateInheritance}`);
  }
  
  console.log('\n属性检查:');
  Object.keys(result.properties).forEach(prop => {
    if (!['templateInheritance'].includes(prop)) {
      const value = result.properties[prop];
      console.log(`  ${prop}: ${value}`);
    }
  });
  
  // 错误
  if (result.errors.length > 0) {
    console.log('\n❌ 错误:');
    result.errors.forEach(error => {
      console.log(`  - ${error}`);
    });
  }
  
  // 警告
  if (result.warnings.length > 0) {
    console.log('\n⚠️ 警告:');
    result.warnings.forEach(warning => {
      console.log(`  - ${warning}`);
    });
  }
  
  // 建议
  if (result.suggestions.length > 0) {
    console.log('\n💡 建议:');
    result.suggestions.forEach(suggestion => {
      console.log(`  - ${suggestion}`);
    });
  }
  
  // 总结
  console.log('\n=== 验证总结 ===');
  if (result.isValid) {
    console.log('✅ 源文件基本格式正确');
    if (result.warnings.length === 0 && result.errors.length === 0) {
      console.log('🎉 未发现明显问题，可以尝试加载测试');
    } else {
      console.log('📝 请检查上面的警告和建议');
    }
  } else {
    console.log('❌ 源文件存在问题，需要修复');
  }
  
  // 下一步建议
  console.log('\n下一步:');
  if (!result.isValid) {
    console.log('1. 修复上述错误');
  }
  console.log('2. 在播放器中测试源功能');
  console.log('3. 检查分类、列表、详情、搜索功能是否正常');
  console.log('4. 测试播放功能');
}

if (require.main === module) {
  main();
}

module.exports = { validateDrpySource, validateDrpyFile: main };