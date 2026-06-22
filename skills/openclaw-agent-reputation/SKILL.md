---
name: openclaw-agent-reputation
display_name: OpenClaw Agent Reputation
version: 0.1.0
author: ZhenStaff
category: blockchain
subcategory: reputation
license: MIT-0
description: On-chain credit scoring and soulbound identity for autonomous agents
tags: [blockchain, ai-agent, reputation, soulbound-token, credit-score, web3, base, ethereum, openclaw]
repository: https://github.com/ZhenRobotics/openclaw-agent-reputation
homepage: https://github.com/ZhenRobotics/openclaw-agent-reputation
documentation: https://github.com/ZhenRobotics/openclaw-agent-reputation/blob/main/README.md
---

# Agent Reputation

[中文](#中文说明) | [English](#english)

---

## 中文说明

### 📋 Skill 简介

**Agent Reputation** 是一个区块链智能体信用评分系统，为自主 AI Agent 提供链上信用评分和灵魂绑定身份（Soulbound Token）。

**Tagline**: 链上信用评分与灵魂绑定身份，为自主智能体构建信任基础

### 🎯 核心功能

1. **创建 Agent 身份** (`create_agent_identity`)
   - 为 AI Agent 铸造灵魂绑定代币（SBT）
   - 不可转让的永久链上身份
   - 绑定到控制者钱包地址

2. **查询 Agent 身份** (`query_identity`)
   - 通过地址或 Token ID 查询身份信息
   - 获取 Agent 名称、类型、创建时间等
   - 查看身份激活状态

3. **获取信用评分** (`get_credit_score`)
   - 查询 Agent 信用分（300-850 分，类似 FICO）
   - 查看详细评分维度指标
   - 获取历史评分趋势

4. **记录证明** (`record_attestation`)
   - 为 Agent 记录正面或负面证明
   - 社区驱动的信任验证
   - 直接影响信用评分

5. **对比 Agents** (`compare_agents`)
   - 同时对比多个 Agent 的信用分
   - 查看相对排名
   - 辅助选择决策

6. **生成报告** (`generate_report`)
   - 生成完整的信用评估报告
   - 支持文本、JSON、Markdown 格式
   - 包含所有评分维度详情

### 📊 信用评分算法

**评分范围**: 300-850 分（借鉴 FICO 信用评分体系）

**评分维度**（5 个加权指标）：

| 维度 | 权重 | 说明 |
|------|------|------|
| **任务成功率** | 30% | 完成任务数 / 总任务数 |
| **运行时长** | 20% | Agent 累计在线时间 |
| **安全性** | 20% | 安全事件数量（越少越好）|
| **社区证明** | 15% | 正面证明数 - 负面举报数 |
| **经济活动** | 15% | 交易量 + 质押金额 |

**评级标准**：
- 800-850: 优秀（Excellent）
- 740-799: 很好（Very Good）
- 670-739: 良好（Good）
- 580-669: 一般（Fair）
- 300-579: 较差（Poor）

### 🔧 使用场景

#### 1. AI Agent 市场
```
买家在购买前查看 Agent 信用分
高信用 Agent 可获得溢价
```

#### 2. 自主交易机器人
```
DeFi 协议根据信用分授权访问
高信用 Agent 享受低手续费
```

#### 3. Agent 协作网络
```
Agent 根据信用分选择合作伙伴
信用分影响收益分配比例
```

#### 4. 风险评估
```
保险公司根据信用分确定保费
质押平台调整质押要求
```

### 💡 使用示例

#### 示例 1：创建 Agent 身份

**用户输入**：
```
帮我为我的 GPT-4 Agent 创建一个链上身份，地址是 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

**Agent 响应**：
```
好的，我将为您的 GPT-4 Agent 创建灵魂绑定身份...

[调用 create_agent_identity]
参数：
- agent_address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
- name: GPT-4 Assistant
- agent_type: gpt-4
- network: baseSepolia

✅ Agent 身份创建成功！

📋 身份信息：
- Token ID: 42
- 名称: GPT-4 Assistant
- 类型: gpt-4
- 创建时间: 2026-03-12 14:30:00
- 控制者: 0x123...abc
- 状态: 已激活

这是一个永久的、不可转让的链上身份，所有行为都会被记录。
```

#### 示例 2：查询信用评分

**用户输入**：
```
查询 Token ID 为 42 的 Agent 信用分
```

**Agent 响应**：
```
正在查询 Agent #42 的信用评分...

[调用 get_credit_score]
参数：
- token_id: 42
- network: baseSepolia

📊 信用评分报告

总分: 745 / 850 (很好 - Very Good)

详细指标：
✅ 任务成功率: 95% (190/200 任务)
✅ 运行时长: 720 小时
✅ 安全事件: 0 次
✅ 社区证明: +25 条 / -2 条（净值 +23）
✅ 经济活动: 15.5 ETH 交易量 + 2 ETH 质押

评价：该 Agent 表现优秀，具有很高的可信度和可靠性。
建议可以安全地与其进行合作或交易。

最后更新: 2026-03-12 14:25:00
```

#### 示例 3：对比多个 Agents

**用户输入**：
```
帮我对比 Agent #42、#58 和 #91 的信用分，看看哪个更可靠
```

**Agent 响应**：
```
好的，正在对比这三个 Agent 的信用评分...

[调用 compare_agents]
参数：
- token_ids: [42, 58, 91]
- network: baseSepolia

📊 Agent 信用对比

排名 | Token ID | 信用分 | 评级 | 任务成功率 | 运行时长
-----|----------|--------|------|------------|----------
🥇 1 | #42 | 745 | 很好 | 95% | 720h
🥈 2 | #91 | 698 | 良好 | 88% | 450h
🥉 3 | #58 | 612 | 一般 | 76% | 280h

推荐: Agent #42 是最可靠的选择，各项指标均表现优秀。
```

### 🌐 技术规格

**区块链网络**: Base（Coinbase L2）
- 主网: Base Mainnet (Chain ID: 8453)
- 测试网: Base Sepolia (Chain ID: 84532)

**智能合约**:
- AgentSBT: 灵魂绑定代币（不可转让的 ERC-721）
- ReputationScore: 信用评分引擎
- BehaviorRegistry: 行为记录存储

**数据存储**:
- 链上: 身份信息、评分数据、行为记录
- 不可篡改: 所有数据永久保存
- 透明可验证: 任何人都可查询验证

### 🔐 安全说明

1. **灵魂绑定**: SBT 不可转让、不可售卖
2. **权限控制**: 只有控制者可以管理 Agent 身份
3. **数据永久**: 链上数据不可删除或修改
4. **隐私保护**: 未来支持零知识证明

### 📦 工具参数说明

#### 1. create_agent_identity

创建 Agent 身份（铸造 SBT）

**参数**：
- `agent_address` (必填): Agent 的以太坊地址
- `name` (必填): Agent 的名称
- `agent_type` (必填): Agent 类型（如 gpt-4, claude-3 等）
- `network` (可选): 网络选择，默认 baseSepolia

**返回**：Token ID 和交易哈希

#### 2. query_identity

查询 Agent 身份信息

**参数**：
- `identifier` (必填): Agent 地址（0x...）或 Token ID
- `network` (可选): 网络选择，默认 baseSepolia

**返回**：完整身份信息

#### 3. get_credit_score

获取信用评分和详细指标

**参数**：
- `token_id` (必填): Agent 的 Token ID
- `network` (可选): 网络选择，默认 baseSepolia

**返回**：信用分和所有评分维度数据

#### 4. record_attestation

记录证明（正面/负面）

**参数**：
- `token_id` (必填): Agent 的 Token ID
- `is_positive` (可选): true 为正面，false 为负面，默认 true
- `network` (可选): 网络选择，默认 baseSepolia

**返回**：交易哈希

#### 5. compare_agents

对比多个 Agents 的信用分

**参数**：
- `token_ids` (必填): Agent Token ID 数组
- `network` (可选): 网络选择，默认 baseSepolia

**返回**：对比结果表格

#### 6. generate_report

生成详细信用报告

**参数**：
- `token_id` (必填): Agent 的 Token ID
- `format` (可选): 格式 text/json/markdown，默认 text
- `network` (可选): 网络选择，默认 baseSepolia

**返回**：格式化的报告内容

### ⚙️ 环境要求

**必需的环境变量**:
- `PRIVATE_KEY` (必填): 以太坊钱包私钥（用于签署区块链交易）
  - ⚠️ 警告：请妥善保管私钥，切勿泄露
  - 建议使用测试网钱包私钥，不要使用主网真实资产钱包

**网络访问**:
- ✅ 连接到 Base 区块链网络（Mainnet 或 Sepolia Testnet）
- ✅ 所有交易上链，数据公开透明
- ✅ 不连接其他外部服务器

**前置条件**:
- Node.js >= 18.0.0
- 以太坊钱包地址和私钥
- 测试币（Base Sepolia）或主网 ETH

### 🚀 快速开始

1. **安装 Skill**
   ```bash
   clawhub install openclaw-agent-reputation
   ```

2. **配置环境变量**
   ```bash
   export PRIVATE_KEY="your_ethereum_private_key_here"
   ```

3. **准备测试 ETH**
   - 访问 Base Sepolia 水龙头获取测试币
   - 或使用主网 ETH（需要真实资产）

4. **开始使用**
   - 自然语言与 Agent 对话
   - Agent 会自动调用相关工具函数
   - 查看链上执行结果

### 📚 相关资源

- **npm 包**: `openclaw-agent-reputation`
- **GitHub**: https://github.com/ZhenRobotics/openclaw-agent-reputation
- **文档**: 完整的 API 文档和架构说明
- **智能合约**: 已开源在 GitHub

### 💰 成本说明

- **Gas 费用**: 根据 Base 网络实时 Gas 价格
- **创建身份**: 约 0.0001-0.0005 ETH
- **查询数据**: 免费（只读操作）
- **记录证明**: 约 0.00005-0.0002 ETH

### 🤝 支持

- **GitHub Issues**: 报告问题或建议
- **文档**: 查看详细使用指南
- **社区**: 加入 Discord 讨论

---

## English

### 📋 Skill Overview

**Agent Reputation** is a blockchain-based credit scoring system providing on-chain credit scores and soulbound identity (Soulbound Token) for autonomous AI Agents.

**Tagline**: On-chain credit scoring and soulbound identity for autonomous agents

### 🎯 Core Functions

1. **Create Agent Identity** (`create_agent_identity`)
   - Mint Soulbound Token (SBT) for AI Agents
   - Non-transferable permanent on-chain identity
   - Bound to controller wallet address

2. **Query Agent Identity** (`query_identity`)
   - Query identity by address or Token ID
   - Get Agent name, type, creation time, etc.
   - Check identity activation status

3. **Get Credit Score** (`get_credit_score`)
   - Query Agent credit score (300-850, similar to FICO)
   - View detailed scoring dimensions
   - Get historical scoring trends

4. **Record Attestation** (`record_attestation`)
   - Record positive or negative attestations for Agents
   - Community-driven trust verification
   - Directly impacts credit score

5. **Compare Agents** (`compare_agents`)
   - Compare multiple Agents' credit scores simultaneously
   - View relative rankings
   - Assist in selection decisions

6. **Generate Report** (`generate_report`)
   - Generate complete credit assessment report
   - Support text, JSON, Markdown formats
   - Include all scoring dimension details

### 📊 Credit Scoring Algorithm

**Score Range**: 300-850 (inspired by FICO credit scoring system)

**Scoring Dimensions** (5 weighted metrics):

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Task Success Rate** | 30% | Completed tasks / Total tasks |
| **Uptime** | 20% | Agent cumulative online time |
| **Security** | 20% | Number of security incidents (fewer is better) |
| **Community Attestations** | 15% | Positive attestations - Negative reports |
| **Economic Activity** | 15% | Transaction volume + Staking amount |

**Rating Standards**:
- 800-850: Excellent
- 740-799: Very Good
- 670-739: Good
- 580-669: Fair
- 300-579: Poor

### 🔧 Use Cases

#### 1. AI Agent Marketplace
```
Buyers check Agent credit score before purchase
High-credit Agents can get premium pricing
```

#### 2. Autonomous Trading Bots
```
DeFi protocols grant access based on credit score
High-credit Agents enjoy lower fees
```

#### 3. Agent Collaboration Network
```
Agents select partners based on credit scores
Credit score affects profit distribution ratio
```

#### 4. Risk Assessment
```
Insurance companies determine premiums based on credit score
Staking platforms adjust staking requirements
```

### 💡 Usage Examples

#### Example 1: Create Agent Identity

**User Input**:
```
Help me create an on-chain identity for my GPT-4 Agent at address 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

**Agent Response**:
```
I'll create a soulbound identity for your GPT-4 Agent...

[Call create_agent_identity]
Parameters:
- agent_address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
- name: GPT-4 Assistant
- agent_type: gpt-4
- network: baseSepolia

✅ Agent identity created successfully!

📋 Identity Information:
- Token ID: 42
- Name: GPT-4 Assistant
- Type: gpt-4
- Created: 2026-03-12 14:30:00
- Controller: 0x123...abc
- Status: Active

This is a permanent, non-transferable on-chain identity. All behaviors will be recorded.
```

#### Example 2: Query Credit Score

**User Input**:
```
Query the credit score for Agent Token ID 42
```

**Agent Response**:
```
Querying credit score for Agent #42...

[Call get_credit_score]
Parameters:
- token_id: 42
- network: baseSepolia

📊 Credit Score Report

Total Score: 745 / 850 (Very Good)

Detailed Metrics:
✅ Task Success Rate: 95% (190/200 tasks)
✅ Uptime: 720 hours
✅ Security Incidents: 0
✅ Community Attestations: +25 / -2 (Net +23)
✅ Economic Activity: 15.5 ETH volume + 2 ETH staked

Assessment: This Agent performs excellently with high trustworthiness and reliability.
Recommended for safe collaboration or transactions.

Last Updated: 2026-03-12 14:25:00
```

#### Example 3: Compare Multiple Agents

**User Input**:
```
Compare Agents #42, #58, and #91 to see which is more reliable
```

**Agent Response**:
```
Comparing credit scores for these three Agents...

[Call compare_agents]
Parameters:
- token_ids: [42, 58, 91]
- network: baseSepolia

📊 Agent Credit Comparison

Rank | Token ID | Score | Rating | Success Rate | Uptime
-----|----------|-------|--------|--------------|-------
🥇 1 | #42 | 745 | Very Good | 95% | 720h
🥈 2 | #91 | 698 | Good | 88% | 450h
🥉 3 | #58 | 612 | Fair | 76% | 280h

Recommendation: Agent #42 is the most reliable choice with excellent performance across all metrics.
```

### 🌐 Technical Specifications

**Blockchain Network**: Base (Coinbase L2)
- Mainnet: Base Mainnet (Chain ID: 8453)
- Testnet: Base Sepolia (Chain ID: 84532)

**Smart Contracts**:
- AgentSBT: Soulbound Token (non-transferable ERC-721)
- ReputationScore: Credit scoring engine
- BehaviorRegistry: Behavior record storage

**Data Storage**:
- On-chain: Identity info, scoring data, behavior records
- Immutable: All data permanently saved
- Transparent & Verifiable: Anyone can query and verify

### 🔐 Security Notes

1. **Soulbound**: SBT is non-transferable, non-sellable
2. **Access Control**: Only controller can manage Agent identity
3. **Data Permanence**: On-chain data cannot be deleted or modified
4. **Privacy Protection**: Future support for zero-knowledge proofs

### 📦 Tool Parameters

#### 1. create_agent_identity

Create Agent identity (mint SBT)

**Parameters**:
- `agent_address` (required): Agent's Ethereum address
- `name` (required): Agent's name
- `agent_type` (required): Agent type (e.g., gpt-4, claude-3)
- `network` (optional): Network choice, default baseSepolia

**Returns**: Token ID and transaction hash

#### 2. query_identity

Query Agent identity information

**Parameters**:
- `identifier` (required): Agent address (0x...) or Token ID
- `network` (optional): Network choice, default baseSepolia

**Returns**: Complete identity information

#### 3. get_credit_score

Get credit score and detailed metrics

**Parameters**:
- `token_id` (required): Agent's Token ID
- `network` (optional): Network choice, default baseSepolia

**Returns**: Credit score and all scoring dimension data

#### 4. record_attestation

Record attestation (positive/negative)

**Parameters**:
- `token_id` (required): Agent's Token ID
- `is_positive` (optional): true for positive, false for negative, default true
- `network` (optional): Network choice, default baseSepolia

**Returns**: Transaction hash

#### 5. compare_agents

Compare credit scores of multiple Agents

**Parameters**:
- `token_ids` (required): Array of Agent Token IDs
- `network` (optional): Network choice, default baseSepolia

**Returns**: Comparison result table

#### 6. generate_report

Generate detailed credit report

**Parameters**:
- `token_id` (required): Agent's Token ID
- `format` (optional): Format text/json/markdown, default text
- `network` (optional): Network choice, default baseSepolia

**Returns**: Formatted report content

### ⚙️ Environment Requirements

**Required Environment Variables**:
- `PRIVATE_KEY` (required): Ethereum wallet private key (for signing blockchain transactions)
  - ⚠️ Warning: Keep your private key secure, never expose it
  - Recommend using testnet wallet private key, not mainnet wallets with real assets

**Network Access**:
- ✅ Connects to Base blockchain network (Mainnet or Sepolia Testnet)
- ✅ All transactions on-chain, data publicly transparent
- ✅ No other external servers

**Prerequisites**:
- Node.js >= 18.0.0
- Ethereum wallet address and private key
- Test tokens (Base Sepolia) or mainnet ETH

### 🚀 Quick Start

1. **Install Skill**
   ```bash
   clawhub install openclaw-agent-reputation
   ```

2. **Configure Environment**
   ```bash
   export PRIVATE_KEY="your_ethereum_private_key_here"
   ```

3. **Get Test ETH**
   - Visit Base Sepolia faucet for test tokens
   - Or use mainnet ETH (requires real assets)

4. **Start Using**
   - Chat with Agent in natural language
   - Agent automatically calls relevant tool functions
   - View on-chain execution results

### 📚 Resources

- **npm Package**: `openclaw-agent-reputation`
- **GitHub**: https://github.com/ZhenRobotics/openclaw-agent-reputation
- **Documentation**: Complete API docs and architecture guide
- **Smart Contracts**: Open-sourced on GitHub

### 💰 Cost Information

- **Gas Fees**: Based on Base network real-time gas prices
- **Create Identity**: ~0.0001-0.0005 ETH
- **Query Data**: Free (read-only operations)
- **Record Attestation**: ~0.00005-0.0002 ETH

### 🤝 Support

- **GitHub Issues**: Report issues or suggestions
- **Documentation**: View detailed usage guides
- **Community**: Join Discord for discussions

---

**Version**: 0.1.0
**Last Updated**: 2026-03-12
