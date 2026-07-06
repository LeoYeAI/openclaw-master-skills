#!/usr/bin/env node
/**
 * drpy源压缩脚本
 * 使用uglify-js压缩drpy源代码
 * 用法：node minify_drpy.js input.js [output.js]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 1) {
    console.log('用法: node minify_drpy.js <输入文件> [输出文件]');
    console.log('示例:');
    console.log('  node minify_drpy.js source.js');
    console.log('  node minify_drpy.js source.js source.min.js');
    process.exit(1);
  }
  
  const inputFile = args[0];
  const outputFile = args[1] || getMinifiedName(inputFile);
  
  if (!fs.existsSync(inputFile)) {
    console.error(`错误: 文件不存在 ${inputFile}`);
    process.exit(1);
  }
  
  console.log(`正在压缩: ${inputFile}`);
  
  try {
    // 检查是否安装了uglify-js
    try {
      execSync('uglifyjs --version', { stdio: 'pipe' });
    } catch (e) {
      console.error('错误: 请先安装 uglify-js');
      console.error('安装命令: npm install uglify-js -g');
      process.exit(1);
    }
    
    // 使用uglifyjs压缩
    const command = `uglifyjs "${inputFile}" -o "${outputFile}" --compress --mangle`;
    execSync(command, { stdio: 'inherit' });
    
    const inputSize = fs.statSync(inputFile).size;
    const outputSize = fs.statSync(outputFile).size;
    const ratio = ((1 - outputSize / inputSize) * 100).toFixed(2);
    
    console.log(`\n压缩完成:`);
    console.log(`  输入文件: ${inputFile} (${formatBytes(inputSize)})`);
    console.log(`  输出文件: ${outputFile} (${formatBytes(outputSize)})`);
    console.log(`  压缩率: ${ratio}%`);
    
  } catch (error) {
    console.error('压缩失败:', error.message);
    
    // 如果uglify失败，尝试简单的压缩
    console.log('尝试简单压缩...');
    simpleMinify(inputFile, outputFile);
  }
}

function getMinifiedName(filename) {
  const ext = path.extname(filename);
  const name = path.basename(filename, ext);
  const dir = path.dirname(filename);
  return path.join(dir, `${name}.min${ext}`);
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function simpleMinify(inputFile, outputFile) {
  try {
    let content = fs.readFileSync(inputFile, 'utf8');
    
    // 简单的压缩步骤
    let minified = content
      // 移除注释
      .replace(/\/\/.*$/gm, '')
      .replace(/\/\*[\s\S]*?\*\//g, '')
      // 移除多余的空格和换行
      .replace(/\s+/g, ' ')
      .replace(/\s*([{}();,+=&|])\s*/g, '$1')
      .trim();
    
    fs.writeFileSync(outputFile, minified, 'utf8');
    
    const inputSize = content.length;
    const outputSize = minified.length;
    const ratio = ((1 - outputSize / inputSize) * 100).toFixed(2);
    
    console.log(`简单压缩完成:`);
    console.log(`  输入大小: ${inputSize} 字符`);
    console.log(`  输出大小: ${outputSize} 字符`);
    console.log(`  压缩率: ${ratio}%`);
    
  } catch (error) {
    console.error('简单压缩也失败:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { minifyDrpy: main };