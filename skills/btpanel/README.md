# btpanel

宝塔面板(BT-Panel)运维监控技能，提供服务器资源监控、网站状态检查、服务状态检查、SSH安全审计、计划任务管理、日志读取等功能

## 版本要求

- **宝塔面板**: >= 9.0.0
- **Python**: >= 3.10

## 快速开始

1. 安装依赖:
   ```bash
   pip install requests pyyaml rich
   ```

2. 配置服务器:
   ```bash
   # 使用配置工具添加服务器
   python3 scripts/bt-config.py add --name prod-01 --host https://panel.example.com:8888 --token YOUR_TOKEN

   # 查看配置
   python3 scripts/bt-config.py list
   ```

   或手动编辑配置文件 `~/.openclaw/bt-skills.yaml`

3. 运行:
   ```bash
   # 查看帮助
   python3 scripts/monitor.py --help

   # 监控所有服务器
   python3 scripts/monitor.py
   ```

## 可用脚本

| 脚本 | 功能 |
|------|------|
| monitor.py | 系统资源监控 |
| sites.py | 网站状态检查 |
| services.py | 服务状态检查 |
| logs.py | 日志读取 |
| ssh.py | SSH状态和登录日志 |
| crontab.py | 计划任务检查 |
| bt-config.py | 配置管理工具 |

## 配置管理工具

```bash
# 初始化配置
python3 scripts/bt-config.py init

# 列出服务器
python3 scripts/bt-config.py list

# 添加服务器
python3 scripts/bt-config.py add -n prod-01 -H https://panel.example.com:8888 -t YOUR_TOKEN

# 更新服务器
python3 scripts/bt-config.py update prod-01 --disabled

# 删除服务器
python3 scripts/bt-config.py remove prod-01

# 设置阈值
python3 scripts/bt-config.py threshold --cpu 75 --memory 80

# 查看配置路径
python3 scripts/bt-config.py path
```

详细使用说明请参考 SKILL.md
