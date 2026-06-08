# 微信公众号 IP 白名单配置指南

## 什么是 IP 白名单？

微信公众号为了安全，要求所有调用 API 的服务器 IP 必须在白名单中。如果 IP 不在白名单，API 调用会失败。

## 为什么需要配置？

当你使用 `wechat-md-publisher` 发布文章时，工具会从你的电脑/服务器向微信 API 发送请求。微信会检查请求来源的 IP 地址，只有在白名单中的 IP 才能成功调用。

## 如何获取你的 IP 地址？

### 方法 1：使用命令行（推荐）

```bash
# macOS/Linux
curl ifconfig.me

# 或
curl icanhazip.com

# 或
curl ipinfo.io/ip
```

### 方法 2：访问网站

访问以下任一网站查看你的公网 IP：
- https://www.ip.cn/
- https://ipinfo.io/
- https://ifconfig.me/

### 方法 3：在微信公众平台查看

登录微信公众平台后，在 IP 白名单设置页面，微信会显示你当前的 IP 地址。

## 如何配置 IP 白名单？

### 步骤 1：登录微信公众平台

访问 https://mp.weixin.qq.com/ 并登录

### 步骤 2：进入 IP 白名单设置

1. 点击左侧菜单「设置与开发」
2. 点击「基本配置」
3. 找到「IP白名单」部分
4. 点击「修改」或「查看」

### 步骤 3：添加 IP 地址

1. 点击「添加」按钮
2. 输入你的公网 IP 地址
3. 点击「确定」

**示例**：
```
123.456.789.012
```

### 步骤 4：验证配置

添加后，等待 1-2 分钟生效，然后测试：

```bash
wechat-pub account list
```

如果能正常显示账号列表，说明配置成功。

## 常见场景

### 场景 1：在家里使用

**问题**：家庭宽带的 IP 地址可能会变化

**解决方案**：
1. **短期方案**：每次 IP 变化后重新添加
2. **长期方案**：
   - 联系运营商申请固定 IP（可能需要付费）
   - 使用云服务器部署（推荐）

### 场景 2：在公司使用

**问题**：公司可能使用固定 IP 或代理

**解决方案**：
1. 询问 IT 部门获取公司的公网出口 IP
2. 将公司 IP 添加到白名单
3. 如果公司使用代理，需要添加代理服务器的 IP

### 场景 3：在云服务器使用

**推荐方案**：
1. 购买云服务器（阿里云、腾讯云、AWS 等）
2. 云服务器通常有固定的公网 IP
3. 将云服务器 IP 添加到白名单
4. 在云服务器上安装和使用 `wechat-md-publisher`

**优点**：
- ✅ IP 固定，不会变化
- ✅ 24/7 在线
- ✅ 可以设置定时任务自动发布
- ✅ 网络稳定

### 场景 4：使用 VPN 或代理

**问题**：VPN 会改变你的出口 IP

**解决方案**：
1. 关闭 VPN 后获取真实 IP
2. 将真实 IP 添加到白名单
3. 使用工具时关闭 VPN

或者：
1. 获取 VPN 的出口 IP
2. 将 VPN IP 添加到白名单
3. 使用工具时保持 VPN 连接

## 多 IP 配置

微信公众号支持添加多个 IP 地址（通常最多 10-20 个）。

**适用场景**：
- 在多个地点使用（家里、公司、咖啡厅）
- 团队协作（多人使用）
- 备用 IP（防止主 IP 失效）

**配置方法**：
在 IP 白名单页面，点击「添加」，逐个添加所有需要的 IP。

## 安全建议

### ✅ 推荐做法

1. **只添加必要的 IP**
   - 不要添加不信任的 IP
   - 定期检查和清理不再使用的 IP

2. **使用固定 IP**
   - 云服务器（推荐）
   - 固定宽带 IP

3. **定期更新**
   - IP 变化后及时更新白名单
   - 删除不再使用的 IP

