# 自动审查配置指南

本指南说明如何配置和启动自动审查功能。

---
## 📦 第一步:配置审查仓库

编辑 `config/repos.conf` 文件,每行一个仓库（格式: `owner/repo`):

示例：
```
cann/runtime
cann/compiler
cann/driver
cann/tools
cann/samples
```

<details>
<summary>配置示例（点击展开）
</details>

<details>
<summary>环境变量方式</summary>

也可以环境变量配置（需要审查的仓库：
```bash
export CANN_REVIEW_REPOS="cann/runtime,cann/compiler,cann/driver"
```
```

**注意**： 多个仓库用逗号分隔，不要有空格。
</details>
