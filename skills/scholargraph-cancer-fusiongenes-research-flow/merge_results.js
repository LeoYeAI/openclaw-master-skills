/**
 * 多轮搜索结果合并去重脚本
 * 用法: node merge_results.js
 */

const fs = require('fs');
const path = require('path');

// 读取搜索结果文件
function loadResults(filename) {
  const filePath = path.join(__dirname, filename);
  if (fs.existsSync(filePath)) {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  }
  return [];
}

// 合并去重函数
function mergeAndDeduplicate(results1, results2) {
  const seen = new Map();
  const merged = [];
  
  // 合并两轮结果
  const allItems = [...(results1 || []), ...(results2 || [])];
  
  for (const item of allItems) {
    // 根据基因+融合类型作为唯一标识
    const key = `${item.gene || item.基因}-${item.fusion || item.融合类型}`;
    if (!seen.has(key)) {
      seen.set(key, true);
      merged.push(item);
    }
  }
  
  return merged;
}

// 主函数
function main() {
  const round1 = loadResults('round1.json');
  const round2 = loadResults('round2.json');
  
  console.log(`Round 1: ${round1.length} records`);
  console.log(`Round 2: ${round2.length} records`);
  
  const merged = mergeAndDeduplicate(round1, round2);
  
  console.log(`Merged: ${merged.length} unique records`);
  
  // 保存合并结果
  fs.writeFileSync(
    path.join(__dirname, 'merged_results.json'),
    JSON.stringify(merged, null, 2)
  );
  
  console.log('Saved to merged_results.json');
}

main();