### ❌ 不推荐做法

1. **不要使用公共 WiFi**
   - 公共 WiFi 的 IP 可能被多人共享
   - 存在安全风险

2. **不要添加 0.0.0.0 或通配符**
   - 微信不支持通配符
   - 必须添加具体的 IP 地址

3. **不要分享你的 AppSecret**
   - 即使 IP 在白名单中，也要保护好 AppSecret
   - 不要将 AppSecret 提交到 Git 仓库

## 故障排查

### 错误：IP 不在白名单

**症状**：
```
错误码: 40164
错误信息: invalid ip xxx.xxx.xxx.xxx, not in whitelist
```

**解决步骤**：

1. **确认当前 IP**：
   ```bash
   curl ifconfig.me
   ```

2. **检查白名单**：
   - 登录微信公众平台
   - 查看 IP 白名单列表
   - 确认当前 IP 是否在列表中

3. **添加 IP**：
   - 如果不在，添加当前 IP
   - 等待 1-2 分钟生效

4. **重试**：
   ```bash
   wechat-pub account list
   ```

### 错误：IP 频繁变化

**症状**：今天能用，明天就不能用了

**原因**：家庭宽带 IP 动态分配

**解决方案**：

**方案 1：使用云服务器（推荐）**
```bash
# 1. 购买云服务器（最低配置即可）
# 2. 在云服务器上安装工具
ssh user@your-server-ip
npm install -g wechat-md-publisher

# 3. 配置账号
wechat-pub account add --name "公众号" --app-id xxx --app-secret xxx

# 4. 使用
wechat-pub publish create --file article.md --theme default
```

**方案 2：申请固定 IP**
- 联系宽带运营商
- 申请固定公网 IP（可能需要额外费用）

**方案 3：使用 DDNS**
- 配置动态 DNS
- 使用脚本自动更新白名单（需要开发）

## 自动化脚本

### 检查 IP 是否变化

```bash
#!/bin/bash
# check-ip.sh

CURRENT_IP=$(curl -s ifconfig.me)
SAVED_IP=$(cat ~/.wechat-pub-ip 2>/dev/null)

if [ "$CURRENT_IP" != "$SAVED_IP" ]; then
    echo "⚠️  IP 已变化！"
    echo "旧 IP: $SAVED_IP"
    echo "新 IP: $CURRENT_IP"
    echo "请更新微信公众平台的 IP 白名单"
    echo "$CURRENT_IP" > ~/.wechat-pub-ip
else
    echo "✓ IP 未变化: $CURRENT_IP"
fi
```

使用：
```bash
chmod +x check-ip.sh
./check-ip.sh
```

## 推荐配置

### 个人用户

**推荐方案**：使用云服务器
- 成本：约 10-30 元/月
- 优点：IP 固定、稳定可靠
- 推荐服务商：阿里云、腾讯云、华为云

### 企业用户

**推荐方案**：公司服务器 + 固定 IP
- 在公司内网服务器部署
- 配置公司出口 IP 到白名单
- 设置定时任务自动发布

### 团队协作

**推荐方案**：共享云服务器
- 团队共用一台云服务器
- 所有成员通过 SSH 访问
- 统一的 IP 地址

## 总结

1. ✅ **必须配置 IP 白名单**才能使用微信公众号 API
2. ✅ 使用 `curl ifconfig.me` 获取当前 IP
3. ✅ 在微信公众平台添加 IP 到白名单
4. ✅ 推荐使用云服务器获得固定 IP
5. ✅ 定期检查和更新 IP 白名单

## 相关链接

- [微信公众平台](https://mp.weixin.qq.com/)
- [微信公众号开发文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Getting_Started_Guide.html)
- [IP 白名单说明](https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html)

---

如有问题，请查看 [SKILL.md](../SKILL.md) 或提交 [Issue](https://github.com/sipingme/wechat-md-publisher/issues)。
