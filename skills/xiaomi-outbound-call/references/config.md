# 阿里云晓蜜外呼机器人及对话分析配置指南

## 环境变量配置

在使用晓蜜外呼机器人及对话分析功能前，需要设置以下环境变量：

| 环境变量                                | 说明                    | 示例              |
| --------------------------------------- | ----------------------- | ----------------- |
| `ALIYUN_OUTBOUND_BOT_ACCESS_KEY_ID`     | 阿里云 AccessKey ID     | `asdasdasd`       |
| `ALIYUN_OUTBOUND_BOT_ACCESS_KEY_SECRET` | 阿里云 AccessKey Secret | `your-secret-key` |

## 获取 AccessKey

1. 登录 [阿里云控制台](https://www.aliyun.com/)
2. 进入 **AccessKey 管理** 页面
3. 创建或使用现有的 AccessKey
4. **注意**：AccessKey Secret 只在创建时显示一次，请妥善保存

## 设置环境变量

### Linux/macOS

```bash
export ALIYUN_OUTBOUND_BOT_ACCESS_KEY_ID="your-access-key-id"
export ALIYUN_OUTBOUND_BOT_ACCESS_KEY_SECRET="your-access-key-secret"
```

### Windows (PowerShell)

```powershell
$env:ALIYUN_OUTBOUND_BOT_ACCESS_KEY_ID="your-access-key-id"
$env:ALIYUN_OUTBOUND_BOT_ACCESS_KEY_SECRET="your-access-key-secret"
```

### 永久配置（推荐）

将上述 export 命令添加到 `~/.bashrc` 或 `~/.zshrc` 文件中。
