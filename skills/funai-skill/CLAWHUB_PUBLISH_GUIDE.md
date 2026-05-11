# Funai-skill 发布与更新指南（ClawHub）

这份文档用于指导你把当前 skill 发布到 ClawHub，并在之后持续维护更新。

适用目录：`/Users/lvke/Desktop/Funai-skill`

当前已确认信息：

- Skill 主文件：`/Users/lvke/Desktop/Funai-skill/SKILL.md`
- 当前版本文件：`/Users/lvke/Desktop/Funai-skill/VERSION`
- 当前版本号：`1.0.6`
- 建议长期固定使用的 slug：`funai-skill`

重要原则：

1. 第一次发布成功后，后续更新必须继续使用同一个 `slug`。
2. 每次更新都要递增版本号，不能重复发布同一个版本。
3. 推荐把 `VERSION` 文件作为你本地的唯一版本来源。
4. 首次发布建议使用 `publish`，后续维护可以继续用 `publish`，也可以使用 `sync`。

---

## 1. 你这次发布前要确认什么

在当前 skill 目录中，至少要有：

- `SKILL.md`
- `VERSION`

你当前目录已经具备：

- `agents/`
- `config/`
- `examples/`
- `references/`
- `scripts/`
- `SKILL.md`
- `VERSION`

这说明你的 skill 目录结构已经满足基本发布条件。

---

## 2. 安装 ClawHub CLI

任选一种方式安装：

```bash
npm i -g clawhub
```

或者：

```bash
pnpm add -g clawhub
```

安装完成后，建议先确认命令可用：

```bash
clawhub --cli-version
```

如果能输出版本号，说明 CLI 已安装成功。

---

## 3. 登录 ClawHub

执行：

```bash
clawhub login
```

它通常会拉起浏览器登录。

登录完成后，建议再执行一次：

```bash
clawhub whoami
```

如果能看到当前账号信息，说明你已经登录成功，可以发布 skill。

---

## 4. 第一次发布：直接可执行命令

你这次首次发布，直接使用下面这条命令：

```bash
clawhub publish "/Users/lvke/Desktop/Funai-skill" --slug funai-skill --name "Funai-skill" --version 1.0.6 --changelog "Initial release" --tags latest
```

参数含义：

- `publish "/Users/lvke/Desktop/Funai-skill"`：发布这个目录里的 skill。
- `--slug funai-skill`：这个 skill 的唯一标识。以后更新时必须保持不变。
- `--name "Funai-skill"`：展示名称。
- `--version 1.0.6`：本次发布版本号。当前来自你的 `VERSION` 文件。
- `--changelog "Initial release"`：本次发布说明。
- `--tags latest`：把这个版本标为默认最新版本。

如果这是你第一次发到 ClawHub，建议不要改 `slug`，就固定使用 `funai-skill`。

---

## 5. 如何判断这次是否发布成功

发布命令执行后，通常会返回成功信息。

建议你再做这几步检查：

### 方法 A：在网页上检查

打开：

- `https://clawhub.ai/`
- 或 `https://clawhub.com/`

搜索：

- `funai-skill`

如果能看到这个 skill，说明已经发布到注册中心。

### 方法 B：用 CLI 搜索

```bash
clawhub search "funai-skill"
```

### 方法 C：尝试安装到其他目录验证

你可以在一个临时目录验证安装是否正常：

```bash
mkdir -p /tmp/clawhub-skill-test
clawhub install funai-skill --workdir /tmp/clawhub-skill-test
```

如果能成功安装，说明外部用户已经可以获取你的 skill。

---

## 6. 以后怎么发布更新

以后每次更新 skill，都按这个流程执行。

### 第一步：修改 skill 内容

比如你改了：

- `SKILL.md`
- `examples/`
- `scripts/`
- `references/`
- `config/`

只要这些内容属于这个 skill 包的一部分，就可以重新发布新版本。

### 第二步：更新 `VERSION`

你当前版本是：

```text
1.0.6
```

下一次如果只是小修复，建议改成：

```text
1.0.7
```

如果是新增能力但兼容旧用法，建议改成：

```text
1.1.0
```

如果是重大改动或不兼容调整，建议改成：

```text
2.0.0
```

推荐语义化版本规则：

- `patch`：小修复，例如 `1.0.6 -> 1.0.7`
- `minor`：新增功能，例如 `1.0.6 -> 1.1.0`
- `major`：破坏性变更，例如 `1.0.6 -> 2.0.0`

### 第三步：重新发布

假设你把版本更新成 `1.0.7`，则执行：

```bash
clawhub publish "/Users/lvke/Desktop/Funai-skill" --slug funai-skill --name "Funai-skill" --version 1.0.7 --changelog "Refine skill instructions and update resources" --tags latest
```

以后无论发布多少次，都继续：

- 使用同一个目录
- 使用同一个 `slug`
- 使用递增后的新版本号

