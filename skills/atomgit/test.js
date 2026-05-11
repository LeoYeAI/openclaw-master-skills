#!/usr/bin/env node

/**
 * AtomGit MCP Server 测试脚本
 * 
 * 使用方法:
 * ATOMGIT_TOKEN=your-token node test.js
 */

const { exec } = require('child_process');
const path = require('path');

const MCP_SERVER = path.join(__dirname, 'mcp-server.js');

// 测试用例
const tests = [
  {
    name: 'getCurrentUser',
    request: { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'getCurrentUser', arguments: {} } }
  },
  {
    name: 'listRepos',
    request: { jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: 'listRepos', arguments: { perPage: 5 } } }
  }
];

async function runTest(test) {
  return new Promise((resolve, reject) => {
    console.log(`\n🧪 Testing: ${test.name}`);
    
    const proc = exec(`node ${MCP_SERVER}`, (error, stdout, stderr) => {
      if (error) {
        reject(error);
        return;
      }
      console.log('Response:', stdout);
      resolve(stdout);
    });
    
    // 发送请求
    setTimeout(() => {
      proc.stdin.write(JSON.stringify(test.request) + '\n');
      setTimeout(() => {
        proc.kill();
      }, 1000);
    }, 500);
  });
}

async function main() {
  console.log('🚀 AtomGit MCP Server Test Suite\n');
  
  if (!process.env.ATOMGIT_TOKEN) {
    console.error('❌ ERROR: ATOMGIT_TOKEN environment variable is not set');
    console.error('Please run: export ATOMGIT_TOKEN=your-token');
    process.exit(1);
  }
  
  console.log('✅ Token is set\n');
  
  for (const test of tests) {
    try {
      await runTest(test);
      console.log(`✅ ${test.name} passed`);
    } catch (error) {
      console.error(`❌ ${test.name} failed:`, error.message);
    }
  }
  
  console.log('\n🎉 Test suite completed');
}

main().catch(console.error);
