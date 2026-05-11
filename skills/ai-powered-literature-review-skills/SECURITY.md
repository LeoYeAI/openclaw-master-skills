# 安全声明与免责声明

## ⚠️ 重要提示

**在使用 Literature Reviewer Skill 之前，请仔细阅读以下安全声明。**

---

## 1. 依赖声明

### 必需的依赖

本 Skill **依赖以下外部组件**才能正常运行：

| 依赖项 | 类型 | 说明 | 用途 |
|--------|------|------|------|
| `browser` skill | MCP/Skill | 浏览器自动化 | 访问 CNKI、Web of Science 等数据库 |
| Playwright | 运行时库 | 浏览器控制 | 驱动浏览器执行检索操作 |
| `web_search` skill (可选) | MCP/Skill | 网页搜索 | 辅助获取文献信息 |
| `docx` skill (可选) | MCP/Skill | Word 文档生成 | 生成 .docx 格式综述 |

**注意**: 本 Skill 本身不包含浏览器自动化功能，必须配合 `browser` skill 使用。

---

## 2. 权限说明

### 运行时权限

使用本 Skill 时，AI 助手将需要以下权限：

#### 文件系统权限
- ✅ 读取/写入 `./sessions/` 目录（存放会话数据）
- ✅ 读取/写入 `./output/` 目录（存放输出文件）
- ✅ 读取 `./agents/`、`/references/`、`/scripts/` 目录

#### 网络权限
- ✅ 访问 `kns.cnki.net`（中国知网）
- ✅ 访问 `www.webofscience.com`（Web of Science）
- ✅ 访问 `www.sciencedirect.com`（ScienceDirect）
- ✅ 访问 `scholar.google.com`（Google Scholar）
- ✅ 访问 `pubmed.ncbi.nlm.nih.gov`（PubMed）

#### 浏览器权限
- ✅ 控制浏览器实例（导航、点击、填写表单）
- ✅ 读取浏览器页面内容（DOM 提取）
- ✅ 下载文件（PDF 文献）

---

## 3. 风险提示

### 3.1 浏览器自动化风险

⚠️ **浏览器会话共享**: 本 Skill 使用 `browser` skill 控制浏览器，将：
- 访问您本地浏览器中的 cookies 和登录状态
- 如果您已登录 CNKI/WOS 等机构账号，Skill 将以您的身份访问
- 可能看到您浏览器中的其他标签页（但不会主动访问）

**建议**: 
- 在专用浏览器配置文件或无痕模式下运行
- 避免在已登录银行、邮箱等敏感账户的浏览器中使用

### 3.2 数据隐私

⚠️ **本地数据处理**: 
- 所有检索的文献信息存储在本地 `./sessions/` 目录
- 不会上传文献数据到第三方服务器
- 但浏览器访问过程中，目标网站可能记录访问日志

### 3.3 网站服务条款

⚠️ **爬虫与速率限制**:
- 本 Skill 通过浏览器自动化访问学术数据库
- 可能触发目标网站的反爬虫机制（验证码、IP 限制）
- 请遵守各数据库的服务条款和合理使用政策
- 建议控制检索频率，避免批量下载过多文献

### 3.4 安装安全

⚠️ **关于"自然语言安装"**:
- README 中提供的自然语言安装提示仅供参考
- **建议手动安装**，不要让 AI 自动执行 `git clone` 命令
- 安装前请审查本仓库的代码内容

---

## 4. 安全使用建议

### 推荐方案：Docker 隔离运行

为了最大程度保障安全，建议在 Docker 容器中运行本 Skill：

```bash
# 使用提供的 Docker 配置
docker-compose up -d

# 在容器内运行 Skill
docker exec -it literature-reviewer bash
```

**Docker 优势**:
- ✅ 与主机系统隔离
- ✅ 独立的浏览器环境
- ✅ 限制的文件系统访问
- ✅ 网络隔离和监控

### 手动安装安全步骤

1. **审查代码**
   ```bash
   # 查看关键文件内容
   cat SKILL.md
   cat scripts/*.py
   cat agents/*.md
   ```

2. **在隔离目录安装**
   ```bash
   # 不要在主 skills 目录直接安装
   # 先在测试环境验证
   mkdir -p ~/test-skills
   cd ~/test-skills
   git clone https://github.com/stephenlzc/AI-Powered-Literature-Review-Skills.git
   ```

3. **限制权限**
   ```bash
   # 设置只读权限（除 sessions 和 output 目录外）
   chmod -R 755 literature-reviewer-skill/
   mkdir -p literature-reviewer-skill/sessions
   mkdir -p literature-reviewer-skill/output
   chmod 777 literature-reviewer-skill/sessions
   chmod 777 literature-reviewer-skill/output
   ```

---

## 5. 免责声明

### 5.1 法律声明

**本 Skill 仅供学术研究使用**。使用者需自行承担以下责任：

- 遵守目标数据库（CNKI、Web of Science 等）的服务条款
- 尊重文献版权，仅用于个人学习和研究
- 不将批量下载的文献用于商业目的或非法传播
- 合理控制访问频率，不对目标服务器造成负担

### 5.2 免责声明

**开发者不对以下情况负责**：

1. 因使用本 Skill 导致的账号封禁或 IP 限制
2. 因浏览器自动化触发的验证码或安全验证
3. 因违反目标网站服务条款导致的法律问题
4. 检索结果的不完整性或准确性问题
5. 因 Skill 使用导致的任何直接或间接损失

### 5.3 开源许可

本项目基于 MIT-0 许可证开源：
- ✅ 可自由使用、修改、分发
- ✅ 无需署名
- ❌ 无担保（AS IS）

完整许可证见 [LICENSE](./LICENSE) 文件。

---

## 6. 问题报告

如发现安全漏洞或可疑行为，请通过以下方式报告：

- 🐛 GitHub Issues: https://github.com/stephenlzc/AI-Powered-Literature-Review-Skills/issues
- 📧 邮件: [待添加]

---

**最后更新**: 2024-03-09  
**版本**: v3.1.0