不要复用旧版本号。

---

## 7. 推荐你长期采用的更新流程

每次更新都按下面顺序走，最稳妥：

1. 修改 skill 内容。
2. 打开 `VERSION`，把版本号加一。
3. 准备一条简短的更新说明。
4. 执行 `clawhub publish`。
5. 用 `clawhub search` 或网页检查新版本是否可见。

一个完整示例：

```bash
clawhub whoami
clawhub publish "/Users/lvke/Desktop/Funai-skill" --slug funai-skill --name "Funai-skill" --version 1.0.7 --changelog "Improve prompts and workflow guidance" --tags latest
clawhub search "funai-skill"
```

---

## 8. 如果你想更省事：使用 sync

如果你后面会频繁维护更新，也可以用 `sync`。

先预览：

```bash
clawhub sync --root "/Users/lvke/Desktop/Funai-skill" --dry-run
```

确认没问题后执行：

```bash
clawhub sync --root "/Users/lvke/Desktop/Funai-skill" --all --bump patch --changelog "Routine update"
```

说明：

- `--root`：指定扫描这个 skill 根目录。
- `--all`：直接处理扫描到的内容。
- `--bump patch`：自动递增补丁版本。
- `--changelog`：填写本次更新说明。

什么时候适合 `sync`：

- 你后面会反复更新。
- 你可能会维护多个 skills。
- 你希望减少手工输入版本命令。

什么时候适合继续用 `publish`：

- 你想完全手动控制版本号。
- 你希望每次发版都非常明确。
- 你目前只维护一个 skill。

对于你现在的情况，建议：

- 第一次发布：用 `publish`
- 后续更新：仍可继续用 `publish`，等你熟悉后再考虑换 `sync`

---

## 9. 常见错误与解决方式

### 错误 1：版本号已经存在

表现：发布时报错，提示这个版本已经发布过。

原因：你重复使用了旧版本号。

解决：

1. 打开 `VERSION`
2. 把版本号增加，例如从 `1.0.6` 改为 `1.0.7`
3. 重新执行发布命令

### 错误 2：换了 slug，导致像是新 skill

表现：你以为是在更新，结果平台上出现了一个新的 skill 条目。

原因：`slug` 变了。

解决：

- 一旦第一次发布成功，之后必须始终使用 `funai-skill`

### 错误 3：没有登录

表现：发布时报认证错误。

解决：

```bash
clawhub login
clawhub whoami
```

### 错误 4：目录写错

表现：发布失败，或者提示找不到 skill 文件。

解决：确认路径就是：

```bash
/Users/lvke/Desktop/Funai-skill
```

### 错误 5：缺少 `SKILL.md`

表现：CLI 无法识别成有效 skill。

解决：确保根目录下存在：

```bash
/Users/lvke/Desktop/Funai-skill/SKILL.md
```

### 错误 6：更新后搜索不到最新结果

表现：刚发布完，网页或搜索里暂时看不到。

解决：

- 稍等片刻后再刷新
- 再执行一次 `clawhub search "funai-skill"`
- 确认这次发布是否确实返回成功

---

## 10. 推荐你固定保存的命令模板

### 首次发布模板

```bash
clawhub login
clawhub publish "/Users/lvke/Desktop/Funai-skill" --slug funai-skill --name "Funai-skill" --version 1.0.6 --changelog "Initial release" --tags latest
```

### 日常更新模板

把版本号和 changelog 改掉即可：

```bash
clawhub publish "/Users/lvke/Desktop/Funai-skill" --slug funai-skill --name "Funai-skill" --version 1.0.7 --changelog "Update skill instructions and resources" --tags latest
```

### 搜索模板

```bash
clawhub search "funai-skill"
```

### 查看登录状态模板

```bash
clawhub whoami
```

---

## 11. 我对你的最终建议

为了确保你这次能顺利发到 ClawHub，并且之后能稳定维护，建议你就按下面做：

### 这次

1. 安装 CLI
2. `clawhub login`
3. 执行首次发布命令
4. 用搜索或网页确认 skill 已可见

### 以后每次更新

1. 改 skill 内容
2. 增加 `VERSION`
3. 写一句 `changelog`
4. 再次执行 `clawhub publish`

只要你一直保持：

- 路径不变
- `slug` 不变
- 版本号递增

你就可以长期维护这个 skill。

---

## 12. 建议的下一步

如果你现在准备立即发布，就直接执行：

```bash
clawhub login
clawhub publish "/Users/lvke/Desktop/Funai-skill" --slug funai-skill --name "Funai-skill" --version 1.0.6 --changelog "Initial release" --tags latest
```

如果这次发布成功，下一步建议你额外做两件事：

1. 给这个 skill 建一个 git 仓库，用于跟踪每次改动。
2. 以后每次更新前先修改 `VERSION`，避免忘记发新版。
