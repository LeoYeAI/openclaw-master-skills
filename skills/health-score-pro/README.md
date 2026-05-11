# Health Management Skill

> Data-driven health tracking based on consensus from 10 best-selling health books

## Features

✅ **Three-Dimensional Diet Scoring**
- Greger's Daily Dozen (How Not to Die)
- Li's 5×5×5 Framework (Eat to Beat Disease)
- Consensus checklist from 10 health books

✅ **Food Defense System Analysis**
- Angiogenesis (blood vessel formation)
- Regeneration (stem cell activation)
- Microbiome (gut health)
- DNA Protection (epigenetics)
- Immunity (immune system support)

✅ **Multi-Language Support**
- Automatic language detection from user profile
- Supports Chinese (zh-CN), English (en), and more
- All outputs in user's preferred language

✅ **Timezone-Aware**
- User-configured timezone
- Correct date/time handling for all records

✅ **Automated Backup**
- GitHub repository backup
- Automatic backup after data changes
- Manual backup on request

## Security & Permissions

This skill follows the [ClawHub Security Framework](https://github.com/openclaw/openclaw/issues/10890).

### Declared Permissions

See [manifest.json](./manifest.json) for full permission declaration.

**Summary**:
- **Tools**: exec, read, write, web_search, web_fetch
- **Paths**: User health data directory, skill directory, backup directory
- **Scripts**: 6 shell scripts for backup, language, and timezone utilities
- **Network**: Tavily API for nutritional research
- **Capabilities**: filesystem, network

### Security Guarantees

✅ **Data Privacy**
- All data stored locally in `memory/health-users/{username}/`
- Each user's data isolated
- No cross-user access

✅ **No Exfiltration**
- Scripts only write to local files and user's own GitHub repo
- No third-party servers
- No telemetry

✅ **Transparency**
- All scripts are readable Bash code
- No obfuscation
- No binary executables

✅ **Least Privilege**
- Only requests necessary permissions
- No access to sensitive system paths
- Limited filesystem scope

For detailed permissions, see [PERMISSIONS.md](./PERMISSIONS.md).

## Installation

```bash
# Install via ClawHub
openclaw skills install health-management

# Or install from local
openclaw skills install /path/to/health-management
```

## Setup

### 1. Configure User Profile

The skill will guide you through first-time setup:

1. **Language Selection**: Choose your preferred language
2. **Timezone**: Set your timezone for accurate date/time handling
3. **GitHub Backup** (Optional): Configure automatic backup to your repository

### 2. API Keys (Optional)

For nutritional research features, configure Tavily API:

```bash
openclaw config set skills.tavily-search.apiKey YOUR_API_KEY
```

## Usage

### Record Diet

```
今天吃了：
- 早餐：燕麦粥、蓝莓、核桃
- 午餐：三文鱼、西兰花、糙米
- 晚餐：豆腐、菠菜、红薯
```

### View Analysis

```
分析一下这周的健康得分
```

### Backup Data

```
备份数据到GitHub
```

## Data Storage

All user data stored in:

```
~/.openclaw/workspace/memory/health-users/{username}/
├── profile.md          # User profile (language, timezone)
├── database.json       # Diet records and scores
├── reports/            # Weekly/monthly/yearly reports
│   ├── weekly/
│   ├── monthly/
│   └── yearly/
└── backup_config.json  # GitHub backup settings
```

## Development

### File Structure

```
health-management/
├── SKILL.md              # Main skill instructions
├── manifest.json         # Permission manifest
├── PERMISSIONS.md        # Permissions documentation
├── README.md             # This file
├── scripts/              # Shell scripts
│   ├── backup_health_data.sh
│   ├── check_git_config.sh
│   ├── configure_backup.sh
│   ├── manage_backup.sh
│   ├── language_utils.sh
│   └── timezone_utils.sh
├── references/           # Reference materials
├── assets/              # Static assets
└── templates/           # Report templates
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Update documentation
5. Submit pull request

## License

MIT

## Author

**longerian**
- GitHub: [@longerian](https://github.com/longerian)
- ClawHub: [clawhub.ai/longerian](https://clawhub.ai/longerian)

## Support

- **Issues**: [GitHub Issues](https://github.com/longerian/health-management/issues)
- **Discord**: [OpenClaw Community](https://discord.gg/clawd)

## Changelog

### v1.0.0 (2026-03-15)

- Initial release
- Three-dimensional diet scoring
- Food defense system analysis
- Multi-language support
- Timezone handling
- GitHub backup integration
- Permission manifest for ClawHub security framework

---

**Security First**: This skill is designed with security and privacy as top priorities. All permissions are declared, all scripts are auditable, and user data stays local.
