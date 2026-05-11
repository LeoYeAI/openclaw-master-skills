# sls-trace-analysis

🔍 阿里云 SLS + ARMS 全链路问题排查 Skill

通过一个 trace_id，自动完成：查 SLS 日志 → 拉 ARMS 调用链 → 定位源码 → 排查数据库 → 输出修复方案。

## 功能

- **SLS 日志查询**：按 logstore 分组展示，逐条输出，不合并不去重
- **ARMS 调用链**：树状链路图 + 异常 Span + 方法级堆栈（GetStack）
- **代码排查**：自动搜索代码仓库，定位问题源码和触发条件
- **数据库排查**：SQL 异常、record not found、deadlock 等自动分析
- **交互式流程**：缺参数会问你，查不到数据会让你换时间重查

## 触发方式

```
分析sls
帮我查一下这个 trace_id xxxxxxxx
wusid 72553831
查一下 /path/to/api 这个接口的报错
线上有个接口挂了
SQL超时
```

## 三种查询模式

| 模式 | 说明 | 示例 |
|------|------|------|
| A: trace_id | 已知 trace_id，直接分析 | `trace_id 4d452e4d33cf...` |
| B: wusid/path | 不知道 trace_id，先检索 | `wusid 72553831` |
| C: 组合查询 | 多条件精确缩小范围 | `trace_id xxx; wusid 123` |

## 安装

```bash
# 1. 放到 OpenClaw skills 目录
cp -r sls-trace-analysis ~/.openclaw/workspace/skills/

# 2. 安装 Python 依赖
cd ~/.openclaw/workspace/skills/sls-trace-analysis/scripts
pip install -r requirements.txt

# 3. 配置阿里云 AK/SK（环境变量）
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-ak"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-sk"

# 4. 验证
openclaw skills list
```

## 依赖

- Python 3.8+
- aliyun-log-python-sdk==0.9.42
- alibabacloud-arms20190808==10.0.4
- 阿里云 SLS 和 ARMS 的 AccessKey

## 输出报告结构

1. 📋 问题定位报告（TraceID / 接口 / 时间 / 耗时）
2. 🗺️ ARMS 调用链路图
3. ❌ 异常 Span + 堆栈
4. 🔬 方法级堆栈详情
5. 📄 SLS 日志（按 logstore 分组）
6. 🔍 根因分析
7. 💻 代码排查（有异常时自动执行）
8. 🗄️ 数据库排查（涉及 DB 时自动执行）
9. 📝 综合结论 + 修复建议

## 许可证

MIT-0
